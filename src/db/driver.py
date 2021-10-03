import os, pymongo
from dotenv import load_dotenv
from pymongo.database import Database

msg = '.env loaded' if load_dotenv() else 'Failed to load .env'
print(msg)

class DBdriver:
  client: Database

  def __init__(self) -> None:
    """
    A driver used to make writing and reading from the database
    easier.

    Raises:
        - `ConnectionError`
             - Raised if the driver failed to connect to MongoDB
    """
    client = pymongo.MongoClient(os.environ['MONGODB_URI'])

    try:
      # ping is cheap and doesn't require auth
      client.admin.command('ping')
      print('Connected to MongoDB')
    except pymongo.ConnectionFailure:
      raise ConnectionError('Failed to connect to MongoDB')
    
    # connect to the capstone database
    self.client = client.capstone