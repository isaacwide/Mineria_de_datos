from flask import Flask, jsonify, render_template, request
import os 
from python_wrapers import c_interface
from python_wrapers.lda_metrics import calcular_frecuencias_documento_palabra, calcular_entropia, calcular_perplexity
import numpy as np

app = Flask(__name__)

# Variables globales
documentos = 27
diccionario = 1022
temas = 50  # Valor por defecto

filename1 = "txts/documento/principito_lemas.txt"
filename2 = "txts/temas/topicos.txt"
filename3 = "txts/dic/dic.txt"

# Variables globales para las matrices (inicializadas como None)
matriz_1 = None
matriz_2 = None
apuntado = None
apuntado_2 = None
matriz_sigma = None
apuntado_sigma = None
n_dv = None


class palabraProbabilidad:
    def __init__(self, palabra, probabilidad):
        self.palabra = palabra
        self.probabilidad = probabilidad
    
    def __repr__(self):
        return f"{self.palabra}: {self.probabilidad:.4f}"


def inicializar_matrices():
    """Inicializa las matrices con los parámetros actuales"""
    global matriz_1, matriz_2, apuntado, apuntado_2, n_dv, temas, documentos, diccionario
    
    try:
        # Configurar parámetros en C
        print(f"📝 Configurando parámetros en C: docs={documentos}, temas={temas}, vocab={diccionario}")
        c_interface.iniciar_variables(documentos, temas, diccionario)
        
        print("📊 Calculando matriz 1...")
        resultado_1 = c_interface.matriz_topic_word(filename1, filename2, documentos, temas)
        if resultado_1:
            matriz_1, apuntado = resultado_1
            print(f"✅ Matriz 1 calculada: {matriz_1.shape}")
            # Debug de la matriz 1
            c_interface.debug_matriz_distribucion(matriz_1, "Matriz 1 (inicial)")
        else:
            print("❌ Error: matriz_1 es None")
            return False
        
        print("📊 Calculando matriz 2...")
        resultado_2 = c_interface.matriz_dic_topic(filename1, filename3, diccionario, temas)
        if resultado_2:
            matriz_2, apuntado_2 = resultado_2
            print(f"✅ Matriz 2 calculada: {matriz_2.shape}")
            # Debug de la matriz 2
            c_interface.debug_matriz_distribucion(matriz_2, "Matriz 2 (inicial)")
        else:
            print("❌ Error: matriz_2 es None")
            return False
        
        # Calcular frecuencias documento-palabra para métricas
        print("📊 Calculando frecuencias...")
        n_dv = calcular_frecuencias_documento_palabra(filename1, filename3, documentos, diccionario)
        print(f"✅ Frecuencias calculadas: {n_dv.shape}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en inicializar_matrices: {e}")
        import traceback
        traceback.print_exc()
        return False


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/api/configurar", methods=["POST"])
def configurar_parametros():
    """Endpoint para configurar el número de tópicos"""
    global temas, matriz_1, matriz_2, apuntado, apuntado_2, matriz_sigma, apuntado_sigma
    
    try:
        data = request.get_json()
        
        if not data or 'temas' not in data:
            return jsonify({"error": "Debe proporcionar el parámetro 'temas'"}), 400
        
        nuevos_temas = int(data['temas'])
        
        # Validar rango
        if nuevos_temas < 1 or nuevos_temas > 300:
            return jsonify({"error": "El número de temas debe estar entre 1 y 300"}), 400
        
        # Si es el mismo valor, no hacer nada
        if nuevos_temas == temas:
            return jsonify({
                "mensaje": "Los parámetros no han cambiado",
                "temas": temas,
                "documentos": documentos,
                "diccionario": diccionario
            })
        
        print(f"\n{'='*60}")
        print(f"🔄 Cambiando número de temas de {temas} a {nuevos_temas}")
        print(f"{'='*60}\n")
        
        # Liberar matrices anteriores
        if apuntado is not None and apuntado_2 is not None:
            try:
                c_interface.liberar_matrices(apuntado, apuntado_2, documentos, temas)
                print("✓ Memoria anterior liberada")
            except Exception as e:
                print(f"⚠️ Error al liberar memoria: {e}")
        
        # Resetear variables
        matriz_1 = None
        matriz_2 = None
        apuntado = None
        apuntado_2 = None
        matriz_sigma = None
        apuntado_sigma = None
        
        # Actualizar variable global
        temas = nuevos_temas
        
        # Reinicializar con nuevos parámetros
        print(f"🔄 Reinicializando matrices...")
        if not inicializar_matrices():
            return jsonify({"error": "No se pudieron reinicializar las matrices"}), 500
        
        print(f"✅ Configuración completada exitosamente\n")
        
        return jsonify({
            "mensaje": "Parámetros actualizados exitosamente",
            "temas": temas,
            "documentos": documentos,
            "diccionario": diccionario,
            "matriz_1_shape": list(matriz_1.shape),
            "matriz_2_shape": list(matriz_2.shape)
        })
    
    except ValueError:
        return jsonify({"error": "El valor de 'temas' debe ser un número entero"}), 400
    except Exception as e:
        print(f"❌ Error en configurar_parametros: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/parametros", methods=["GET"])
