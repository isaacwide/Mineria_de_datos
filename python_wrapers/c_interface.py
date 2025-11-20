import ctypes
import os
from numpy import ctypeslib as npct
import numpy as np

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dll_path = os.path.join(base_dir, "c_libs/build", "lid_lda.dll")

if not os.path.exists(dll_path):
    raise FileNotFoundError(f"No se encuentra la DLL en: {dll_path}")

# Cargar la librería
lib = ctypes.CDLL(dll_path)

def matriz_topic_word(filename1, filename2, documentos, temas):
    word_in_topic = lib.word_in_topic
    word_in_topic.restype = ctypes.POINTER(ctypes.POINTER(ctypes.c_float))
    word_in_topic.argtypes = [ctypes.c_char_p, ctypes.c_char_p]

    resultado = word_in_topic(filename1.encode('utf-8'), filename2.encode('utf-8'))
     
    if not resultado:
        return None, None
    
    matriz = np.zeros((documentos, temas), dtype=np.float32)
    for i in range(documentos):
        for j in range(temas):
            matriz[i][j] = resultado[i][j]
    
    return matriz, resultado


def matriz_dic_topic(filename1, filename3, diccionario, temas):
    dic_in_topic = lib.dic_in_topic
    dic_in_topic.restype = ctypes.POINTER(ctypes.POINTER(ctypes.c_float))
    dic_in_topic.argtypes = [ctypes.c_char_p, ctypes.c_char_p]

    resultado = dic_in_topic(filename1.encode('utf-8'), filename3.encode('utf-8'))

    if not resultado:
        return None, None
    
    matriz = np.zeros((temas, diccionario), dtype=np.float32)
    for i in range(temas):
        for j in range(diccionario):
            matriz[i][j] = resultado[i][j]

    return matriz, resultado


def calcular_matriz_final(m1, m2, n_repeticiones):
    """
    Calcula la matriz final iterada.
    NO libera m1 ni m2 porque se siguen usando.
    """
    direccion_documento = "txts/documento/principito_lemas.txt"

    matriz_final = lib.matriz_final
    matriz_final.restype = ctypes.POINTER(ctypes.POINTER(ctypes.c_float))
    matriz_final.argtypes = [
        ctypes.POINTER(ctypes.POINTER(ctypes.c_float)),
        ctypes.POINTER(ctypes.POINTER(ctypes.c_float)),
        ctypes.c_int,
        ctypes.c_char_p
    ]

    print(f"Calculando matriz final con {n_repeticiones} repeticiones...")
    
    resultado = matriz_final(
        m1,
        m2,
        n_repeticiones,
        direccion_documento.encode('utf-8')
    )
    
    if not resultado:
        print("Error: matriz_final retornó NULL")
        return None
    matriz = np.zeros((7, 50), dtype=np.float32)
    try:
        for i in range(7):
            for j in range(50):
                matriz[i][j] = resultado[i][j]
    except Exception as e:
        print(f"Error al copiar datos: {e}")
        return None

    return matriz


def liberar_matrices(m1, m2, filas_m1, filas_m2):
    """
    Función para liberar memoria cuando ya no se necesiten las matrices.
    Llamar solo al final, cuando no se vayan a usar más.
    """
    free_matrix = lib.free_matrix
    free_matrix.argtypes = [ctypes.POINTER(ctypes.POINTER(ctypes.c_float)), ctypes.c_int]
    
    if m1:
        free_matrix(m1, filas_m1)
    if m2:
        free_matrix(m2, filas_m2)
    
    print("Memoria liberada")


def param_sigma(mtx, filas=1063, columnas=50):
    parametro_sigma = lib.parametro_sigma
    parametro_sigma.restype = ctypes.POINTER(ctypes.POINTER(ctypes.c_float))
    parametro_sigma.argtypes = [ctypes.POINTER(ctypes.POINTER(ctypes.c_float))] 

    print(f"Llamando a parametro_sigma con matriz {filas}x{columnas}...")
    resultado_sigma = parametro_sigma(mtx)

    # Verificar correctamente el resultado
    if not resultado_sigma:
        print("Error: parametro_sigma retornó NULL")
        return None
    
    try:
        # Crear la matriz numpy
        matriz = np.zeros((filas, columnas), dtype=np.float32)
        
        # Copiar datos con manejo de errores
        for i in range(filas):
            if not resultado_sigma[i]:
                print(f"Error: fila {i} es NULL")
                return None
            for j in range(columnas):
                matriz[i][j] = resultado_sigma[i][j]
        
        print(f"Matriz sigma calculada exitosamente: {matriz.shape}")
        return resultado_sigma, matriz
        
    except Exception as e:
        print(f"Error al copiar datos de sigma: {e}")
        return None
