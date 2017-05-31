import pyaudio
import numpy
import wave
from reader import BaseReader

class MicrophoneReader(BaseReader):
  default_chunksize = 8192
  default_format = pyaudio.paInt16
  default_channels = 2
  default_rate = 44100
  default_seconds = 0

  # Funcion que inicializa los parametros por defecto del microfono 
  def __init__(self, a):
    super(MicrophoneReader, self).__init__(a)
    self.audio = pyaudio.PyAudio()
    self.stream = None
    self.data = []
    self.channels = MicrophoneReader.default_channels
    self.chunksize = MicrophoneReader.default_chunksize
    self.rate = MicrophoneReader.default_rate
    self.recorded = False

  # Funcion que inicia la grabacion con los parametros por defecto
  def start_recording(self, channels=default_channels,
                      rate=default_rate,
                      chunksize=default_chunksize,
                      seconds=default_seconds):
    self.chunksize = chunksize
    self.channels = channels
    self.recorded = False
    self.rate = rate

    if self.stream:
      self.stream.stop_stream()
      self.stream.close()

    self.stream = self.audio.open(
      format=self.default_format,
      channels=channels,
      rate=rate,
      input=True,
      frames_per_buffer=chunksize,
    )

    self.data = [[] for i in range(channels)]

  # Funcion que guarda todo el proceso de grabacion y sus datos
  def process_recording(self):
    data = self.stream.read(self.chunksize)
    nums = numpy.fromstring(data, numpy.int16)

    for c in range(self.channels):
      self.data[c].extend(nums[c::self.channels])

    return nums

  # Funcion que detiene la grabacion y actualiza el estado del programa (ya grabado)
  def stop_recording(self):
    self.stream.stop_stream()
    self.stream.close()
    self.stream = None
    self.recorded = True

  # Funcion que retorna los datos obtenidos de la grabacion
  def get_recorded_data(self):
    return self.data

  # Funcion que guarda los datos grabados como una onda de sonora en un fragmento de sonido
  def save_recorded(self, output_filename):
    wf = wave.open(output_filename, 'wb')
    wf.setnchannels(self.channels)
    wf.setsampwidth(self.audio.get_sample_size(self.default_format))
    wf.setframerate(self.rate)

    chunk_length = len(self.data[0]) / self.channels
    result = numpy.reshape(self.data[0], (chunk_length, self.channels))

    wf.writeframes(result)
    wf.close()

  def play(self):
    pass

  # Funcion que retorna el tiempo de grabacion
  def get_recorded_time(self):
    return len(self.data[0]) / self.rate