def obtener_parametros():
    """Endpoint para obtener los parámetros actuales"""
    return jsonify({
        "documentos": documentos,
        "temas": temas,
        "diccionario": diccionario,
        "matrices_inicializadas": matriz_1 is not None and matriz_2 is not None
    })


@app.route("/api/matrices", methods=["GET"])
def get_matrices():
    """Endpoint para obtener las matrices en formato JSON"""
    global matriz_1, matriz_2, apuntado, apuntado_2
    
    # Si las matrices no existen, inicializarlas
    if matriz_1 is None or matriz_2 is None:
        inicializar_matrices()
    
    if matriz_1 is None or matriz_2 is None:
        return jsonify({"error": "No se pudieron calcular las matrices"}), 500
    
    return jsonify({
        "matriz_1": {
            "datos": matriz_1.tolist(),
            "shape": list(matriz_1.shape),
            "descripcion": "Matriz Documento-Tópico"
        },
        "matriz_2": {
            "datos": matriz_2.tolist(),
            "shape": list(matriz_2.shape),
            "descripcion": "Matriz Palabra-Tópico"
        }
    })


@app.route("/api/matrizFinal", methods=["GET", "POST"])
def get_final():
    """Endpoint para calcular la matriz iterada"""
    global matriz_1, matriz_2, apuntado, apuntado_2
    
    repeticiones = request.args.get('repeticiones', default=100, type=int)
    print(f"Recibida petición para {repeticiones} repeticiones")
    
    # Verificar que los punteros existan
    if apuntado is None or apuntado_2 is None:
        print("Punteros vacios. Recalculando matrices...")
        inicializar_matrices()
    
    if apuntado is None or apuntado_2 is None:
        return jsonify({"error": "Las matrices base no están disponibles"}), 500
    
    try:
        matrizFinal, matriz_phi_actualizada = c_interface.calcular_matriz_final(
            apuntado, 
            apuntado_2, 
            repeticiones,
            documentos,
            temas
        )
        
        if matrizFinal is None:
            return jsonify({"error": "No se pudo calcular la matriz iterada"}), 500
        
        # Actualizar matriz_2 con la versión actualizada de Gibbs sampling
        if matriz_phi_actualizada is not None:
            matriz_2 = matriz_phi_actualizada
            print("✅ Matriz Phi actualizada después de Gibbs sampling")
        
        return jsonify({
            "datos": matrizFinal.tolist(),
            "shape": list(matrizFinal.shape),
            "repeticiones": repeticiones,
            "descripcion": f"Matriz Documento-Tópico iterada {repeticiones} veces"
        })
    
    except Exception as e:
        print(f"Error en get_final: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/topicosfinal", methods=["GET"])
