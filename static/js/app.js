document.addEventListener('DOMContentLoaded', function() {
    const botonMostrar = document.getElementById('click');
    const resultadosDiv = document.getElementById('resultados');
    
    botonMostrar.addEventListener('click', async function() {
        try {
            // Mostrar loading
            botonMostrar.disabled = true;
            botonMostrar.innerHTML = '<span>Cargando...</span>';
            
            // Obtener AMBAS matrices
            const [response1, response2] = await Promise.all([
                fetch('/api/matrices'),
                fetch('/api/matrizFinal?repeticiones=300')
            ]);
            
            const data1 = await response1.json();
            const data2 = await response2.json();
            
            if (data1.error || data2.error) {
                alert('Error: ' + (data1.error || data2.error));
                return;
            }
            
            // Combinar los datos
            const dataCombinada = {
                matriz_1: data1.matriz_1,
                matriz_2: data1.matriz_2,
                matriz_final: data2  // La matriz iterada
            };
            
            // Mostrar resultados
            mostrarMatrices(dataCombinada);
            
            // Animar aparición
            resultadosDiv.classList.remove('hidden');
            setTimeout(() => {
                resultadosDiv.classList.remove('opacity-0');
            }, 10);
            
            // Ocultar botón
            botonMostrar.style.display = 'none';
            
        } catch (error) {
            console.error('Error:', error);
            alert('Error al cargar los datos');
        } finally {
            botonMostrar.disabled = false;
        }
    });
});

function mostrarMatrices(data) {
    const resultadosDiv = document.getElementById('resultados');
    
    const html = `
        <div class="border-t-2 border-purple-200 pt-8">
            <h3 class="text-2xl font-bold text-gray-800 mb-6 flex items-center">
                <svg class="w-8 h-8 text-purple-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                </svg>
                Resultados del Análisis LDA
            </h3>
            
            <!-- Matriz 1 -->
            <div class="mb-8 bg-gradient-to-br from-purple-50 to-indigo-50 rounded-xl p-6 border-2 border-purple-200">
                <h4 class="text-xl font-bold text-purple-800 mb-4">
                    ${data.matriz_1.descripcion}
                </h4>
                <p class="text-gray-600 mb-4">
                    Dimensiones: ${data.matriz_1.shape[0]} documentos × ${data.matriz_1.shape[1]} tópicos
                </p>
                <div class="overflow-x-auto">
                    ${generarTablaMatriz(data.matriz_1.datos, 'Documento', 'Tópico')}
                </div>
            </div>
            
            <!-- Matriz 2 -->
            <div class="mb-8 bg-gradient-to-br from-indigo-50 to-pink-50 rounded-xl p-6 border-2 border-indigo-200">
                <h4 class="text-xl font-bold text-indigo-800 mb-4">
                    ${data.matriz_2.descripcion}
                </h4>
                <p class="text-gray-600 mb-4">
                    Dimensiones: ${data.matriz_2.shape[0]} palabras × ${data.matriz_2.shape[1]} tópicos
                </p>
                <div class="overflow-x-auto">
                    ${generarTablaMatriz(data.matriz_2.datos.slice(0, 20), 'Palabra', 'Tópico', true)}
                </div>
            </div>

            <!-- Matriz Final (Iterada) -->
            <div class="mb-8 bg-gradient-to-br from-green-50 to-teal-50 rounded-xl p-6 border-2 border-green-200">
                <h4 class="text-xl font-bold text-green-800 mb-4">
                    ${data.matriz_final.descripcion}
                </h4>
                <p class="text-gray-600 mb-4">
                    Dimensiones: ${data.matriz_final.shape[0]} documentos × ${data.matriz_final.shape[1]} tópicos
                    <br>
                    <span class="text-purple-600 font-semibold">Iteraciones: ${data.matriz_final.repeticiones}</span>
                </p>
                <div class="overflow-x-auto">
                    ${generarTablaMatriz(data.matriz_final.datos, 'Documento', 'Tópico')}
                </div>
            </div>
        </div>
    `;
    
    resultadosDiv.innerHTML = html;
}

function generarTablaMatriz(datos, labelFila, labelColumna, limitarColumnas = false) {
    const filas = datos.length;
    const columnas = limitarColumnas ? Math.min(10, datos[0].length) : datos[0].length;
    
    let html = '<table class="min-w-full bg-white rounded-lg overflow-hidden shadow-md text-sm">';
    
    // Header
    html += '<thead class="bg-gradient-to-r from-purple-500 to-indigo-500 text-white">';
    html += '<tr><th class="px-4 py-2">' + labelFila + '</th>';
    for (let j = 0; j < columnas; j++) {
        html += `<th class="px-4 py-2">${labelColumna} ${j}</th>`;
    }
    html += '</tr></thead>';
    
    // Body
    html += '<tbody>';
    for (let i = 0; i < Math.min(10, filas); i++) {
        html += `<tr class="${i % 2 === 0 ? 'bg-gray-50' : 'bg-white'}">`;
        html += `<td class="px-4 py-2 font-semibold text-purple-600">${i}</td>`;
        for (let j = 0; j < columnas; j++) {
            const valor = datos[i][j].toFixed(4);
            const color = datos[i][j] > 0.5 ? 'text-green-600 font-bold' : 'text-gray-600';
            html += `<td class="px-4 py-2 ${color}">${valor}</td>`;
        }
        html += '</tr>';
    }
    html += '</tbody></table>';
    
    return html;
}