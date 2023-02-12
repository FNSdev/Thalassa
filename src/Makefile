include ./.env.local

format:
	black .

consume-tweets:
	PYTHONPATH=./ python etl/connectors/twitter.py

preprocess-tweets:
	spark-submit --conf "spark.mongodb.read.connection.uri=${SPARK_MONGODB_READ_URL}" \
              --conf "spark.mongodb.write.connection.uri=${SPARK_MONGODB_WRITE_URL}" \
              --packages org.mongodb.spark:mongo-spark-connector_2.12:10.1.1 \
              ./etl/spark_jobs/preprocess_tweets.py

count-words:
	spark-submit --conf "spark.mongodb.read.connection.uri=${SPARK_MONGODB_READ_URL}" \
              --conf "spark.mongodb.write.connection.uri=${SPARK_MONGODB_WRITE_URL}" \
              --packages org.mongodb.spark:mongo-spark-connector_2.12:10.1.1 \
              ./etl/spark_jobs/count_words.py