def calcular_palabras_sigma():
    """Calcula las top 20 palabras por tópico"""
    global apuntado_2, matriz_sigma, apuntado_sigma, temas
    
    # Verificar que matriz_2 existe
    if apuntado_2 is None:
        print("Matriz 2 no disponible. Inicializando...")
        inicializar_matrices()
    
    if apuntado_2 is None:
        return jsonify({"error": "Matriz 2 no está disponible"}), 500
    
    # Calcular sigma si no existe
    if matriz_sigma is None:
        print("Calculando matriz sigma...")
        resultado = c_interface.param_sigma(apuntado_2, diccionario, temas)
        if resultado:
            apuntado_sigma, matriz_sigma = resultado
            print(f"Matriz sigma shape: {matriz_sigma.shape}")
        else:
            return jsonify({"error": "No se pudo calcular matriz sigma"}), 500
    
    # 1. Cargar diccionario
    dic = []
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ruta_txt = os.path.join(base_dir, "txts/dic", "dic.txt")
    
    # 2. Cargar nombres de tópicos
    nombres_temas = []
    ruta_temas = os.path.join(base_dir, "txts/temas", "topicos.txt")
    
    try:
        with open(ruta_txt, "r", encoding="utf-8") as f:
            for linea in f:
                palabra = linea.strip()
                if palabra:
                    dic.append(palabra)
        
        with open(ruta_temas, "r", encoding="utf-8") as f:
            for linea in f:
                nombre = linea.strip()
                if nombre:
                    nombres_temas.append(nombre)
    
    except FileNotFoundError as e:
        return jsonify({"error": f"No se encuentra el archivo: {e.filename}"}), 500
    
    # 3. Usar el tamaño real de la matriz sigma
    num_topicos_reales = matriz_sigma.shape[1]
    print(f"Procesando {num_topicos_reales} tópicos")
    
    # 4. Procesar cada tópico
    todos_topicos = []
    
    for p in range(num_topicos_reales):
        topico_n = []
        
        # Crear objeto para cada palabra en este tópico
        for i in range(len(dic)):
            palabras_ordenadas = palabraProbabilidad(dic[i], matriz_sigma[i][p])
            topico_n.append(palabras_ordenadas)
        
        # Ordenar por probabilidad (mayor a menor)
        topico_ordenado = sorted(topico_n, key=lambda x: x.probabilidad, reverse=True)
        
        # Obtener top 20
        top_20 = topico_ordenado[:20]
        
        # Convertir objetos a diccionarios para JSON
        top_20_dict = [
            {
                "palabra": obj.palabra,
                "probabilidad": float(obj.probabilidad)
            }
            for obj in top_20
        ]
        
        # Obtener nombre del tópico
        nombre_topico = nombres_temas[p] if p < len(nombres_temas) else f"Tópico {p}"
        
        todos_topicos.append({
            "topico": p,
            "nombre": nombre_topico,
            "top_palabras": top_20_dict
        })
    
    # 5. Retornar JSON
    return jsonify({
        "topicos": todos_topicos,
        "num_topicos": num_topicos_reales,
        "palabras_por_topico": 20
    })


@app.route("/api/entropia", methods=["GET"])
def get_entropia():
    """Endpoint para calcular la entropía del modelo"""
    global matriz_1, matriz_2, n_dv
    
    # Verificar que las matrices existen
    if matriz_1 is None or matriz_2 is None or n_dv is None:
        print("Matrices no disponibles. Inicializando...")
        inicializar_matrices()
    
    if matriz_1 is None or matriz_2 is None or n_dv is None:
        return jsonify({"error": "No se pudieron calcular las matrices"}), 500
    
    try:
        # Normalizar matrices con estabilidad numérica
        theta = matriz_1 / (np.sum(matriz_1, axis=1, keepdims=True) + 1e-12)
        phi = matriz_2 / (np.sum(matriz_2, axis=1, keepdims=True) + 1e-12)
        
        # Calcular métricas
        entropia = calcular_entropia(theta, phi, n_dv)
        perplexity = calcular_perplexity(entropia)
        
        print(f"=== MÉTRICAS BÁSICAS ===")
        print(f"Entropía: {entropia:.6f}")
        print(f"Perplejidad: {perplexity:.2f}")
        
        return jsonify({
            "entropia": float(entropia),
            "perplexity": float(perplexity),
            "descripcion": "Métricas del modelo LDA"
        })
    
    except Exception as e:
        print(f"Error en get_entropia: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/entropia-final", methods=["GET"])
