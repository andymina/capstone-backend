from dotenv import load_dotenv
import os
import pymongo

msg = '.env loaded' if load_dotenv() else 'Failed to load .env'
print(msg)

class DBdriver:
    client: pymongo.MongoClient = None

    def __init__(self) -> None:
        self.client = pymongo.MongoClient(os.environ['MONGODB_URI'])

        try:
            # The ping command is cheap and does not require auth.
            self.client.admin.command('ping')
            print('Connected to MongoDB')
        except pymongo.ConnectionFailure:
            print('Failed to connect to MongoDB')