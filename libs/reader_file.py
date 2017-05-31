from reader import BaseReader
import os
from pydub import AudioSegment
from pydub.utils import audioop
import numpy as np
from hashlib import sha1

class FileReader(BaseReader):
  def __init__(self, filename):
    # super(FileReader, self).__init__(a)
    self.filename = filename

  """
   Lee cualquier archivo soportado por pydub (ffmpeg) y devuelve los datos contenidos
   dentro.

   Puede limitarse opcionalmente a una cierta cantidad de segundos desde el principio
   del archivo especificando el parametro `limit`. Esta es la cantidad de
   segundos desde el inicio del archivo.
  """
  def parse_audio(self):
    limit = None
    # limit = 10

    songname, extension = os.path.splitext(os.path.basename(self.filename))

    try:
      audiofile = AudioSegment.from_file(self.filename)

      if limit:
        audiofile = audiofile[:limit * 1000]

      data = np.fromstring(audiofile._data, np.int16)

      channels = []
      for chn in xrange(audiofile.channels):
        channels.append(data[chn::audiofile.channels])

      fs = audiofile.frame_rate
    except audioop.error:
      print('audioop.error')
      pass
        # fs, _, audiofile = wavio.readwav(filename)

        # if limit:
        #     audiofile = audiofile[:limit * 1000]

        # audiofile = audiofile.T
        # audiofile = audiofile.astype(np.int16)

        # channels = []
        # for chn in audiofile:
        #     channels.append(chn)

    return {
      "songname": songname,
      "extension": extension,
      "channels": channels,
      "Fs": audiofile.frame_rate,
      "file_hash": self.parse_file_hash()
    }

  def parse_file_hash(self, blocksize=2**20):
    """ Funcion para generar un hash donde se genere de forma unica un archivo
    sacada de: http://stackoverflow.com/a/1131255/712997
    """
    s = sha1()

    with open(self.filename , "rb") as f:
      while True:
        buf = f.read(blocksize)
        if not buf: break
        s.update(buf)

    return s.hexdigest().upper()
