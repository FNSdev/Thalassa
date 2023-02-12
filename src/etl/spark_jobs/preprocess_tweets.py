import re
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import current_timestamp
from pyspark.sql.types import (
    ArrayType,
    LongType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)

STOPWORDS = {
    "could",
    "he'll",
    "they'll",
    "for",
    "however",
    "own",
    "you",
    "but",
    "have",
    "i'll",
    "why",
    "you're",
    "herself",
    "she'd",
    "has",
    "i'd",
    "just",
    "get",
    "weren't",
    "didn't",
    "here",
    "so",
    "doesn't",
    "further",
    "above",
    "they're",
    "are",
    "had",
    "not",
    "shouldn't",
    "you'd",
    "she",
    "there's",
    "let's",
    "yours",
    "should",
    "hadn't",
    "isn't",
    "only",
    "he's",
    "when's",
    "wouldn't",
    "he'd",
    "did",
    "no",
    "any",
    "the",
    "since",
    "theirs",
    "would",
    "below",
    "other",
    "this",
    "it",
    "than",
    "where's",
    "yourself",
    "mustn't",
    "therefore",
    "in",
    "before",
    "into",
    "until",
    "these",
    "i've",
    "they've",
    "after",
    "how's",
    "else",
    "i",
    "we'd",
    "a",
    "we",
    "to",
    "you've",
    "most",
    "under",
    "am",
    "be",
    "don't",
    "from",
    "shan't",
    "with",
    "couldn't",
    "more",
    "that",
    "at",
    "what's",
    "aren't",
    "was",
    "can't",
    "itself",
    "then",
    "his",
    "doing",
    "like",
    "who",
    "an",
    "hasn't",
    "each",
    "is",
    "of",
    "also",
    "your",
    "himself",
    "their",
    "does",
    "myself",
    "some",
    "you'll",
    "me",
    "otherwise",
    "as",
    "how",
    "wasn't",
    "ours",
    "there",
    "shall",
    "themselves",
    "them",
    "her",
    "why's",
    "by",
    "and",
    "k",
    "too",
    "com",
    "i'm",
    "during",
    "http",
    "r",
    "can",
    "very",
    "whom",
    "off",
    "such",
    "between",
    "up",
    "she'll",
    "once",
    "our",
    "they'd",
    "it's",
    "hence",
    "what",
    "hers",
    "him",
    "were",
    "when",
    "my",
    "she's",
    "we've",
    "few",
    "having",
    "do",
    "because",
    "where",
    "or",
    "through",
    "over",
    "which",
    "he",
    "we're",
    "haven't",
    "all",
    "again",
    "while",
    "same",
    "ever",
    "here's",
    "won't",
    "about",
    "down",
    "being",
    "both",
    "yourselves",
    "been",
    "its",
    "ought",
    "www",
    "that's",
    "those",
    "against",
    "ourselves",
    "who's",
    "if",
    "we'll",
    "on",
    "they",
    "cannot",
    "nor",
    "out",
}


@dataclass
class Tweet:
    id: int
    created_at: datetime
    text: str
    category: str
    location: Optional[str]
    username: Optional[str]


@dataclass
class ProcessedTweet:
    id: int
    created_at: datetime
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
    text = text.encode("utf-16", "surrogatepass").decode("utf-16")
    words = [word for word in text.split(" ") if word]
    words = ["".join(c for c in word if c.isalnum()) for word in words]
    words = [word.lower() for word in words if word]
    words = [word for word in words if word not in STOPWORDS]

    return ProcessedTweet(
        id=row.id,
        created_at=row.created_at,
        words=words,
        category=row.category,
        location=row.location,
        username=row.username,
    )


spark = SparkSession.builder.appName("thalassa").getOrCreate()

tweets_df: DataFrame = (
    spark.read.option("spark.mongodb.read.collection", "tweets").format("mongodb").load()
)
users_df: DataFrame = (
    spark.read.option("spark.mongodb.read.collection", "twitter_users").format("mongodb").load()
)

tweets_df.createOrReplaceTempView("tweets")
users_df.createOrReplaceTempView("users")

# TODO: process tweets for
#   a. current date (by default)
#   b. specific date (need to research how to pass it as an argument)
tweets_with_authors_df = spark.sql(
    sqlQuery=(
        """
        SELECT 
            t._id as id,
            t.created_at,
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
            StructField(name="created_at", dataType=TimestampType(), nullable=False),
            StructField(
                name="words",
                dataType=ArrayType(elementType=StringType(), containsNull=False),
                nullable=False,
            ),
            StructField(name="category", dataType=StringType(), nullable=False),
            StructField(name="location", dataType=StringType(), nullable=True),
            StructField(name="username", dataType=StringType(), nullable=True),
        ],
    ),
)
preprocessed_tweets_df = preprocessed_tweets_df.withColumn("saved_at", current_timestamp())
preprocessed_tweets_df = preprocessed_tweets_df.withColumnRenamed(existing="id", new="_id")
(
    preprocessed_tweets_df.write.format("mongodb")
    .mode("append")
    .option("collection", "preprocessed_tweets")
    .save()
)
