import sys

""" 
Clase principal de la base de datos, la cual permite modificaciones directas
"""

class Database(object):
  TABLE_SONGS = None
  TABLE_FINGERPRINTS = None

  def __init__(self, a):
    self.a = a

  def connect(self): pass
  def insert(self, table, params): pass

  #Funcion que retorna un archivo de audio pedido por nombre a la base de datos
  def get_song_by_filehash(self, filehash):
    return self.findOne(self.TABLE_SONGS, {
      "filehash": filehash
    })

  #Funcion que retorna un archivo de audio pedido por id a la base de datos
  def get_song_by_id(self, id):
    return self.findOne(self.TABLE_SONGS, {
      "id": id
    })

  #Funcion que agrega una cancion a la base de datos
  def add_song(self, filename, filehash):
    song = self.get_song_by_filehash(filehash)

    if not song:
      song_id = self.insert(self.TABLE_SONGS, {
        "name": filename,
        "filehash": filehash
      })
    else:
      song_id = song[0]

    return song_id

  def get_song_hashes_count(self, song_id):
    pass

  #Funcion que agrega las huellas digitales de las canciones a la base de datos
  def store_fingerprints(self, values):
    self.insertMany(self.TABLE_FINGERPRINTS,
      ['song_fk', 'hash', 'offset'], values
    )
