"""Script for processing kafka streams 
#############################################################
import pyspark and its configuration
"""
import logging
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.functions import sum as _sum
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType, FloatType, MapType
# Reference: https://denisecase.github.io/starting-spark
import os
from typing import List, Optional
import pyspark.sql.functions as F
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, year, month, dayofmonth, hour
import pyspark
import atexit
# from pyspark.sql.streaming import DataStreamReader


print(pyspark.__version__)


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# def rr() ->SparkSession: 
def create_or_get_spark():

    app_name = "KafkaElectionAnalysis"
    cluster_manager="spark://164.92.85.68:7077"
    packages = [ "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0",
                # "io.delta:delta-core_2.13:1.1.0","io.delta:delta-spark_2.12:3.5.0",
                    "org.apache.hadoop:hadoop-common:3.3.6",
                    "org.scala-lang:scala-library:2.13.0"
]
    

    
    """_summary_

    Args:
        app_name (str): Name of the spark application
        jars (str): List of jars needs to be installed before running spark application
        cluster_manager (str, optional): cluster manager Defaults to "local[*]".

    Returns:
        SparkSession: returns spark session
    """
    jars = ",".join(packages)
    # Initialize SparkSession
    spark = (SparkSession.builder
         .appName("TechKafkaElectionAnalysis")
         .master("spark://164.92.85.68:7077")
         .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.13:3.5.0")
         .getOrCreate())

    # print(spark)

#     logger.info("Kafka stream processing completed successfully.")
# except Exception as e:
#     logger.error(f"Error during Kafka stream processing: {str(e)}", exc_info=True)
# finally:
#     atexit.register(lambda: spark.stop() if spark else None)
#     # Stop the Spark session
#     # if "spark" in locals():
#     #     spark.stop()
    return spark 
# create_or_get_spark()



def define_read_Stream():
# Define schemas for Kafka topics
    """_summary_

        Args:
            spark (SparkSession): spark session
            broker_address (str): kafka broker address Ex: localhost:9092
            topic (str): topic from which events needs to consumed
            offset (str, optional): _description_. Defaults to "earliest".

        Returns:
            DataStreamReader: Interface used to load a streaming DataFrame from external storage systems

        Reference:
            https://spark.apache.org/docs/2.2.0/structured-streaming-kafka-integration.html
    """
    spark = create_or_get_spark()
    # print(stream)
    vote_schema = StructType([
            StructField("voter_id", StringType(), True),
            StructField("candidate_id", StringType(), True),
            StructField("voting_time", TimestampType(), True),
            StructField("voter_name", StringType(), True),
            StructField("party_affiliation", StringType(), True),
            StructField("biography", StringType(), True),
            StructField("campaign_platform", StringType(), True),
            StructField("photo_url", StringType(), True),
            StructField("candidate_name", StringType(), True),
            StructField("date_of_birth", StringType(), True),
            StructField("gender", StringType(), True),
            StructField("nationality", StringType(), True),
            StructField("registration_number", StringType(), True),
            StructField("address", StructType([
                StructField("street", StringType(), True),
                StructField("city", StringType(), True),
                StructField("state", StringType(), True),
                StructField("country", StringType(), True),
                StructField("postcode", StringType(), True)
            ]), True),
            StructField("email", StringType(), True),
            StructField("phone_number", StringType(), True),
            StructField("cell_number", StringType(), True),
            StructField("picture", StringType(), True),
            StructField("registered_age", IntegerType(), True),
            StructField("vote", IntegerType(), True)
        ])
    # print(vote_schema)

     # Read data from Kafka 'votes_topic' and process it
    KAFKA_BOOTSTRAP_SERVER = "164.92.85.68" + ":9092"
    print(KAFKA_BOOTSTRAP_SERVER)
    stream = (
        spark.readStream.format("kafka") \
        .option("kafka.bootstrap.servers", "164.92.85.68" + ":9092") \
        .option("subscribe", "voters_topic") \
        .option(
            "key.deserializer",
            "org.apache.kafka.common.serialization.StringDeserializer",
        )
        .option(
            "value.deserializer",
            "org.apache.kafka.common.serialization.StringDeserializer",
        )
        .option("failOnDataLoss", False)
        .load() \
        # .selectExpr("CAST(value AS STRING)") \
        # .select(from_json(col("value"), vote_schema).alias("data")) \
        # .select("data.*")
    )

    print(stream)
    #  # Data preprocessing: type casting and watermarking
    # votes_df = stream.withColumn("voting_time", col("voting_time").cast(TimestampType())) \
    #         .withColumn('vote', col('vote').cast(IntegerType()))
    # print(votes_df)
    # enriched_votes_df = votes_df.withWatermark("voting_time", "1 minute")
    # print(enriched_votes_df)
    # Aggregate votes per candidate and turnout by location
    # votes_per_candidate = enriched_votes_df.groupBy("candidate_id", "candidate_name", "party_affiliation",
    #                                                 "photo_url").agg(_sum("vote").alias("total_votes"))
    # print(votes_per_candidate)
    # turnout_by_location = enriched_votes_df.groupBy("address.state").count().alias("total_votes")
    # print(turnout_by_location)

    # # Write aggregated data to Kafka topics ('aggregated_votes_per_candidate', 'aggregated_turnout_by_location')
    # votes_per_candidate_to_kafka = votes_per_candidate.selectExpr("to_json(struct(*)) AS value") \
    #     .writeStream \
    #     .format("kafka") \
    #     .option("kafka.bootstrap.servers", "164.92.85.68" +":9092") \
    #     .option("topic", "aggregated_votes_per_candidate") \
    #     .option("checkpointLocation", "/Users/airscholar/Dev/Projects/Python/Voting/checkpoints/checkpoint1") \
    #     .outputMode("update") \
    #     .start()

    # turnout_by_location_to_kafka = turnout_by_location.selectExpr("to_json(struct(*)) AS value") \
    #     .writeStream \
    #     .format("kafka") \
    #     .option("kafka.bootstrap.servers", "164.92.85.68" + ":9092") \
    #     .option("topic", "aggregated_turnout_by_location") \
    #     .option("checkpointLocation", "/Users/airscholar/Dev/Projects/Python/Voting/checkpoints/checkpoint2") \
    #     .outputMode("update") \
    #     .start()

    # # Await termination for the streaming queries
    # votes_per_candidate_to_kafka.awaitTermination()
    # turnout_by_location_to_kafka.awaitTermination()
define_read_Stream()