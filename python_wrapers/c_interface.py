import  ctypes
import os
from numpy import ctypeslib as npct

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dll_path = os.path.join(base_dir, "c_libs/build", "lid_lda.dll")


if not os.path.exists(dll_path):
    raise FileNotFoundError(f"No se encuentra la DLL en: {dll_path}")

# Cargar la librería
lib = ctypes.CDLL(dll_path)


def matriz_topic_word(filename1,filename2):
    # Definir tipos de argumentos y valor de retorno
    word_in_topic = lib.word_in_topic
    word_in_topic.restype= ctypes.c_char_p
    word_in_topic.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    # llamamos a la funcion 
    resultado = word_in_topic(filename1.encode('utf-8'),filename2.encode('utf-8'))
    #la funcion modifica un txt no retorna nada es muy grande


def matriz_dic_topic(filename2,fiename3):
    #definimos argumentos en nuestro codigo 
    dic_in_topic= lib.dic_in_topic
    dic_in_topic.restype= ctypes.c_char_p
    dic_in_topic.argtypes = [ctypes.c_char_p, ctypes.c_char_p]

    resultado = dic_in_topic(filename2.encode('utf-8'),fiename3.encode('utf-8'))

# en dado caso que se nesesitan mas funciones se agregaran apartir de aca 