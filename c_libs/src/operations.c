#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include<time.h>

#define documentos 13
#define temas 50
#define palabras_dic 1063
#define betha 1.0
#define alfa 0.01

// Declaración adelantada de la función
float numeros_aleatorios();
int es_delimitador(char *palabra);

float numeros_aleatorios() {
    return (float)rand() / RAND_MAX;
}
int es_delimitador(char *palabra) {
    // Delimitadores exactos
    const char *delims[] = {
        "DOCUMENT1", "DOCUMENT2", "DOCUMENT3", "DOCUMENT4", "DOCUMENT5",
        "DOCUMENT6", "DOCUMENT7", "DOCUMENT8", "DOCUMENT9", "DOCUMENT10",
        "DOCUMENT11", "DOCUMENT12", "DOCUMENT13", "DOCUMENT14", "DOCUMENT15",
        "DOCUMENT16", "DOCUMENT17", "DOCUMENT18", "DOCUMENT19", "DOCUMENT20",
        "DOCUMENT21", "DOCUMENT22", "DOCUMENT23", "DOCUMENT24", "DOCUMENT25",
        "DOCUMENT26", "DOCUMENT27",
        "document1", "document2", "document3", "document4", "document5",
        "document6", "document7", "document8", "document9", "document10",
        "document11", "document12", "document13", "document14", "document15",
        "document16", "document17", "document18", "document19", "document20",
        "document21", "document22", "document23", "document24", "document25",
        "document26", "document27"
    };
    
    for(int i = 0; i < 54; i++) {
        if(strcmp(palabra, delims[i]) == 0) {
            return 1;
        }
    }
    return 0;
}


__declspec(dllexport) float** word_in_topic(char *filename1, char *filename2) {
    FILE *file1 = fopen(filename1, "r");
    FILE *file2 = fopen(filename2, "r");
    
    // Asignar memoria dinámica para la matriz
    float **mtx_1 = (float**)malloc(documentos * sizeof(float*));
    for(int i = 0; i < documentos; i++) {
        mtx_1[i] = (float*)calloc(temas, sizeof(float)); // calloc inicializa en 0.0
    }

    if(file1 == NULL || file2 == NULL) {
        printf("Error al abrir los archivos.\n");
        if(file1) fclose(file1);
        if(file2) fclose(file2);
        // Liberar memoria antes de retornar
        for(int i = 0; i < documentos; i++) {
            free(mtx_1[i]);
        }
        free(mtx_1);
        return NULL;
    }

    double rangos[301] = {0};
    for(int i = 0; i < temas; i++){
        rangos[i+1] = rangos[i] + 0.02;
    }

    char palabra[100];
    int l = 0;
    
    while (fscanf(file1, "%s", palabra) != EOF) {
        if (es_delimitador(palabra)){
            l++;
        } else {
            if(l > 0 && l <= documentos) {
                float probabilidad = numeros_aleatorios();
                for(int j = 0; j < temas; j++){
                    if (probabilidad >= rangos[j] && probabilidad < rangos[j+1]){
                        mtx_1[l-1][j]++;
                        break;
                    }
                }
            }
        }
    }

    fclose(file1);
    fclose(file2);
    return mtx_1;
}

