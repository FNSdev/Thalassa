include ./.env.local

format:
	black .
	isort .

consume-tweets:
	PYTHONPATH=./ python etl/connectors/twitter.py

import-tweets-from-csv:
	spark-submit --conf "spark.mongodb.write.connection.uri=${SPARK_MONGODB_WRITE_URL}" \
              --packages org.mongodb.spark:mongo-spark-connector_2.12:10.1.1 \
              ./etl/spark_jobs/import_tweets_from_csv.py

join-tweets-with-users:
	spark-submit --conf "spark.mongodb.read.connection.uri=${SPARK_MONGODB_READ_URL}" \
              --conf "spark.mongodb.write.connection.uri=${SPARK_MONGODB_WRITE_URL}" \
              --packages org.mongodb.spark:mongo-spark-connector_2.12:10.1.1 \
              ./etl/spark_jobs/join_tweets_with_users.py

clean-tweets:
	spark-submit --conf "spark.mongodb.read.connection.uri=${SPARK_MONGODB_READ_URL}" \
              --conf "spark.mongodb.write.connection.uri=${SPARK_MONGODB_WRITE_URL}" \
              --packages org.mongodb.spark:mongo-spark-connector_2.12:10.1.1 \
              ./etl/spark_jobs/clean_tweets.py

count-words:
	spark-submit --conf "spark.mongodb.read.connection.uri=${SPARK_MONGODB_READ_URL}" \
              --conf "spark.mongodb.write.connection.uri=${SPARK_MONGODB_WRITE_URL}" \
              --packages org.mongodb.spark:mongo-spark-connector_2.12:10.1.1 \
              ./etl/spark_jobs/count_words.py
