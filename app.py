from flask import Flask, jsonify, render_template, request
import os 
from python_wrapers import c_interface
import numpy as np

app = Flask(__name__)

documentos = 7
temas = 50
diccionario = 1064

filename1 = "txts/documento/principito_lemas.txt"
filename2 = "txts/temas/topicos.txt"
filename3 = "txts/dic/dic.txt"

# Calcular matrices al iniciar
print("Calculando matrices iniciales...")
matriz_1, apuntado = c_interface.matriz_topic_word(filename1, filename2, documentos, temas)
matriz_2, apuntado_2 = c_interface.matriz_dic_topic(filename1, filename3, diccionario, temas)

matriz_sigma = c_interface.param_sigma(apuntado_2)

print("Matriz 1 shape:", matriz_1.shape if matriz_1 is not None else "None")
print("Matriz 2 shape:", matriz_2.shape if matriz_2 is not None else "None")


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/api/matrices", methods=["GET"])
def get_matrices():
    """Endpoint para obtener las matrices en formato JSON"""
    if matriz_1 is None or matriz_2 is None:
        return jsonify({"error": "No se pudieron calcular las matrices"}), 500
    
    return jsonify({
        "matriz_1": {
            "datos": matriz_1.tolist(),
            "shape": matriz_1.shape,
            "descripcion": "Matriz Documento-Tópico"
        },
        "matriz_2": {
            "datos": matriz_2.tolist(),
            "shape": matriz_2.shape,
            "descripcion": "Matriz Palabra-Tópico"
        }
    })


@app.route("/api/matrizFinal", methods=["GET", "POST"])
def get_final():
    """Endpoint para calcular la matriz iterada"""
    repeticiones = request.args.get('repeticiones', default=100, type=int)
    
    print(f"Recibida petición para {repeticiones} repeticiones")
    
    # Verificar que los punteros existan
    global matriz_1, matriz_2, apuntado, apuntado_2
    if apuntado is None or apuntado_2 is None:
        print ("Punteros vacios. Recalclando matrices...")
        matriz_1, apuntado = c_interface.matriz_topic_word(filename1, filename2, documentos, temas)
        matriz_2, apuntado_2 = c_interface.matriz_dic_topic(filename1, filename3, diccionario, temas)
    
    if apuntado is None or apuntado_2 is None:
        return jsonify({"error": "Las matrices base no están disponibles"}), 500
    
    try:
        matrizFinal = c_interface.calcular_matriz_final(apuntado, apuntado_2, repeticiones)
        
        if matrizFinal is None:
            return jsonify({"error": "No se pudo calcular la matriz iterada"}), 500
        
        return jsonify({
            "datos": matrizFinal.tolist(),
            "shape": matrizFinal.shape,
            "repeticiones": repeticiones,
            "descripcion": f"Matriz Documento-Tópico iterada {repeticiones} veces"
        })
    
    except Exception as e:
        print(f"Error en get_final: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/liberar", methods=["POST"])
def liberar_memoria():
    """Endpoint opcional para liberar memoria al final"""
    try:
        c_interface.liberar_matrices(apuntado, apuntado_2, documentos, temas)
        return jsonify({"mensaje": "Memoria liberada exitosamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    try:
        app.run(debug=True)
    finally:
        print("Liberando memoria...")
        c_interface.liberar_matrices(apuntado, apuntado_2, documentos, temas)