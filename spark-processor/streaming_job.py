from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, window, avg, count, max as spark_max, min as spark_min,
    from_json, current_timestamp, when, lit
)
from pyspark.sql.types import (
    StructType, StructField, StringType, 
    IntegerType, DoubleType, TimestampType
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_spark_session():
    """Create Spark session with Kafka support"""
    return SparkSession.builder \
        .appName("WacoFlow-Traffic-Processor") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
        .config("spark.sql.streaming.checkpointLocation", "/tmp/spark-checkpoint") \
        .config("spark.sql.shuffle.partitions", "4") \
        .getOrCreate()

def create_intersection_stream(spark):
    """
    Read intersection data from Kafka
    This is the Flow Cube data
    """
    schema = StructType([
        StructField("source", StringType()),
        StructField("intersection_id", StringType()),
        StructField("timestamp", TimestampType()),
        StructField("signal_phase", StringType()),
        StructField("total_vehicles", IntegerType()),
        StructField("max_wait_time", IntegerType())
    ])
    
    # Read from Kafka
    kafka_df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "intersection-data") \
        .option("startingOffsets", "latest") \
        .load()
    
    # Parse JSON
    parsed_df = kafka_df \
        .select(from_json(col("value").cast("string"), schema).alias("data")) \
        .select("data.*")
    
    return parsed_df

def windowed_aggregations(intersection_stream):
    """
    5-minute rolling window aggregations
    KEY CISCO CONCEPT: Real-time analytics at scale
    """
    
    # Add watermark for late data (handles 10-minute delays)
    with_watermark = intersection_stream \
        .withWatermark("timestamp", "10 minutes")
    
    # 5-minute sliding window (updates every 1 minute)
    aggregated = with_watermark \
        .groupBy(
            col("intersection_id"),
            window(col("timestamp"), "5 minutes", "1 minute")
        ) \
        .agg(
            avg("total_vehicles").alias("avg_vehicles"),
            spark_max("total_vehicles").alias("peak_vehicles"),
            spark_min("total_vehicles").alias("min_vehicles"),
            avg("max_wait_time").alias("avg_wait_time"),
            spark_max("max_wait_time").alias("peak_wait_time"),
            count("*").alias("sample_count")
        )
    
    # Detect congestion (anomaly detection)
    with_congestion_flag = aggregated \
        .withColumn("is_congested", 
            when((col("avg_vehicles") > 40) | (col("avg_wait_time") > 60), lit(True))
            .otherwise(lit(False))
        ) \
        .withColumn("congestion_level",
            when(col("avg_vehicles") > 60, lit("SEVERE"))
            .when(col("avg_vehicles") > 40, lit("MODERATE"))
            .when(col("avg_vehicles") > 25, lit("LIGHT"))
            .otherwise(lit("CLEAR"))
        )
    
    return with_congestion_flag

def write_to_console(df, query_name):
    """Write stream to console for debugging"""
    return df \
        .writeStream \
        .outputMode("update") \
        .format("console") \
        .option("truncate", "false") \
        .queryName(query_name) \
        .trigger(processingTime="10 seconds") \
        .start()

def write_to_postgres(df, query_name):
    """
    Write to PostgreSQL/TimescaleDB
    In production, this stores historical data
    """
    def write_batch(batch_df, batch_id):
        batch_df.write \
            .format("jdbc") \
            .option("url", "jdbc:postgresql://localhost:5432/wacoflow") \
            .option("dbtable", "traffic_aggregates") \
            .option("user", "admin") \
            .option("password", "wacoflow2025") \
            .mode("append") \
            .save()
    
    return df \
        .writeStream \
        .foreachBatch(write_batch) \
        .queryName(query_name) \
        .trigger(processingTime="30 seconds") \
        .start()

def main():
    """Main Spark job"""
    logger.info("🚀 Starting WacoFlow Spark Streaming Job")
    
    # Create Spark session
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")
    
    # Create streaming DataFrame
    logger.info("📊 Creating intersection data stream...")
    intersection_stream = create_intersection_stream(spark)
    
    # Apply windowed aggregations
    logger.info("🔄 Setting up 5-minute rolling windows...")
    aggregated_stream = windowed_aggregations(intersection_stream)
    
    # Write to console (for demo/debugging)
    console_query = write_to_console(aggregated_stream, "traffic-aggregates-console")
    
    # Optionally write to PostgreSQL (uncomment for production)
    # postgres_query = write_to_postgres(aggregated_stream, "traffic-aggregates-postgres")
    
    logger.info("✅ Spark streaming job started successfully!")
    logger.info("📈 View Spark UI at: http://localhost:4040")
    logger.info("⏸️  Press Ctrl+C to stop")
    
    # Keep running
    console_query.awaitTermination()

if __name__ == "__main__":
    main()