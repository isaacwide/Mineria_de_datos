from flask import Flask, jsonify, render_template
import os 
from python_wrapers import c_interface
import numpy as np

app = Flask(__name__)

documentos = 13 
temas = 50
diccionario = 1195  # Ajusta según tu diccionario

filename1 = "txts/documento/principito_lemas.txt"
filename2 = "txts/temas/topicos.txt"
filename3 = "txts/dic/dic.txt"

# Calcular matrices al iniciar
print("Calculando matrices...")
matriz_1, apuntado = c_interface.matriz_topic_word(filename1, filename2, documentos, temas)
matriz_2, apuntado_2 = c_interface.matriz_dic_topic(filename2, filename3, diccionario, temas)

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
            "datos": matriz_1.tolist(),  # Convertir numpy array a lista
            "shape": matriz_1.shape,
            "descripcion": "Matriz Documento-Tópico"
        },
        "matriz_2": {
            "datos": matriz_2.tolist(),
            "shape": matriz_2.shape,
            "descripcion": "Matriz Palabra-Tópico"
        }
    })

if __name__ == "__main__":
    app.run(debug=True)