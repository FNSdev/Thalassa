import re
from dataclasses import dataclass
from typing import List, Optional

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import current_timestamp
from pyspark.sql.types import ArrayType, LongType, StringType, StructField, StructType


@dataclass
class Tweet:
    id: int
    text: str
    category: str
    location: Optional[str]
    username: Optional[str]


@dataclass
class ProcessedTweet:
    id: int
    words: List[str]
    category: str
    location: Optional[str]
    username: Optional[str]


def clean_text(row: Tweet) -> ProcessedTweet:
    text = row.text
    text = text.strip()
    text = text.replace("\n", " ")
    text = re.sub(r"@\w+", "", text)
    text = re.sub(r"https://\S+", "", text)
    text = re.sub(r"&.+;", "", text)
    text = text.encode('utf-16', 'surrogatepass').decode("utf-16")
    words = [word for word in text.split(' ') if word]
    words = [''.join(c for c in word if c.isalnum()) for word in words]
    words = [word.lower() for word in words if word]

    return ProcessedTweet(
        id=row.id,
        words=words,
        category=row.category,
        location=row.location,
        username=row.username,
    )


spark = (
    SparkSession
    .builder
    .appName("thalassa")
    .getOrCreate()
)

tweets_df: DataFrame = (
    spark.read.option("spark.mongodb.read.collection", "tweets_1").format("mongodb").load()
)
users_df: DataFrame = (
    spark.read.option("spark.mongodb.read.collection", "twitter_users").format("mongodb").load()
)

tweets_df.createOrReplaceTempView("tweets")
users_df.createOrReplaceTempView("users")

tweets_with_authors_df = spark.sql(
    sqlQuery=(
        """
        SELECT 
            t._id as id,
            t.text,
            t.category,
            u.location,
            u.username
        FROM tweets t
        LEFT OUTER JOIN users u ON t.author_id = u._id
        """
    ),
)

rdd = tweets_with_authors_df.rdd.map(f=clean_text)

preprocessed_tweets_df: DataFrame = rdd.toDF(
    schema=StructType(
        fields=[
            StructField(name="id", dataType=LongType(), nullable=False),
            StructField(
                name="words",
                dataType=ArrayType(elementType=StringType(), containsNull=False),
                nullable=False,
            ),
            StructField(name="category", dataType=StringType(), nullable=False),
            StructField(name="location", dataType=StringType(), nullable=True),
            StructField(name="username", dataType=StringType(), nullable=True),
        ],
    )
)
preprocessed_tweets_df = preprocessed_tweets_df.withColumn("saved_at", current_timestamp())
preprocessed_tweets_df = preprocessed_tweets_df.withColumnRenamed(existing="id", new="_id")
(
    preprocessed_tweets_df.write
    .format("mongodb")
    .mode("append")
    .option("collection", "preprocessed_tweets")
    .save()
)
