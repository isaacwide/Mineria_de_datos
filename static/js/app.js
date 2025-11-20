document.addEventListener('DOMContentLoaded', function() {
    const botonMostrar = document.getElementById('click');
    const resultadosDiv = document.getElementById('resultados');
    
    botonMostrar.addEventListener('click', async function() {
        try {
            // Mostrar loading
            botonMostrar.disabled = true;
            botonMostrar.innerHTML = `
                <span class="flex items-center space-x-2">
                    <svg class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span>Cargando...</span>
                </span>
            `;
            
            const Iteraciones = document.getElementById('iteraciones').value;
            
            // Obtener TODAS las matrices incluyendo tópicos y métricas de entropía
            const [response1, response2, response3, response4] = await Promise.all([
                fetch('/api/matrices'),
                fetch(`/api/matrizFinal?repeticiones=${Iteraciones}`),
                fetch('/api/topicosfinal'),
                fetch(`/api/entropia-final?repeticiones=${Iteraciones}`)
            ]);
            
            const data1 = await response1.json();
            const data2 = await response2.json();
            const data3 = await response3.json();
            const data4 = await response4.json();
            
            if (data1.error || data2.error || data3.error || data4.error) {
                alert('Error: ' + (data1.error || data2.error || data3.error || data4.error));
                return;
            }
            
            // Combinar los datos
            const dataCombinada = {
                matriz_1: data1.matriz_1,
                matriz_2: data1.matriz_2,
                matriz_final: data2,
                topicos: data3,
                metricas: data4
            };
            
            // Mostrar resultados
            mostrarMatrices(dataCombinada);
            
            // Animar aparición
            resultadosDiv.classList.remove('hidden');
            setTimeout(() => {
                resultadosDiv.classList.remove('opacity-0');
                resultadosDiv.classList.add('opacity-100');
            }, 10);
            
            // Ocultar botón con animación
            botonMostrar.classList.add('opacity-0', 'scale-0');
            setTimeout(() => {
                botonMostrar.style.display = 'none';
            }, 300);
            
        } catch (error) {
            console.error('Error:', error);
            alert('Error al cargar los datos: ' + error.message);
        } finally {
            botonMostrar.disabled = false;
        }
    });
});