__declspec(dllexport) float** dic_in_topic(char *filename1, char *filename3) {
    // 1. CARGAR DICCIONARIO
    FILE *file_dic = fopen(filename3, "r");
    if (file_dic == NULL) {
        printf("Error al abrir el archivo diccionario: %s\n", filename3);
        return NULL;
    }

    char diccionario[1300][100];
    int num_palabras_dic = 0;
    while (fscanf(file_dic, "%s", diccionario[num_palabras_dic]) != EOF && num_palabras_dic < 1300) {
        num_palabras_dic++;
    }
    fclose(file_dic);
    printf("Diccionario cargado con %d palabras.\n", num_palabras_dic);

    // 2. CREAR MATRIZ [tópicos][palabras]
    float **mtx_2 = (float**)malloc(temas * sizeof(float*));
    for(int i = 0; i < temas; i++) {
        mtx_2[i] = (float*)calloc(num_palabras_dic, sizeof(float));
    }
    
    // 3. LEER DOCUMENTO Y ASIGNAR TÓPICOS ALEATORIOS
    FILE *file_docs = fopen(filename1, "r");
    if (file_docs == NULL) {
        printf("Error al abrir el archivo de documentos: %s\n", filename1);
        for(int i = 0; i < temas; i++) {
            free(mtx_2[i]);
        }
        free(mtx_2);
        return NULL;
    }

    // Crear rangos para asignación aleatoria uniforme
    double rangos[51] = {0};
    for(int i = 0; i < temas; i++){
        rangos[i+1] = rangos[i] + (1.0 / (double)temas);
    }

    char palabra[100];
    int doc_actual = 0;
    
    // Leer cada palabra del documento
    while (fscanf(file_docs, "%s", palabra) != EOF) {
        if (es_delimitador(palabra)) {
            doc_actual++;
        } else {
            if (doc_actual > 0 && doc_actual <= documentos) {
                // Buscar la palabra en el diccionario
                int palabra_encontrada = 0;
                for (int j = 0; j < num_palabras_dic; j++) {
                    if (strcmp(diccionario[j], palabra) == 0) {
                        // Asignar tópico aleatorio a esta ocurrencia de la palabra
                        float probabilidad = numeros_aleatorios();
                        for(int t = 0; t < temas; t++){
                            if (probabilidad >= rangos[t] && probabilidad < rangos[t+1]){
                                mtx_2[t][j]++;  // [tópico][palabra_del_diccionario]
                                break;
                            }
                        }
                        palabra_encontrada = 1;
                        break;
                    }
                }
            }
        }
    }
    fclose(file_docs);
    
    printf("Matriz dic_in_topic inicializada con asignaciones aleatorias.\n");
    return mtx_2;
}

float *n_ms(float **mtx_1){
    float *n_m = (float*)calloc(documentos, sizeof(float));
    // Calcular n_m para todos los documentos
    for(int i = 0; i < documentos; i++){
        for(int j = 0; j < temas; j++){
            n_m[i] += mtx_1[i][j];
        }
    }

    return n_m;
}

float*n_ks(float**mtx_2){
    float* n_k = (float*)calloc(temas, sizeof(float)); 
    for(int i = 0; i < temas; i++){
        for(int j = 0; j < palabras_dic; j++){
            n_k[i] += mtx_2[i][j];
        }
    }

    return n_k;
}

__declspec(dllexport) float** parametro_sigma(float **mtx_2){
    if (mtx_2 == NULL) {
        printf("Error: mtx_2 es NULL\n");
        return NULL;
    }
    // Calcular n_k para TODAS las palabras
    float * n_k = n_ks(mtx_2);
    
    // Asignar memoria para sigma
    float **sigma = (float**)malloc(palabras_dic * sizeof(float*));
    for(int i = 0; i < palabras_dic; i++){
        sigma[i] = (float*)calloc(temas, sizeof(float));
    }
    // Calcular sigma
    for(int k = 0; k < palabras_dic; k++){
        for(int t = 0; t < temas; t++){
            float a = mtx_2[k][t] + betha;
            float b = n_k[k] + (betha * palabras_dic); // Usar temas, que es 50
            
            if (b > 0) {
                sigma[k][t] = a / b;
            } else {
                sigma[k][t] = 0.0;
            }
        }
    }
    
    printf("Sigma calculado correctamente\n");
    free(n_k);
    
    return sigma;
}

float** parametro_gama(float **mtx_1){
    
    
    if (mtx_1 == NULL) {
        printf("Error: mtx_1 es NULL\n");
        return NULL;
    }
    float* n_m = n_ms(mtx_1);
    // Asignar memoria para gama
    float **gama = (float**)malloc(documentos * sizeof(float*));
    for(int i = 0; i < documentos; i++){
        gama[i] = (float*)calloc(temas, sizeof(float));
    }
    // Calcular gama
    for(int k = 0; k < documentos; k++){
        for(int t = 0; t < temas; t++){
            float a = mtx_1[k][t] + alfa;
            float b = n_m[k] + (alfa * temas);  // Sumar alfa * número de tópicos
            
            if (b > 0) {
                gama[k][t] = a / b;
            } else {
                gama[k][t] = 0.0;
            } 
        }
    }
    
    printf("Gama calculado correctamente\n");
    
    // Liberar n_m
    free(n_m);
    
    return gama;
}

// Estructura para almacenar información del documento
typedef struct {
    char **palabras;
    int *doc_id;
    int num_palabras;
} DocumentoInfo;

// Función para cargar el diccionario en memoria
char** cargar_diccionario(char *filename, int *num_palabras) {
    FILE *f = fopen(filename, "r");
    if (!f) return NULL;
    
    char **dic = (char**)malloc(palabras_dic * sizeof(char*));
    *num_palabras = 0;
    char buffer[100];
    
    while (fscanf(f, "%s", buffer) != EOF && *num_palabras < palabras_dic) {
        dic[*num_palabras] = (char*)malloc(strlen(buffer) + 1);
        strcpy(dic[*num_palabras], buffer);
        (*num_palabras)++;
    }
    fclose(f);
    return dic;
}

