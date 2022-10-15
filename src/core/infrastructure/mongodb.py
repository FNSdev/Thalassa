from pymongo import MongoClient

from core import settings

client = MongoClient(
    host=settings.MONGODB_HOST,
    port=settings.MONGODB_PORT,
    username=settings.MONGODB_USERNAME,
    password=settings.MONGODB_PASSWORD,
)
