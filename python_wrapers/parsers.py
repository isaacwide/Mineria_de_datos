import spacy
import os
import pdfquery
from c_interface import matriz_topic_word, matriz_dic_topic #llamaos las funciones porque vamos a poceder con el parse 
nlp = spacy.load("es_core_news_sm")

def lematizar_texto(texto):
    doc =nlp(texto)
    lemas = [token.lema_ for token in doc if not token.is_punct and not token.is_space]
    return lemas

def eliminar_duplicados(r):
    palabras = set()
    palabras_unicas = []
    for palabra in r.splitlines(): #devuelve el texto cada que existe un salto de linbea
        if palabra not in palabras:
            palabras.add(palabra)
            palabras_unicas.append(palabra)
    return palabras_unicas 

def extraer_texto_pdf(ruta_pdf):
    pdf=pdfquery.PDFQuery(ruta_pdf)
    pdf.load()
    elementos_texto = pdf.pq('LTTextBoxHorizontal')
    texto = [t.text for t in elementos_texto if t.text is not None]
    return texto


def guardar_texto_en_txt(ruta, ruta_txt):
    text = extraer_texto_pdf(ruta)
    with open(ruta_txt, "w", encoding="utf-8") as f:
        contador = 0  # Empieza en 0
        decimal_value = 1
        f.write(f"DOCUMENT{decimal_value}\n")  # Escribe el primer documento
        
        for line in text:
            if line.strip():  # Si la línea no está vacía
                # como estamos llendo linea por linea nesesitamos usar algp para dividir palabra por palabra
                palabras = line.split()
                for palabra in palabras:
                    f.write(palabra + "\n")  # Escribe cada palabra en una nueva línea
                    contador += 1  # Incrementa el contador por cada palabra
                # Cuando llegues a 500 líneas, cambia de documento
                if contador >= 500:
                    contador = 0  # Reinicia el contador
                    decimal_value += 1
                    f.write(f"\nDOCUMENT{decimal_value}\n") 



def lematizar_y_eliminar_duplicados(ruta_txt):
    """
    1. Lee el texto original
    2. Lo lematiza y guarda en principito_lemas.txt
    3. Elimina duplicados y crea el diccionario en dic.txt
    """
    
    
    print("📖 Leyendo texto original...")
    with open(ruta_txt, "r", encoding="utf-8") as f:
        contenido = f.read()
    
    print("🔄 Lematizando texto...")
    lemmas = lematizar_texto(contenido)
    
    # Guardar lemmas (con repeticiones)
    ruta_lemmas = os.path.join("txts", "documento", "principito_lemas.txt")
    os.makedirs(os.path.dirname(ruta_lemmas), exist_ok=True)
    
    with open(ruta_lemmas, "w", encoding="utf-8") as f_out:
        f_out.write("\n".join(lemmas))
    
    print(f"✅ Lemmas guardados: {len(lemmas)} palabras")
    
    # ===== PASO 2: CREAR DICCIONARIO (sin duplicados) =====
    print("🗑️  Eliminando duplicados...")
    dic = eliminar_duplicados(lemmas)  # Directamente desde la lista
    
    # Guardar diccionario
    ruta_dic = os.path.join("txts", "dic", "dic.txt")
    os.makedirs(os.path.dirname(ruta_dic), exist_ok=True)
    
    with open(ruta_dic, "w", encoding="utf-8") as f_out:
        f_out.write("\n".join(dic))
    
    print(f"✅ Diccionario guardado: {len(dic)} palabras únicas")
    
    return {
        'lemmas_total': len(lemmas),
        'palabras_unicas': len(dic),
        'ruta_lemmas': ruta_lemmas,
        'ruta_dic': ruta_dic
    }
