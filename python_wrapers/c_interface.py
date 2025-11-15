import  ctypes
import os
from numpy import ctypeslib as npct
import numpy as np

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dll_path = os.path.join(base_dir, "c_libs/build", "lid_lda.dll")


if not os.path.exists(dll_path):
    raise FileNotFoundError(f"No se encuentra la DLL en: {dll_path}")

# Cargar la librería
lib = ctypes.CDLL(dll_path)


def matriz_topic_word(filename1,filename2,documentos,temas):
    # Definir tipos de argumentos y valor de retorno
    word_in_topic = lib.word_in_topic
    word_in_topic.restype= ctypes.POINTER(ctypes.POINTER(ctypes.c_float)) #obtener el puntero
    word_in_topic.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    # llamamos a la funcion 

    free_matrix = lib.free_matrix
    free_matrix.argtypes = [ctypes.POINTER(ctypes.POINTER(ctypes.c_float)), ctypes.c_int]

    resultado = word_in_topic(filename1.encode('utf-8'),filename2.encode('utf-8'))
     
    if not resultado:
        return None
    
    matriz = np.zeros((documentos, temas), dtype=np.float32)
    for i in range(documentos):
        for j in range(temas):
            matriz[i][j] = resultado[i][j]
    
    # Liberar memoria C
    
    return matriz, resultado


def matriz_dic_topic(filename2,fiename3,diccionario,temas):
    #definimos argumentos en nuestro codigo 
    dic_in_topic= lib.dic_in_topic
    dic_in_topic.restype= ctypes.POINTER(ctypes.POINTER(ctypes.c_float))

    free_matrix = lib.free_matrix
    free_matrix.argtypes = [ctypes.POINTER(ctypes.POINTER(ctypes.c_float)), ctypes.c_int]

    resultado = dic_in_topic(filename2.encode('utf-8'),fiename3.encode('utf-8'))

    if not resultado:
        return None
    
    matriz = np.zeros((diccionario,temas),dtype=np.float32)
    for i in range(diccionario):
        for j in range(temas):
            matriz[i][j]=resultado[i][j]




    free_matrix = lib.free_matrix
    free_matrix.argtypes = [ctypes.POINTER(ctypes.POINTER(ctypes.c_float)), ctypes.c_int]

    return matriz, resultado

# en dado caso que se nesesitan mas funciones se agregaran apartir de aca 


def calcular_matriz_final(m1,m2,n_repeticiones):

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    direccion_dicionario=os.path.join(base_dir, "txts/documento", "principito_lemas.txt")

    matriz_final=lib.matriz_final
    matriz_final.restype = ctypes.POINTER(ctypes.POINTER(ctypes.c_float))
    matriz_final.argtypes = [
        ctypes.POINTER(ctypes.POINTER(ctypes.c_float)),
        ctypes.POINTER(ctypes.POINTER(ctypes.c_float)),
        ctypes.c_int,
        ctypes.c_char_p
    ]

    resultado = matriz_final(
        m1,
        m2,
        n_repeticiones,
        direccion_dicionario.encode('utf-8')
    )
    if not resultado:
        # Liberar las matrices intermedias antes de retornar
        free_matrix = lib.free_matrix
        free_matrix.argtypes = [ctypes.POINTER(ctypes.POINTER(ctypes.c_float)), ctypes.c_int]
        free_matrix(m1, 13)
        free_matrix(m2, 1195)
        return None
    

    matriz = np.zeros((13, 50), dtype=np.float32)
    for i in range(13):
        for j in range(50):
            matriz[i][j] = resultado[i][j]


    
