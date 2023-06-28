from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import current_timestamp, lit, monotonically_increasing_id
from pyspark.sql.types import (
    BooleanType,
    IntegerType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)

spark = SparkSession.builder.appName("thalassa").getOrCreate()

schema = StructType(
    fields=[
        StructField(name="user_name", dataType=StringType(), nullable=False),
        StructField(name="user_location", dataType=StringType(), nullable=True),
        StructField(name="user_description", dataType=StringType(), nullable=True),
        StructField(name="user_created", dataType=TimestampType(), nullable=False),
        StructField(name="user_followers", dataType=IntegerType(), nullable=False),
        StructField(name="user_friends", dataType=IntegerType(), nullable=False),
        StructField(name="user_favourites", dataType=IntegerType(), nullable=False),
        StructField(name="user_verified", dataType=BooleanType(), nullable=False),
        StructField(name="date", dataType=TimestampType(), nullable=False),
        StructField(name="text", dataType=StringType(), nullable=False),
        StructField(name="hashtags", dataType=StringType(), nullable=True),
        StructField(name="source", dataType=StringType(), nullable=False),
        StructField(name="is_retweet", dataType=BooleanType(), nullable=False),
    ],
)

tweets_df: DataFrame = (
    spark.read.options(header=True, multiline=True, escape='"')
    .schema(schema=schema)
    .format(source="csv")
    .load(path="covid19_tweets.csv")
)

tweets_df = tweets_df.filter(tweets_df.is_retweet == False)
tweets_df = tweets_df.withColumn("saved_at", current_timestamp())
tweets_df = tweets_df.withColumn("_id", monotonically_increasing_id())

tweets_df = tweets_df.select("_id", "saved_at", "date", "user_name", "user_location", "text")
tweets_df = tweets_df.withColumnRenamed(existing="date", new="created_at")
tweets_df = tweets_df.withColumnRenamed(existing="user_name", new="username")
tweets_df = tweets_df.withColumnRenamed(existing="user_location", new="location")

tweets_df = tweets_df.withColumn("category", lit("covid"))

(tweets_df.write.format("mongodb").mode("append").option("collection", "tweets_from_csv").save())