def get_entropia_final():
    """Endpoint para calcular la entropía de la matriz iterada"""
    global matriz_1, matriz_2, apuntado, apuntado_2, n_dv
    
    try:
        repeticiones = request.args.get('repeticiones', default=100, type=int)
        
        # Verificar punteros
        if apuntado is None or apuntado_2 is None or n_dv is None:
            print("Punteros vacios. Recalculando matrices...")
            inicializar_matrices()
        
        if apuntado is None or apuntado_2 is None or n_dv is None:
            return jsonify({"error": "Las matrices base no están disponibles"}), 500
        
        matrizFinal, matriz_phi_actualizada = c_interface.calcular_matriz_final(
            apuntado, 
            apuntado_2, 
            repeticiones,
            documentos,
            temas
        )
        
        if matrizFinal is None:
            return jsonify({"error": "No se pudo calcular la matriz iterada"}), 500
        
        # Actualizar matriz_2 si hay una versión actualizada
        if matriz_phi_actualizada is not None:
            matriz_2 = matriz_phi_actualizada
            print("Matriz Phi actualizada para cálculo de entropía")
        
        # DEBUG: Verificar matrices antes del cálculo
        print("=== DEBUG ANTES DE CÁLCULO ENTROPÍA ===")
        print(f"matrizFinal shape: {matrizFinal.shape}, suma: {np.sum(matrizFinal):.2f}")
        print(f"matriz_2 shape: {matriz_2.shape}, suma: {np.sum(matriz_2):.2f}")
        print(f"n_dv shape: {n_dv.shape}, suma: {np.sum(n_dv):.2f}")
        
        # Normalizar theta (documento-tópico) con estabilidad numérica
        theta_sums = np.sum(matrizFinal, axis=1, keepdims=True)
        theta = matrizFinal / (theta_sums + 1e-12)
        
        # Normalizar phi (palabra-tópico) con estabilidad numérica  
        phi_sums = np.sum(matriz_2, axis=1, keepdims=True)
        phi = matriz_2 / (phi_sums + 1e-12)
        
        # Verificar normalización
        print(f"Theta normalizado - suma por filas: {np.sum(theta, axis=1)[:5]}")
        print(f"Phi normalizado - suma por filas: {np.sum(phi, axis=1)[:5]}")
        
        # Calcular entropía
        entropia = calcular_entropia(theta, phi, n_dv)
        
        # Calcular perplejidad
        perplexity = calcular_perplexity(entropia)
        
        print(f"=== RESULTADOS ENTROPÍA FINAL ===")
        print(f"Entropía: {entropia:.6f}")
        print(f"Perplejidad: {perplexity:.2f}")
        print(f"Iteraciones: {repeticiones}")
        
        return jsonify({
            "entropia": float(entropia),
            "perplexity": float(perplexity),
            "repeticiones": repeticiones,
            "descripcion": f"Métricas del modelo LDA iterado {repeticiones} veces"
        })
    
    except Exception as e:
        print(f"Error en get_entropia_final: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/liberar", methods=["POST"])
def liberar_memoria():
    """Endpoint opcional para liberar memoria al final"""
    global apuntado, apuntado_2
    
    try:
        if apuntado is not None and apuntado_2 is not None:
            c_interface.liberar_matrices(apuntado, apuntado_2, documentos, temas)
            return jsonify({"mensaje": "Memoria liberada exitosamente"})
        else:
            return jsonify({"mensaje": "No hay memoria para liberar"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    try:
        print("\n" + "="*60)
        print("🚀 Iniciando servidor Flask...")
        print("="*60 + "\n")
        
        # Inicializar matrices al arrancar
        inicializar_matrices()
        
        print("\n" + "="*60)
        print("✅ Servidor listo en http://127.0.0.1:5000")
        print("="*60 + "\n")
        
        app.run(debug=True, port=5000)
    except Exception as e:
        print(f"\n❌ Error al iniciar: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nLiberando memoria...")
        if apuntado is not None and apuntado_2 is not None:
            c_interface.liberar_matrices(apuntado, apuntado_2, documentos, temas)