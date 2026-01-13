import numpy as np
from collections import defaultdict

def calcular_frecuencias_documento_palabra(filename, diccionario_path, num_documentos, tam_vocabulario):
    """
    Calcula la matriz de frecuencias n_{d,v} donde:
    n_{d,v} = número de veces que la palabra v aparece en el documento d
    
    Returns:
        np.ndarray: Matriz de forma (num_documentos, tam_vocabulario)
    """
    # Cargar diccionario
    with open(diccionario_path, 'r', encoding='utf-8') as f:
        diccionario = [line.strip() for line in f.readlines()]
    
    # Crear mapeo palabra -> índice
    palabra_a_indice = {palabra: idx for idx, palabra in enumerate(diccionario)}
    
    # Inicializar matriz de frecuencias
    n_dv = np.zeros((num_documentos, tam_vocabulario), dtype=np.float32)
    
    # Delimitadores de documentos
    delimitadores = set([f"DOCUMENT{i}" for i in range(1, 30)] + 
                        [f"document{i}" for i in range(1, 30)])
    
    # Leer archivo y contar frecuencias
    doc_actual = -1
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            palabra = line.strip()
            
            if palabra in delimitadores:
                doc_actual += 1
            elif doc_actual >= 0 and doc_actual < num_documentos and palabra in palabra_a_indice:
                palabra_idx = palabra_a_indice[palabra]
                n_dv[doc_actual][palabra_idx] += 1
    
    return n_dv


def calcular_entropia(theta, phi, n_dv):
    """
    Calcula la entropía del modelo LDA.
    
    Fórmula:
    log(entropía) = -∑_{d=1}^{D} [∑_{v=1}^{V} n_{d,v} * log(∑_{k=1}^{K} θ_{d,k} * φ_{k,v})] / ∑_{d=1}^{D} N_d
    
    Args:
        theta: Matriz documento-tópico (D x K) - matriz_1
        phi: Matriz palabra-tópico (K x V) - matriz_2 transpuesta
        n_dv: Matriz de frecuencias documento-palabra (D x V)
    
    Returns:
        float: Valor de entropía
    """
    D, K = theta.shape  # D = documentos, K = tópicos
    K, V = phi.shape    # V = vocabulario
    
    # Calcular N_d (total de palabras por documento)
    N_d = np.sum(n_dv, axis=1)  # Shape: (D,)
    total_palabras = np.sum(N_d)
    
    if total_palabras == 0:
        return 0.0
    
    # Calcular ∑_{k=1}^{K} θ_{d,k} * φ_{k,v} para todos los d,v
    # Producto matricial: theta @ phi = (D x K) @ (K x V) = (D x V)
    theta_phi = theta @ phi  # Shape: (D, V)
    
    # Evitar log(0) añadiendo epsilon pequeño
    epsilon = 1e-10
    theta_phi = np.maximum(theta_phi, epsilon)
    
    # Calcular log(∑_{k=1}^{K} θ_{d,k} * φ_{k,v})
    log_theta_phi = np.log(theta_phi)  # Shape: (D, V)
    
    # Calcular ∑_{v=1}^{V} n_{d,v} * log(...)
    suma_interna = np.sum(n_dv * log_theta_phi, axis=1)  # Shape: (D,)
    
    # Calcular la suma sobre todos los documentos
    suma_total = np.sum(suma_interna)
    
    # Aplicar fórmula completa con signo negativo y normalización
    entropia = -suma_total / total_palabras
    
    return float(entropia)


def calcular_perplexity(entropia):
    """
    Calcula la perplejidad a partir de la entropía.
    
    Perplexity = exp(-entropía)
    
    Args:
        entropia: Valor de entropía
    
    Returns:
        float: Valor de perplejidad
    """
    return np.exp(-entropia)