function mostrarMatrices(data) {
    const resultadosDiv = document.getElementById('resultados');
    
    const html = `
        <div class="border-t-2 border-purple-200 pt-8">
            <h3 class="text-2xl font-bold text-gray-800 mb-6 flex items-center animate-fade-in">
                <svg class="w-8 h-8 text-purple-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                </svg>
                Resultados del Análisis LDA
            </h3>

            <!-- Métricas del Modelo -->
            <div class="mb-8 bg-gradient-to-br from-yellow-50 to-orange-50 rounded-xl p-6 border-2 border-yellow-300 animate-fade-in">
                <h4 class="text-xl font-bold text-orange-800 mb-4 flex items-center">
                    <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path>
                    </svg>
                    Métricas del Modelo
                </h4>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="bg-white rounded-lg p-4 shadow-sm">
                        <p class="text-sm text-gray-600 mb-1">Entropía</p>
                        <p class="text-2xl font-bold text-orange-700">${data.metricas.entropia.toFixed(6)}</p>
                    </div>
                    <div class="bg-white rounded-lg p-4 shadow-sm">
                        <p class="text-sm text-gray-600 mb-1">Perplejidad</p>
                        <p class="text-2xl font-bold text-orange-700">${data.metricas.perplexity.toFixed(2)}</p>
                    </div>
                </div>
                <p class="text-gray-600 text-sm mt-3">
                    Iteraciones: ${data.metricas.repeticiones} | La perplejidad más baja indica mejor ajuste del modelo
                </p>
            </div>
            
            <!-- Tópicos Identificados -->
            <div class="mb-8 bg-gradient-to-br from-yellow-50 to-orange-50 rounded-xl p-6 border-2 border-yellow-200 animate-slide-up" style="animation-delay: 0.1s;">
                <h4 class="text-2xl font-bold text-orange-800 mb-6 flex items-center">
                    <svg class="w-7 h-7 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"></path>
                    </svg>
                    Tópicos Identificados (Top 20 Palabras)
                </h4>
                
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    ${generarTopicos(data.topicos)}
                </div>
            </div>

            <!-- Matriz 1 -->
            <div class="mb-8 bg-gradient-to-br from-purple-50 to-indigo-50 rounded-xl p-6 border-2 border-purple-200 animate-slide-up" style="animation-delay: 0.2s;">
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
            <div class="mb-8 bg-gradient-to-br from-indigo-50 to-pink-50 rounded-xl p-6 border-2 border-indigo-200 animate-slide-up" style="animation-delay: 0.3s;">
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

            <!-- Matriz Final -->
            <div class="mb-8 bg-gradient-to-br from-green-50 to-teal-50 rounded-xl p-6 border-2 border-green-200 animate-slide-up" style="animation-delay: 0.4s;">
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

function generarTopicos(topicosData) {
    const colores = [
        { bg: 'from-purple-50 to-purple-100', border: 'border-purple-300', text: 'text-purple-800', badge: 'bg-purple-500', tag: 'text-purple-700' },
        { bg: 'from-indigo-50 to-indigo-100', border: 'border-indigo-300', text: 'text-indigo-800', badge: 'bg-indigo-500', tag: 'text-indigo-700' },
        { bg: 'from-pink-50 to-pink-100', border: 'border-pink-300', text: 'text-pink-800', badge: 'bg-pink-500', tag: 'text-pink-700' },
        { bg: 'from-blue-50 to-blue-100', border: 'border-blue-300', text: 'text-blue-800', badge: 'bg-blue-500', tag: 'text-blue-700' },
        { bg: 'from-green-50 to-green-100', border: 'border-green-300', text: 'text-green-800', badge: 'bg-green-500', tag: 'text-green-700' },
        { bg: 'from-red-50 to-red-100', border: 'border-red-300', text: 'text-red-800', badge: 'bg-red-500', tag: 'text-red-700' },
        { bg: 'from-yellow-50 to-yellow-100', border: 'border-yellow-300', text: 'text-yellow-800', badge: 'bg-yellow-500', tag: 'text-yellow-700' },
        { bg: 'from-teal-50 to-teal-100', border: 'border-teal-300', text: 'text-teal-800', badge: 'bg-teal-500', tag: 'text-teal-700' }
    ];
    
    let html = '';
    const topicosAMostrar = topicosData.topicos.slice(0, 12);
    
    topicosAMostrar.forEach((topico, index) => {
        const color = colores[index % colores.length];
        const palabrasMostrar = topico.top_palabras.slice(0, 10);
        
        html += `
            <div class="bg-gradient-to-br ${color.bg} rounded-xl p-4 border-2 ${color.border} 
                        hover:shadow-xl transition-all duration-300 cursor-pointer 
                        transform hover:-translate-y-1 hover:scale-105
                        animate-fade-in-up"
                 style="animation-delay: ${index * 0.05}s;"
                 onclick="mostrarDetalleTopico(${topico.topico})">
                <div class="mb-3">
                    <div class="flex items-center justify-between mb-1">
                        <h5 class="text-lg font-bold ${color.text} truncate pr-2">
                            ${topico.nombre || 'Tópico ' + topico.topico}
                        </h5>
                        <span class="${color.badge} text-white text-xs font-semibold px-2 py-1 rounded-full">
                            ${palabrasMostrar[0].probabilidad.toFixed(3)}
                        </span>
                    </div>
                    <p class="text-xs text-gray-500">ID: ${topico.topico}</p>
                </div>
                <div class="flex flex-wrap gap-2 mb-2">
                    ${palabrasMostrar.map(p => `
                        <span class="bg-white ${color.tag} text-xs px-2 py-1 rounded-full 
                                     shadow-sm hover:shadow-md transition-all duration-200
                                     hover:scale-110" 
                              title="Probabilidad: ${p.probabilidad.toFixed(4)}">
                            ${p.palabra}
                        </span>
                    `).join('')}
                </div>
                <p class="text-xs text-gray-500 mt-2 text-right italic flex items-center justify-end gap-1">
                    <span>👆</span>
                    <span>Click para ver las 20 palabras</span>
                </p>
            </div>
        `;
    });
    
    return html;
}

function mostrarDetalleTopico(topicoId) {
    fetch('/api/topicosfinal')
        .then(response => response.json())
        .then(data => {
            const topico = data.topicos.find(t => t.topico === topicoId);
            if (topico) {
                const modal = `
                    <div id="modal-topico" 
                         class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4
                                animate-fade-in"
                         onclick="cerrarModal(event)">
                        <div class="bg-white rounded-2xl p-8 max-w-3xl w-full max-h-[90vh] overflow-y-auto 
                                    shadow-2xl transform animate-scale-in" 
                             onclick="event.stopPropagation()">
                            
                            <!-- Header del modal -->
                            <div class="flex justify-between items-start mb-6 pb-4 border-b-2 border-purple-100">
                                <div class="flex-1">
                                    <h3 class="text-3xl font-bold text-transparent bg-clip-text 
                                               bg-gradient-to-r from-purple-600 to-indigo-600 mb-2">
                                        ${topico.nombre || 'Tópico ' + topico.topico}
                                    </h3>
                                    <p class="text-sm text-gray-500 flex items-center gap-2">
                                        <span class="bg-purple-100 text-purple-700 px-2 py-1 rounded-full font-semibold">
                                            ID: ${topico.topico}
                                        </span>
                                        <span>•</span>
                                        <span>Top 20 Palabras más relevantes</span>
                                    </p>
                                </div>
                                <button onclick="document.getElementById('modal-topico').remove()" 
                                        class="text-gray-400 hover:text-gray-600 hover:bg-gray-100 
                                               rounded-full w-10 h-10 flex items-center justify-center
                                               text-2xl font-light ml-4 transition-all duration-200
                                               hover:rotate-90">
                                    ×
                                </button>
                            </div>
                            
                            <!-- Lista de palabras con gradientes -->
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                                ${topico.top_palabras.map((p, i) => {
                                    const gradiente = i < 5 ? 'from-purple-100 to-purple-200 border-purple-300' :
                                                     i < 10 ? 'from-indigo-100 to-indigo-200 border-indigo-300' :
                                                     i < 15 ? 'from-blue-100 to-blue-200 border-blue-300' :
                                                     'from-gray-100 to-gray-200 border-gray-300';
                                    
                                    const textColor = i < 5 ? 'text-purple-800' :
                                                     i < 10 ? 'text-indigo-800' :
                                                     i < 15 ? 'text-blue-800' :
                                                     'text-gray-800';
                                    
                                    return `
                                        <div class="flex justify-between items-center 
                                                    bg-gradient-to-r ${gradiente} rounded-lg p-3 border-2 
                                                    hover:shadow-lg transition-all duration-200
                                                    transform hover:scale-105
                                                    animate-fade-in"
                                             style="animation-delay: ${i * 0.02}s;">
                                            <span class="font-semibold ${textColor}">
                                                <span class="inline-block w-8 text-center font-bold">${i + 1}.</span>
                                                ${p.palabra}
                                            </span>
                                            <span class="text-sm text-gray-600 font-mono bg-white 
                                                         px-2 py-1 rounded shadow-sm">
                                                ${p.probabilidad.toFixed(4)}
                                            </span>
                                        </div>
                                    `;
                                }).join('')}
                            </div>
                            
                            <!-- Footer del modal -->
                            <div class="mt-6 pt-6 border-t border-gray-200">
                                <div class="flex items-center justify-center gap-2 text-sm text-gray-600">
                                    <svg class="w-5 h-5 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                    </svg>
                                    <span>Las probabilidades indican la relevancia de cada palabra en este tópico</span>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                document.body.insertAdjacentHTML('beforeend', modal);
            }
        })
        .catch(error => {
            console.error('Error al cargar detalles del tópico:', error);
            alert('Error al cargar los detalles del tópico');
        });
}

function cerrarModal(event) {
    if (event.target.id === 'modal-topico') {
        const modal = event.target;
        modal.classList.add('animate-fade-out');
        setTimeout(() => modal.remove(), 200);
    }
}

function generarTablaMatriz(datos, labelFila, labelColumna, limitarColumnas = false) {
    const filas = datos.length;
    const columnas = limitarColumnas ? Math.min(10, datos[0].length) : datos[0].length;
    
    let html = '<table class="min-w-full bg-white rounded-lg overflow-hidden shadow-md text-sm">';
    
    // Header
    html += '<thead class="bg-gradient-to-r from-purple-500 to-indigo-500 text-white">';
    html += '<tr><th class="px-4 py-3 font-semibold">' + labelFila + '</th>';
    for (let j = 0; j < columnas; j++) {
        html += `<th class="px-4 py-3 font-semibold">${labelColumna} ${j}</th>`;
    }
    html += '</tr></thead>';
    
    // Body
    html += '<tbody>';
    for (let i = 0; i < Math.min(10, filas); i++) {
        html += `<tr class="${i % 2 === 0 ? 'bg-gray-50' : 'bg-white'} hover:bg-purple-50 transition-colors">`;
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