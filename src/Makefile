include ./.env.local

preprocess-tweets:
	spark-submit --conf "spark.mongodb.read.connection.uri=${SPARK_MONGODB_READ_URL}" \
              --conf "spark.mongodb.write.connection.uri=${SPARK_MONGODB_WRITE_URL}" \
              --packages org.mongodb.spark:mongo-spark-connector:10.0.5 \
              ./etl/spark_jobs/preprocess_tweets.py