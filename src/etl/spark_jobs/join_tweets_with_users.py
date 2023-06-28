from pyspark.sql import DataFrame, SparkSession

spark = SparkSession.builder.appName("thalassa").getOrCreate()

tweets_df: DataFrame = (
    spark.read.option("spark.mongodb.read.collection", "tweets").format("mongodb").load()
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
            t._id,
            t.created_at,
            t.text,
            t.category,
            t.saved_at,
            u.location,
            u.username
        FROM tweets t
        LEFT OUTER JOIN users u ON t.author_id = u._id
        """
    ),
)

(
    tweets_with_authors_df.write.format("mongodb")
    .mode("append")
    .option("collection", "tweets_with_users")
    .save()
)