// Función para buscar palabra en diccionario (en memoria)
int buscar_en_diccionario(char *palabra, char **diccionario, int num_palabras) {
    for(int i = 0; i < num_palabras; i++) {
        if(strcmp(palabra, diccionario[i]) == 0) {
            return i;
        }
    }
    return -1;
}

// Cargar documento en memoria
DocumentoInfo* cargar_documento(char *filename) {
    FILE *f = fopen(filename, "r");
    if (!f) return NULL;
    
    DocumentoInfo *info = (DocumentoInfo*)malloc(sizeof(DocumentoInfo));
    info->palabras = (char**)malloc(50000 * sizeof(char*)); // Aumentar tamaño por seguridad
    info->doc_id = (int*)malloc(50000 * sizeof(int));
    info->num_palabras = 0;
    
    char palabra[100];
    int doc_actual = 0;
    
    while (fscanf(f, "%s", palabra) != EOF) {
        if (es_delimitador(palabra)) {
            doc_actual++;
        } else {
            if (doc_actual > 0 && doc_actual <= documentos) {
                // Verificar límites de memoria
                if (info->num_palabras >= 50000) {
                    printf("Advertencia: Se superó el límite de palabras en DocumentoInfo.\n");
                    break; 
                }
                info->palabras[info->num_palabras] = (char*)malloc(strlen(palabra) + 1);
                strcpy(info->palabras[info->num_palabras], palabra);
                info->doc_id[info->num_palabras] = doc_actual - 1;
                info->num_palabras++;
            }
        }
    }
    fclose(f);
    return info;
}

float *vector_intervalos(int posDic, int posDocumento, float **mtx_1, float **mtx_2){
    float* v = (float*)calloc(temas, sizeof(float)); // Usar calloc para inicializar a 0.0
    
    if (posDic < 0 || posDic >= palabras_dic) {
        for(int i = 0; i < temas; i++) {
            v[i] = 1.0 / temas;
        }
        return v;
    }
    

    float * n_m = n_ms(mtx_1);
    float * n_k = n_ks(mtx_2);
    
    for(int i = 0; i < temas; i++){
        float a = mtx_2[i][posDic] + betha;
        float b = n_k[posDic] + (betha * temas);
        float primerCociente = (b > 0) ? (a / b) : 0.0; // P(palabra|tópico)

        // Termino de la distribución de tópicos por documento (gamma)
        float a_1 = mtx_1[posDocumento][i] + alfa;
        float b_1 = n_m[posDocumento] + (alfa * palabras_dic);
        float segundoCociente = (b_1 > 0) ? (a_1 / b_1) : 0.0; // P(tópico|documento)

        // El vector v[i] es proporcional a P(palabra|tópico) * P(tópico|documento)
        v[i] = primerCociente * segundoCociente; 
    }
    
    free(n_m);
    free(n_k);
    
    return v;
}

