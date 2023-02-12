from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import current_timestamp
from pyspark.sql.types import StructType, StringType, LongType, StructField


@dataclass
class ProcessedTweet:
    id: int
    created_at: datetime
    words: List[str]
    category: str
    location: Optional[str]
    username: Optional[str]


def word_count(row: ProcessedTweet) -> list[tuple[str, int]]:
    words = defaultdict(int)
    for word in row.words:
        words[word] += 1

    return [(word, count) for word, count in words.items()]


spark = SparkSession.builder.appName("thalassa").getOrCreate()

# TODO: process tweets for
#   a. current date (by default)
#   b. specific date (need to research how to pass it as an argument)
tweets_df: DataFrame = (
    spark.read.option("spark.mongodb.read.collection", "preprocessed_tweets")
    .format("mongodb")
    .load()
)

rdd = tweets_df.rdd.flatMap(f=word_count).reduceByKey(
    func=lambda count_1, count_2: count_1 + count_2
)
words_count_df: DataFrame = rdd.toDF(
    schema=StructType(
        fields=[
            StructField(name="word", dataType=StringType(), nullable=False),
            StructField(name="count", dataType=LongType(), nullable=False),
        ],
    ),
)
words_count_df = words_count_df.withColumn("saved_at", current_timestamp())

# TODO: what to use as an ID?
words_count_df.write.format("mongodb").mode("append").option("collection", "word_count").save()
