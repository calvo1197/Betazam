from pymongo import MongoClient
from db import Database
from config import get_config

class MongoDatabase(Database):
  def __init__(self):
    pass

  # Funcion de conexion a la base de datos del programa
  def connect(self):
    config = get_config()

    self.client = MongoClient(config['db.dsn'])
    self.db = self.client[config['db.database']]

  # Funcion que inserta un nuevo archivo a la base de datos
  def insert(self, collection, document):
    # if not self.db:
    self.connect()

    return self.db[collection].insert_one(document).inserted_id
