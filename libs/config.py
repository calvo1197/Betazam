import json
import os.path

CONFIG_DEFAULT_FILE = 'config.json'
CONFIG_DEVELOPMENT_FILE = 'config-development.json'

"""
Funcion que carga la configuracion de varios archivos y devuelve el resultado combinado
con la configuracion por defecto para la lectura de estos mismos.
"""
def get_config():
  defaultConfig = {"env": "unknown"}

  return merge_configs(
    defaultConfig,
    parse_config(CONFIG_DEFAULT_FILE),
    parse_config(CONFIG_DEVELOPMENT_FILE)
  )

# Funcion que retornara vacio si el archivo no es legible o no existe
def parse_config(filename):
  config = {}

  if os.path.isfile(filename):
    f = open(filename, 'r')
    config = json.load(f)
    f.close()

  return config

# Funcion que combina los archivos configurados
def merge_configs(*configs):
  z = {}

  for config in configs:
    z.update(config)

  return z
