import hashlib
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

from termcolor import colored
from scipy.ndimage.filters import maximum_filter
from scipy.ndimage.morphology import (generate_binary_structure, iterate_structure, binary_erosion)
from operator import itemgetter

IDX_FREQ_I = 0
IDX_TIME_J = 1

# numero de pruebas por segundo
DEFAULT_FS = 44100

# Tamano de la ventana FFT, afecta la imagen de frecuencia
DEFAULT_WINDOW_SIZE = 4096

#Cada ventana secuencial se superpone a la ultima y la
#siguiente ventana. Una superposicion superior permitira una mayor granularidad del desplazamiento
#pero potencialmente mas huellas dactilares.
DEFAULT_OVERLAP_RATIO = 0.5

# Grado en el que una huella digital se puede emparejar con sus vecinos, a mayor grado
# causara mas huellas dactilares y potencialmente mejor precision.
DEFAULT_FAN_VALUE = 15

# Amplitud minima en el espectrograma para ser considerada un pico.
# esto puede aumentarse para reducir el numero de huellas dactilares, pero puede
# afectar la precision.
DEFAULT_AMP_MIN = 10

# Numero de celulas alrededor de un pico de amplitud en el espectrograma para
# valores mas altos significan menos
# huellas dactilares y una coincidencia mas rapida, pero puede afectar potencialmente la precision.
PEAK_NEIGHBORHOOD_SIZE = 20

# Umbrales sobre la proximidad o la distancia de las huellas digitales en el tiempo
# para ser emparejado como una huella digital. Si su maximo es demasiado bajo, los valores mas altos de
# DEFAULT_FAN_VALUE puede no funcionar como se esperaba.
MIN_HASH_TIME_DELTA = 0
MAX_HASH_TIME_DELTA = 200

# Si es Verdadero, clasificara los picos temporalmente para la huella dactilar;
# no clasificar reducira el numero de huellas dactilares, pero potencialmente
# afectar el rendimiento.
PEAK_SORT = True

# Numero de bits a tirar de la parte frontal del hash SHA1 en el
# calculo de la huella digital. Cuanto mas se tira, menos almacenamiento, pero
# potencialmente colisiones mas altas y clasificaciones erroneas al identificar canciones.
FINGERPRINT_REDUCTION = 20

def fingerprint(channel_samples, Fs=DEFAULT_FS,
                wsize=DEFAULT_WINDOW_SIZE,
                wratio=DEFAULT_OVERLAP_RATIO,
                fan_value=DEFAULT_FAN_VALUE,
                amp_min=DEFAULT_AMP_MIN,
                plots=False):

    # Asigna los puntos 
    if plots:
      plt.plot(channel_samples)
      plt.title('%d samples' % len(channel_samples))
      plt.xlabel('time (s)')
      plt.ylabel('amplitude (A)')
      plt.show()
      plt.gca().invert_yaxis()

    # FFT el canal, logra transformar la salida, encontrar maximos locales, luego retorna
    # hashes localmente sensibles.

    # Traza el espectro angular de los segmentos dentro de la senal en un colormap

    arr2D = mlab.specgram(
        channel_samples,
        NFFT=wsize,
        Fs=Fs,
        window=mlab.window_hanning,
        noverlap=int(wsize * wratio))[0]

    # Muestra el espectrograma
    if plots:
      plt.plot(arr2D)
      plt.title('FFT')
      plt.show()

    # Aplicar log transform desde specgram() devuelve matriz lineal
    arr2D = 10 * np.log10(arr2D) # calcula la base 10 para todos los elementos de arr2D
    arr2D[arr2D == -np.inf] = 0  # reemplaza infs con ceros

    # Encuentra el maximo local
    local_maxima = get_2D_peaks(arr2D, plot=plots, amp_min=amp_min)

    msg = '   local_maxima: %d of frequency & time pairs'
    #print colored(msg, attrs=['dark']) % len(local_maxima)

    # return hashes
    return generate_hashes(local_maxima, fan_value=fan_value)

#Funcion para obtener el maximo local, puntos maximos (picos de frecuencia) 
def get_2D_peaks(arr2D, plot=False, amp_min=DEFAULT_AMP_MIN):
    # http://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.morphology.iterate_structure.html#scipy.ndimage.morphology.iterate_structure
    struct = generate_binary_structure(2, 1)
    neighborhood = iterate_structure(struct, PEAK_NEIGHBORHOOD_SIZE)

    # Encuentra maximos locales usando el filtro shape
    local_max = maximum_filter(arr2D, footprint=neighborhood) == arr2D
    background = (arr2D == 0)
    eroded_background = binary_erosion(background, structure=neighborhood,
                                       border_value=1)

    # Booleano de arr2D con True en picos
    detected_peaks = local_max - eroded_background

    # Extrae los picos
    amps = arr2D[detected_peaks]
    j, i = np.where(detected_peaks)

    # Filtra los picos
    amps = amps.flatten()
    peaks = zip(i, j, amps)
    peaks_filtered = [x for x in peaks if x[2] > amp_min]  # freq, time, amp

    # Obtiene indices de frecuencia y tiempo
    frequency_idx = [x[1] for x in peaks_filtered]
    time_idx = [x[0] for x in peaks_filtered]

    # Dispersion de los picos
    if plot:
      fig, ax = plt.subplots()
      ax.imshow(arr2D)
      ax.scatter(time_idx, frequency_idx)
      ax.set_xlabel('Time')
      ax.set_ylabel('Frequency')
      ax.set_title("Spectrogram")
      plt.gca().invert_yaxis()
      plt.show()

    return zip(frequency_idx, time_idx)


#Genera los hashes y calcula la diferencia de tiempo del pico actual a los posibles siguientes
def generate_hashes(peaks, fan_value=DEFAULT_FAN_VALUE):
    if PEAK_SORT:
      peaks.sort(key=itemgetter(1))

    # forza todos los picos
    for i in range(len(peaks)):
      for j in range(1, fan_value):
        if (i + j) < len(peaks):

          # Tomar el valor actual y siguiente de la  frecuencia de los picos
          freq1 = peaks[i][IDX_FREQ_I]
          freq2 = peaks[i + j][IDX_FREQ_I]

          # Toma valor actual y siguiende del tiempo de los picos 
          t1 = peaks[i][IDX_TIME_J]
          t2 = peaks[i + j][IDX_TIME_J]

          # Obtiene la diferencia de tiempo
          t_delta = t2 - t1

          # Chequea si delta esta entre el min y max
          if t_delta >= MIN_HASH_TIME_DELTA and t_delta <= MAX_HASH_TIME_DELTA:
            h = hashlib.sha1("%s|%s|%s" % (str(freq1), str(freq2), str(t_delta)))
            yield (h.hexdigest()[0:FINGERPRINT_REDUCTION], t1)
