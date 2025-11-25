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
    Calcula la entropía del modelo LDA (cross-entropy).
    
    Fórmula CORREGIDA:
    entropía = -∑_{d=1}^{D} [∑_{v=1}^{V} n_{d,v} * log(∑_{k=1}^{K} θ_{d,k} * φ_{k,v})] / ∑_{d=1}^{D} N_d
    
    Args:
        theta: Matriz documento-tópico (D x K) - NORMALIZADA (suma por documento = 1)
        phi: Matriz palabra-tópico (K x V) - NORMALIZADA (suma por tópico = 1)
        n_dv: Matriz de frecuencias documento-palabra (D x V)
    
    Returns:
        float: Valor de entropía
    """
    D, K = theta.shape
    K_phi, V = phi.shape
    
    # Verificar dimensiones
    if K != K_phi:
        raise ValueError(f"Dimensiones inconsistentes: theta tiene {K} tópicos, phi tiene {K_phi}")
    
    epsilon = 1e-15  # Valor más pequeño para mayor estabilidad
    
    # Calcular N_d (total de palabras por documento)
    N_d = np.sum(n_dv, axis=1)
    total_palabras_corpus = np.sum(N_d)
    
    if total_palabras_corpus == 0:
        return 0.0
    
    # Calcular P(palabra_v | documento_d) = ∑_{k=1}^{K} θ_{d,k} * φ_{k,v}
    p_word_given_doc = np.dot(theta, phi)
    
    # Aplicar logaritmo con estabilidad numérica
    p_word_given_doc = np.clip(p_word_given_doc, epsilon, 1.0)
    log_p = np.log(p_word_given_doc)
    
    # Calcular ∑_{v=1}^{V} n_{d,v} * log(P(v|d)) para cada documento
    sum_n_log_p = np.sum(n_dv * log_p, axis=1)
    
    # Sumar sobre todos los documentos y normalizar
    entropia = -np.sum(sum_n_log_p) / total_palabras_corpus
    
    return float(entropia)


def calcular_perplexity(entropia):
    """
    Calcula la perplejidad a partir de la entropía.
    
    Perplexity = exp(entropía)
    
    Args:
        entropia: Valor de entropía
    
    Returns:
        float: Valor de perplejidad
    """
    return np.exp(entropia)