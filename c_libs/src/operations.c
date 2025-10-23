#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include<time.h>

// Declaración adelantada de la función
float numeros_aleatorios();
int es_delimitador(char *palabra);


// Función para verificar si una palabra es un delimitador y funcion para numeros random
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
float numeros_aleatorios() {
    return (float)rand() / RAND_MAX;
}


__declspec(dllexport) void word_in_topic(char *filename1, char *filename2) {
    FILE *file1 = fopen(filename1, "r");
    FILE *file2 = fopen(filename2, "r");
    int mtx_1[13][300] = {0};

    if(file1 == NULL || file2 == NULL) {
        printf("Error al abrir los archivos.\n");
        if(file1) fclose(file1);
        if(file2) fclose(file2);
        return;
    }

    double rangos[301] = {0};
    for(int i = 0; i < 300; i++){
        rangos[i+1] = rangos[i] + 0.00333;
    }

    char palabra[100];
    int l = 0;
    
    while (fscanf(file1, "%s", palabra) != EOF) {
        if (es_delimitador(palabra)){
            l++;
        } else {
            if(l > 0 && l <= 13) {
                float probabilidad = numeros_aleatorios();
                for(int j = 0; j < 300; j++){
                    if (probabilidad >= rangos[j] && probabilidad < rangos[j+1]){
                        mtx_1[l-1][j]++;
                        break;
                    }
                }
            }
        }
    }

    printf("\nMatriz mtx_1 (todos los valores):\n");
    for(int i = 0; i < 13; i++) {
        for(int j = 0; j < 300; j++) {
            printf("%d ", mtx_1[i][j]);
        }
        printf("\n");
    }

    FILE *output =fopen("matrices.txt", "w");

    if (output == NULL) {
        printf("Error al abrir el archivo de salida.\n");
        fclose(file1);
        fclose(file2);
        return;
    }
    // aqui imprimiriamos la matriz en el archivo matrices.txt para ver los resultados 
    fprintf(output, "Matriz mtx_1 (todos los valores):\n");
    fprintf(output, "Filas: Documentos (1-13), Columnas: Tópicos (1-300)\n");
    for(int i = 0; i < 13; i++){
        for(int j = 0; j < 300; j++){
            fprintf(output, "%d ", mtx_1[i][j]);

        }
        fprintf(output, "\n");
    }
    fclose(output);
    fclose(file1);
    fclose(file2);
}

__declspec(dllexport)void dic_in_topic(char *filename2, char *filename3) {
    FILE *file_dic = fopen(filename3, "r");
    if (file_dic == NULL) {
        printf("Error al abrir el archivo diccionario: %s\n", filename3);
        return;
    }

    char diccionario[1300][100];
    int num_palabras_dic = 0;
    while (fscanf(file_dic, "%s", diccionario[num_palabras_dic]) != EOF && num_palabras_dic < 1300) {
        num_palabras_dic++;
    }
    fclose(file_dic);
    printf("Diccionario cargado con %d palabras.\n", num_palabras_dic);

    double rangos[301] = {0};
    for(int i = 0; i < 300; i++){
        rangos[i+1] = rangos[i] + (1.0 / 300.0);
    }

    //Crear e inicializar la matriz de asignación [palabra][topico].
    int mtx_2[num_palabras_dic][300];
    for(int i = 0; i < num_palabras_dic; i++) {
    for(int j = 0; j < 300; j++) {
        mtx_2[i][j] = 0;
    }
    }


    for (int i = 0; i < num_palabras_dic; i++) {
        float probabilidad = numeros_aleatorios();
        for (int j = 0; j < 300; j++) {
            if (probabilidad >= rangos[j] && probabilidad < rangos[j+1]) {
                // Se marca con '1' la asignación de la palabra 'i' al tópico 'j'.
                mtx_2[i][j] = 1;
                break; // Pasa a la siguiente palabra una vez asignado el tópico.
            }
        }
    }
   FILE *out2 = fopen("matriz2.txt","w");
        if (out2 == NULL) {
            printf("Error al abrir matriz2.txt para escritura\n");
            return;
        }

        // Opcional: puedes quitar o mejorar esta línea
        fprintf(out2,"Matriz de asignación de tópicos\n\n");

        printf("\nMatriz mtx_2 (asignacion de topico por palabra del diccionario):\n");
        for (int i = 0; i < num_palabras_dic; i++) {
            for (int j = 0; j < 300; j++) {
                fprintf(out2,"%d ", mtx_2[i][j]);
            }
            fprintf(out2,"\n");  // Salto de línea después de cada fila
        }
        fclose(out2);
}