__declspec(dllexport)float** matriz_final(float **mtx_1, float **mtx_2, int n, char *docs){
    
    int num_palabras_dic_cargado = 0;
    char **diccionario = cargar_diccionario("txts/dic/dic.txt", &num_palabras_dic_cargado);
    if (!diccionario) {
        printf("Error al cargar diccionario en matriz_final.\n");
        return NULL;
    }
    printf("Diccionario cargado para remuestreo con %d palabras.\n", num_palabras_dic_cargado);
    
    DocumentoInfo *doc_info = cargar_documento(docs);
    if (!doc_info) {
        printf("Error al cargar documento en matriz_final.\n");
        for(int i = 0; i < num_palabras_dic_cargado; i++) free(diccionario[i]);
        free(diccionario);
        return NULL;
    }
    printf("Documento cargado para remuestreo con %d ocurrencias de palabras.\n", doc_info->num_palabras);
    //TORNEO DE PVP EL VIERNES A LAS 8pm
    //CATEGORIAS FREE (GRATIS) Y CAVOID (cuota de 20 pesos)
    //mas info en el grupo de whatsapp del server
    float **mtx_1_actualizado = (float**)malloc(documentos * sizeof(float*));
    for(int i = 0; i < documentos; i++) {
        mtx_1_actualizado[i] = (float*)calloc(temas, sizeof(float)); 
        for(int j = 0; j < temas; j++) {
             mtx_1_actualizado[i][j] = mtx_1[i][j];
        }
    }
    
    float **mtx_2_actualizado = (float**)malloc(temas * sizeof(float*));
    for(int i = 0; i < temas; i++) {
        mtx_2_actualizado[i] = (float*)calloc(palabras_dic, sizeof(float));
        for(int j = 0; j < palabras_dic; j++) {
            mtx_2_actualizado[i][j] = mtx_2[i][j];
        }
    }
    
    float **mtx_f = (float**)malloc(documentos * sizeof(float*));
    for(int i = 0; i < documentos; i++) {
        mtx_f[i] = (float*)calloc(temas, sizeof(float)); 
    }
    
    // Array para guardar el tópico asignado a cada ocurrencia de palabra
    int *topic_assignments = (int*)malloc(doc_info->num_palabras * sizeof(int));
    
    for (int p = 0; p < doc_info->num_palabras; p++) {
        char *palabra = doc_info->palabras[p];
        int doc_index = doc_info->doc_id[p];
        int dic_index = buscar_en_diccionario(palabra, diccionario, num_palabras_dic_cargado);
        
        if (dic_index != -1) {
            int topic = (int)(numeros_aleatorios() * temas);
            if(topic >= temas) topic = temas - 1;
            topic_assignments[p] = topic;
            
            mtx_1_actualizado[doc_index][topic]++;
            mtx_2_actualizado[topic][dic_index]++;
        } else {
            topic_assignments[p] = -1; // Palabra no en diccionario
        }
    }
    
    // Gibbs Sampling
    for(int iter = 0; iter < n; iter++) {
        
        for (int p = 0; p < doc_info->num_palabras; p++) {
            
            char *palabra = doc_info->palabras[p];
            int doc_index = doc_info->doc_id[p];
            int dic_index = buscar_en_diccionario(palabra, diccionario, num_palabras_dic_cargado);
            
            if (dic_index != -1) {
                

                int old_topic = topic_assignments[p];
                
                if (old_topic != -1) {
                    mtx_1_actualizado[doc_index][old_topic]--;
                    mtx_2_actualizado[old_topic][dic_index]--;
                }

                //calcular distribución de probabilidad para nuevo tópico
                float *v = vector_intervalos(dic_index, doc_index, mtx_1_actualizado, mtx_2_actualizado);
                
                float suma = 0.0;
                for(int j = 0; j < temas; j++){
                    suma += v[j];
                }
                
                int new_topic = -1;
                
                if (suma > 0) {
                    float *rangos = (float*)malloc((temas + 1) * sizeof(float));
                    rangos[0] = 0.0;
                    for(int j = 0; j < temas; j++){
                        rangos[j+1] = rangos[j] + (v[j] / suma);
                    }
                    
                    float probabilidad = numeros_aleatorios();
                    for(int j = 0; j < temas; j++){
                        if (probabilidad >= rangos[j] && probabilidad < rangos[j+1]){
                            new_topic = j;
                            break;
                        }
                    }
                    free(rangos);
                } else {
                    new_topic = (int)(numeros_aleatorios() * temas);
                    if(new_topic >= temas) new_topic = temas - 1;
                }
                
                free(v);

                //asigna nuevo tópico e incrementar contadores
                if (new_topic != -1) {
                    topic_assignments[p] = new_topic;
                    mtx_1_actualizado[doc_index][new_topic]++;
                    mtx_2_actualizado[new_topic][dic_index]++;
                }
            }
        }
    } 
    
    for(int k = 0; k < documentos; k++) {
        for(int t = 0; t < temas; t++) {
            mtx_f[k][t] = mtx_1_actualizado[k][t];
        }
    }
    
    // Liberar memoria
    for(int k = 0; k < documentos; k++) free(mtx_1_actualizado[k]);
    free(mtx_1_actualizado);
    
    for(int k = 0; k < temas; k++) free(mtx_2_actualizado[k]);
    free(mtx_2_actualizado);

    for(int k = 0; k < num_palabras_dic_cargado; k++) free(diccionario[k]);
    free(diccionario);
    
    for(int k = 0; k < doc_info->num_palabras; k++) free(doc_info->palabras[k]);
    free(doc_info->palabras);
    free(doc_info->doc_id);
    free(doc_info);
    
    free(topic_assignments);

    return mtx_f;
}

__declspec(dllexport) void free_matrix(float** matrix, int rows) {
    for(int i = 0; i < rows; i++) {
        free(matrix[i]);
    }
    free(matrix);
}
