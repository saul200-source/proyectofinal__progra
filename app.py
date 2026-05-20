from flask import Flask, jsonify, request, render_template_string
import json

app = Flask(__name__)

# Nombre del archivo de base de datos
ARCHIVO_DB = 'database.json'

# ============ LÍMITES DEL MERCADO ============
LIMITES_SECTOR = {
    1: {"nombre": "Frutas y Verduras", "maximo": 8, "ocupados": 0},
    2: {"nombre": "Carnes", "maximo": 8, "ocupados": 0},
    3: {"nombre": "Textiles", "maximo": 4, "ocupados": 0}
}
TOTAL_MAXIMO_LOCALES = 20

# Tamaño base del local (ancho fijo 5m, largo variable)
ANCHO_FIJO = 5  # 5 metros fijos de ancho

# ============ HTML DE LA INTERFAZ WEB ============
INTERFAZ_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>MercatoLogic - Administración</title>
    <meta charset="UTF-8">
    <style>
        * { box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Arial, sans-serif; 
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { 
            max-width: 1200px; 
            margin: auto; 
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 { 
            color: #333; 
            text-align: center;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }
        h2 { 
            color: #667eea; 
            font-size: 1.3em;
            margin-top: 25px;
        }
        input, select, button { 
            display: block; 
            width: 100%; 
            padding: 12px; 
            margin: 8px 0;
            font-size: 16px;
            border: 1px solid #ddd;
            border-radius: 8px;
        }
        button { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; 
            cursor: pointer; 
            font-weight: bold;
            border: none;
            transition: transform 0.2s;
        }
        button:hover {
            transform: scale(1.02);
        }
        .btn-ver {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            margin: 5px 0;
        }
        .btn-menu {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }
        .btn-aumentar {
            background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
        }
        .btn-reducir {
            background: linear-gradient(135deg, #e67e22 0%, #f39c12 100%);
        }
        .btn-eliminar {
            background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        }
        hr { 
            margin: 25px 0; 
            border: none;
            border-top: 2px dashed #ddd;
        }
        .badge {
            background: #667eea;
            color: white;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 12px;
            display: inline-block;
            margin-bottom: 10px;
        }
        .badge-limite {
            background: #e74c3c;
            margin-left: 5px;
        }
        .badge-modulo {
            background: #27ae60;
        }
        .grupo-botones {
            display: flex;
            gap: 10px;
        }
        .grupo-botones button {
            flex: 1;
        }
        
        /* Estilos para la tabla */
        .tabla-datos {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            font-size: 14px;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .tabla-datos th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }
        .tabla-datos td {
            border: 1px solid #ddd;
            padding: 10px;
            text-align: left;
            background-color: white;
        }
        .tabla-datos tr:nth-child(even) td {
            background-color: #f9f9f9;
        }
        .tabla-datos tr:hover td {
            background-color: #f0f0f0;
        }
        .categoria-frutas { color: #27ae60; font-weight: bold; }
        .categoria-carnes { color: #e74c3c; font-weight: bold; }
        .categoria-textiles { color: #8e44ad; font-weight: bold; }
        
        .menu-consultas {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 15px;
            margin-bottom: 20px;
            border: 1px solid #e0e0e0;
        }
        .menu-titulo {
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }
        
        /* Indicadores de capacidad */
        .capacidad-container {
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        .capacidad-card {
            flex: 1;
            background: #f8f9fa;
            border-radius: 10px;
            padding: 12px;
            text-align: center;
            border-left: 4px solid;
        }
        .capacidad-card.frutas { border-left-color: #27ae60; }
        .capacidad-card.carnes { border-left-color: #e74c3c; }
        .capacidad-card.textiles { border-left-color: #8e44ad; }
        .capacidad-card.total { border-left-color: #667eea; background: #e8eaf6; }
        .capacidad-numero {
            font-size: 24px;
            font-weight: bold;
        }
        .capacidad-label {
            font-size: 12px;
            color: #666;
        }
        .capacidad-alerta {
            color: #e74c3c;
            font-size: 12px;
            margin-top: 5px;
        }
        
        /* Notificación tipo nubecita */
        .notificacion {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: white;
            border-radius: 20px;
            padding: 15px 25px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.3);
            z-index: 1000;
            animation: slideIn 0.3s ease;
            border-left: 5px solid #667eea;
            max-width: 350px;
        }
        .notificacion.exito { border-left-color: #27ae60; }
        .notificacion.error { border-left-color: #e74c3c; }
        .notificacion.alerta { border-left-color: #f39c12; }
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        .notificacion-titulo {
            font-weight: bold;
            margin-bottom: 5px;
        }
        .notificacion-mensaje {
            font-size: 14px;
            color: #555;
        }
        .notificacion-cerrar {
            float: right;
            cursor: pointer;
            color: #999;
        }
        
        /* Selector de vendedor */
        .selector-vendedor {
            background: #f0f0f0;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
        }
        .info-modulo {
            background: #e8f5e9;
            padding: 10px;
            border-radius: 8px;
            font-size: 14px;
            margin-top: 10px;
        }
        .acciones-modulos {
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }
        .acciones-modulos button {
            flex: 1;
        }
        
        .info-dimensiones {
            background: #fff3e0;
            padding: 10px;
            border-radius: 8px;
            font-size: 13px;
            margin-top: 10px;
            border-left: 4px solid #f39c12;
        }
        
        .tabla-container {
            overflow-x: auto;
            margin-top: 15px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏪 MercatoLogic API</h1>
        <div style="text-align: center; margin-bottom: 20px;">
            <span class="badge">Sistema de Gestión de Mercados</span>
            <span class="badge badge-limite">Máximo 20 locales</span>
            <span class="badge badge-modulo">📐 Ancho fijo: 5m | Largo: 5m, 10m, 15m, 20m</span>
        </div>
        
        <!-- Indicadores de capacidad -->
        <div class="capacidad-container" id="capacidad-container">
            <!-- Se llena con JavaScript -->
        </div>
        
        <!-- ============ MENÚ DE CONSULTAS ============ -->
        <div class="menu-consultas">
            <div class="menu-titulo">📊 MENÚ DE CONSULTAS</div>
            <div class="grupo-botones">
                <button class="btn-menu" onclick="verTablaCompleta()">📋 Ver Tabla Completa</button>
                <button class="btn-menu" onclick="verSoloFrutas()">🥬 Frutas y Verduras</button>
                <button class="btn-menu" onclick="verSoloCarnes()">🥩 Carnes</button>
                <button class="btn-menu" onclick="verSoloTextiles()">👕 Textiles</button>
            </div>
        </div>
        
        <!-- Sección donde se muestra la TABLA -->
        <div id="contenedor-tabla" style="display: none;">
            <h2>📋 Información de Puestos</h2>
            <div id="tabla-resultado" class="tabla-container"></div>
        </div>
        
        <hr>
        
        <!-- Sección: Asignar nuevo vendedor -->
        <h2>📝 Asignar nuevo vendedor</h2>
        <select id="id_sector">
            <option value="1">Zona Frutas y Verduras (Máx: 8 locales)</option>
            <option value="2">Zona Carnes (Máx: 8 locales)</option>
            <option value="3">Zona Textiles (Máx: 4 locales)</option>
        </select>
        <input type="text" id="nombre_vendedor" placeholder="Nombre del vendedor">
        <select id="cantidad_modulos">
            <option value="1">1 módulo - 5m ancho x 5m largo (25m²)</option>
            <option value="2">2 módulos - 5m ancho x 10m largo (50m²)</option>
            <option value="3">3 módulos - 5m ancho x 15m largo (75m²)</option>
            <option value="4">4 módulos - 5m ancho x 20m largo (100m²)</option>
        </select>
        <div class="info-dimensiones">
            💡 Nota: El ancho de todos los locales es FIJO de 5 metros. El largo varía según los módulos (cada módulo = 5m de largo).
        </div>
        <button onclick="asignarVendedor()">➕ Asignar Vendedor</button>

        <!-- Sección: Gestionar módulos de vendedor -->
        <hr>
        <h2>📦 Gestionar módulos de un vendedor</h2>
        <div class="selector-vendedor">
            <label>Seleccionar vendedor:</label>
            <select id="select_vendedor" onchange="cargarInfoVendedor()">
                <option value="">-- Seleccione un vendedor --</option>
            </select>
            <div id="info_vendedor" class="info-modulo" style="display: none;"></div>
        </div>
        
        <div class="acciones-modulos">
            <button class="btn-aumentar" onclick="aumentarModulos()">➕ Aumentar 1 módulo</button>
            <button class="btn-reducir" onclick="reducirModulos()">➖ Reducir 1 módulo</button>
            <button class="btn-eliminar" onclick="eliminarVendedor()">🗑️ Eliminar vendedor completo</button>
        </div>
        
        <!-- Sección: Información extra -->
        <hr>
        <div class="info-dimensiones">
            <strong>📐 Esquema de dimensiones:</strong><br>
            • 1 módulo → 5m (ancho) x 5m (largo) = 25m²<br>
            • 2 módulos → 5m (ancho) x 10m (largo) = 50m²<br>
            • 3 módulos → 5m (ancho) x 15m (largo) = 75m²<br>
            • 4 módulos → 5m (ancho) x 20m (largo) = 100m²<br>
            <strong>⚠️ Máximo 4 módulos por vendedor.</strong>
        </div>
    </div>

    <script>
        const API_URL = "http://localhost:5001/api";

        function mostrarNotificacion(mensaje, tipo = 'exito') {
            const notifAnterior = document.querySelector('.notificacion');
            if (notifAnterior) notifAnterior.remove();
            
            const notif = document.createElement('div');
            notif.className = `notificacion ${tipo}`;
            let titulo = '';
            if (tipo === 'exito') titulo = '✅ Éxito';
            else if (tipo === 'error') titulo = '❌ Error';
            else titulo = '⚠️ Alerta';
            
            notif.innerHTML = `
                <span class="notificacion-cerrar" onclick="this.parentElement.remove()">✖</span>
                <div class="notificacion-titulo">${titulo}</div>
                <div class="notificacion-mensaje">${mensaje}</div>
            `;
            document.body.appendChild(notif);
            
            setTimeout(() => {
                if (notif) notif.remove();
            }, 10000);
        }
        
        async function actualizarCapacidad() {
            try {
                const response = await fetch(API_URL + '/capacidad');
                const capacidad = await response.json();
                
                const container = document.getElementById('capacidad-container');
                container.innerHTML = `
                    <div class="capacidad-card frutas">
                        <div class="capacidad-numero">${capacidad.frutas_ocupados}/${capacidad.frutas_max}</div>
                        <div class="capacidad-label">🥬 Frutas y Verduras</div>
                        ${capacidad.frutas_ocupados >= capacidad.frutas_max ? '<div class="capacidad-alerta">⚠️ Cupo lleno</div>' : ''}
                    </div>
                    <div class="capacidad-card carnes">
                        <div class="capacidad-numero">${capacidad.carnes_ocupados}/${capacidad.carnes_max}</div>
                        <div class="capacidad-label">🥩 Carnes</div>
                        ${capacidad.carnes_ocupados >= capacidad.carnes_max ? '<div class="capacidad-alerta">⚠️ Cupo lleno</div>' : ''}
                    </div>
                    <div class="capacidad-card textiles">
                        <div class="capacidad-numero">${capacidad.textiles_ocupados}/${capacidad.textiles_max}</div>
                        <div class="capacidad-label">👕 Textiles</div>
                        ${capacidad.textiles_ocupados >= capacidad.textiles_max ? '<div class="capacidad-alerta">⚠️ Cupo lleno</div>' : ''}
                    </div>
                    <div class="capacidad-card total">
                        <div class="capacidad-numero">${capacidad.total_ocupados}/${capacidad.total_max}</div>
                        <div class="capacidad-label">🏪 Total Locales</div>
                        ${capacidad.total_ocupados >= capacidad.total_max ? '<div class="capacidad-alerta">⚠️ Mercado lleno</div>' : ''}
                    </div>
                `;
            } catch (error) {
                console.error("Error al cargar capacidad");
            }
        }
        
        async function cargarListaVendedores() {
            try {
                const response = await fetch(API_URL + '/vendedores');
                const vendedores = await response.json();
                
                const select = document.getElementById('select_vendedor');
                select.innerHTML = '<option value="">-- Seleccione un vendedor --</option>';
                
                for (let v of vendedores) {
                    select.innerHTML += `<option value="${v.id}">${v.nombre} - ${v.sector} (${v.modulos} módulos)</option>`;
                }
            } catch (error) {
                console.error("Error al cargar vendedores");
            }
        }
        
        async function cargarInfoVendedor() {
            const id = document.getElementById('select_vendedor').value;
            if (!id) {
                document.getElementById('info_vendedor').style.display = 'none';
                return;
            }
            try {
                const response = await fetch(API_URL + '/vendedor/' + id);
                const v = await response.json();
                const infoDiv = document.getElementById('info_vendedor');
                infoDiv.innerHTML = `
                    <strong>📋 Información del vendedor:</strong><br>
                    👤 Nombre: ${v.nombre}<br>
                    📍 Sector: ${v.sector}<br>
                    📦 Módulos actuales: ${v.modulos}<br>
                    📐 Dimensiones: ${v.ancho}m (ancho) x ${v.largo}m (largo) = ${v.metros_cuadrados}m²<br>
                    🆔 IDs de puestos: ${v.ids.join(', ')}
                `;
                infoDiv.style.display = 'block';
            } catch (error) {
                console.error("Error al cargar info");
            }
        }
        
        function calcularDimensionesPorModulos(modulos) {
            const ancho = 5;
            const largo = modulos * 5;
            return { ancho, largo, metros_cuadrados: ancho * largo };
        }
        
        function mostrarTabla(puestos, titulo) {
            const contenedor = document.getElementById('contenedor-tabla');
            const tablaDiv = document.getElementById('tabla-resultado');
            contenedor.style.display = 'block';
            
            if (puestos.length === 0) {
                tablaDiv.innerHTML = '<p style="text-align:center; padding:20px;">No hay puestos en esta categoría.</p>';
                return;
            }
            
            let html = `<h3 style="margin-bottom:10px;">${titulo}</h3>`;
            html += `<table class="tabla-datos">`;
            html += `<thead>`;
            html += `<tr>
                        <th>ID(s)</th>
                        <th>Vendedor</th>
                        <th>Giro</th>
                        <th>Sector</th>
                        <th>Módulos</th>
                        <th>Espacio (m²)</th>
                        <th>Dimensiones</th>
                      </tr>`;
            html += `</thead><tbody>`;
            
            const vendedoresMap = new Map();
            for (let puesto of puestos) {
                if (!vendedoresMap.has(puesto.nombre_vendedor)) {
                    vendedoresMap.set(puesto.nombre_vendedor, []);
                }
                vendedoresMap.get(puesto.nombre_vendedor).push(puesto);
            }
            
            for (let [nombre, puestosVendedor] of vendedoresMap) {
                const primerPuesto = puestosVendedor[0];
                let ids = puestosVendedor.map(p => p.id).join(', ');
                let modulos = puestosVendedor.length;
                let dimensiones = `${primerPuesto.dimensiones.ancho}m x ${primerPuesto.dimensiones.largo}m`;
                
                let claseColor = "";
                let giroTexto = "";
                if (primerPuesto.giro_negocio === 'frutas_verduras') {
                    claseColor = "categoria-frutas";
                    giroTexto = "🥬 Frutas y Verduras";
                } else if (primerPuesto.giro_negocio === 'carnes') {
                    claseColor = "categoria-carnes";
                    giroTexto = "🥩 Carnes";
                } else if (primerPuesto.giro_negocio === 'textiles') {
                    claseColor = "categoria-textiles";
                    giroTexto = "👕 Textiles";
                }
                
                html += `<tr>
                            <td><strong>${ids}</strong></td>
                            <td><strong>${nombre}</strong></td>
                            <td class="${claseColor}">${giroTexto}</td>
                            <td>${primerPuesto.sector_nombre || primerPuesto.id_sector}</td>
                            <td>${modulos} módulo(s)</td>
                            <td>${primerPuesto.dimensiones.metros_cuadrados} m²</td>
                            <td>${dimensiones}</td>
                          </tr>`;
            }
            html += `</tbody></table>`;
            tablaDiv.innerHTML = html;
        }
        
        async function obtenerTodosLosPuestos() {
            try {
                const [puestosRes, sectoresRes] = await Promise.all([
                    fetch(API_URL + '/puestos'),
                    fetch(API_URL + '/sectores')
                ]);
                const puestos = await puestosRes.json();
                const sectores = await sectoresRes.json();
                
                for (let puesto of puestos) {
                    const sector = sectores.find(s => s.id === puesto.id_sector);
                    puesto.sector_nombre = sector ? sector.nombre : "Desconocido";
                }
                return puestos;
            } catch (error) {
                mostrarNotificacion("Error al cargar los datos", "error");
                return [];
            }
        }
        
        async function verTablaCompleta() {
            const puestos = await obtenerTodosLosPuestos();
            mostrarTabla(puestos, "📋 TODOS LOS PUESTOS DEL MERCADO");
            mostrarNotificacion("Tabla completa cargada", "exito");
        }
        
        async function verSoloFrutas() {
            const puestos = await obtenerTodosLosPuestos();
            const filtrados = puestos.filter(p => p.giro_negocio === 'frutas_verduras');
            mostrarTabla(filtrados, "🥬 PUESTOS DE FRUTAS Y VERDURAS");
            mostrarNotificacion(`Se encontraron ${filtrados.length} puestos de Frutas y Verduras`, "exito");
        }
        
        async function verSoloCarnes() {
            const puestos = await obtenerTodosLosPuestos();
            const filtrados = puestos.filter(p => p.giro_negocio === 'carnes');
            mostrarTabla(filtrados, "🥩 PUESTOS DE CARNES");
            mostrarNotificacion(`Se encontraron ${filtrados.length} puestos de Carnes`, "exito");
        }
        
        async function verSoloTextiles() {
            const puestos = await obtenerTodosLosPuestos();
            const filtrados = puestos.filter(p => p.giro_negocio === 'textiles');
            mostrarTabla(filtrados, "👕 PUESTOS DE TEXTILES");
            mostrarNotificacion(`Se encontraron ${filtrados.length} puestos de Textiles`, "exito");
        }

        async function asignarVendedor() {
            const modulos = parseInt(document.getElementById('cantidad_modulos').value);
            const dimensiones = calcularDimensionesPorModulos(modulos);
            const idSector = parseInt(document.getElementById('id_sector').value);
            
            let giro = "";
            if (idSector === 1) giro = "frutas_verduras";
            else if (idSector === 2) giro = "carnes";
            else giro = "textiles";
            
            const data = {
                id_sector: idSector,
                nombre_vendedor: document.getElementById('nombre_vendedor').value,
                giro_negocio: giro,
                modulos: modulos,
                ancho: dimensiones.ancho,
                largo: dimensiones.largo
            };

            if (!data.nombre_vendedor) {
                mostrarNotificacion("Por favor ingresa el nombre del vendedor", "error");
                return;
            }

            try {
                const response = await fetch(API_URL + '/asignacion/puesto', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                
                if (response.ok) {
                    mostrarNotificacion(result.mensaje, "exito");
                    document.getElementById('nombre_vendedor').value = '';
                    await actualizarCapacidad();
                    await cargarListaVendedores();
                    setTimeout(() => verTablaCompleta(), 1000);
                } else {
                    mostrarNotificacion(result.error, "error");
                }
            } catch (error) {
                mostrarNotificacion("Error de conexión con el servidor", "error");
            }
        }
        
        async function aumentarModulos() {
            const id = document.getElementById('select_vendedor').value;
            if (!id) {
                mostrarNotificacion("Por favor selecciona un vendedor", "error");
                return;
            }
            
            try {
                const response = await fetch(API_URL + '/vendedor/' + id + '/aumentar', {
                    method: 'PUT'
                });
                const result = await response.json();
                
                if (response.ok) {
                    mostrarNotificacion(result.mensaje, "exito");
                    await cargarListaVendedores();
                    await actualizarCapacidad();
                    await cargarInfoVendedor();
                    setTimeout(() => verTablaCompleta(), 1000);
                } else {
                    mostrarNotificacion(result.error, "error");
                }
            } catch (error) {
                mostrarNotificacion("Error de conexión con el servidor", "error");
            }
        }
        
        async function reducirModulos() {
            const id = document.getElementById('select_vendedor').value;
            if (!id) {
                mostrarNotificacion("Por favor selecciona un vendedor", "error");
                return;
            }
            
            try {
                const response = await fetch(API_URL + '/vendedor/' + id + '/reducir', {
                    method: 'PUT'
                });
                const result = await response.json();
                
                if (response.ok) {
                    mostrarNotificacion(result.mensaje, "exito");
                    await cargarListaVendedores();
                    await actualizarCapacidad();
                    await cargarInfoVendedor();
                    setTimeout(() => verTablaCompleta(), 1000);
                } else {
                    mostrarNotificacion(result.error, "error");
                }
            } catch (error) {
                mostrarNotificacion("Error de conexión con el servidor", "error");
            }
        }
        
        async function eliminarVendedor() {
            const id = document.getElementById('select_vendedor').value;
            if (!id) {
                mostrarNotificacion("Por favor selecciona un vendedor", "error");
                return;
            }
            
            if (confirm("⚠️ ¿Estás seguro de eliminar COMPLETAMENTE a este vendedor? Esta acción no se puede deshacer.")) {
                try {
                    const response = await fetch(API_URL + '/vendedor/' + id + '/eliminar', {
                        method: 'DELETE'
                    });
                    const result = await response.json();
                    
                    if (response.ok) {
                        mostrarNotificacion(result.mensaje, "exito");
                        await cargarListaVendedores();
                        await actualizarCapacidad();
                        document.getElementById('select_vendedor').value = "";
                        document.getElementById('info_vendedor').style.display = 'none';
                        setTimeout(() => verTablaCompleta(), 1000);
                    } else {
                        mostrarNotificacion(result.error, "error");
                    }
                } catch (error) {
                    mostrarNotificacion("Error de conexión con el servidor", "error");
                }
            }
        }
        
        // Inicialización
        actualizarCapacidad();
        cargarListaVendedores();
        setInterval(actualizarCapacidad, 5000);
        setInterval(cargarListaVendedores, 5000);
    </script>
</body>
</html>
'''

# ============ FUNCIONES PARA MANEJAR LA BASE DE DATOS ============

def leer_datos():
    with open(ARCHIVO_DB, 'r', encoding='utf-8') as archivo:
        return json.load(archivo)

def guardar_datos(datos):
    with open(ARCHIVO_DB, 'w', encoding='utf-8') as archivo:
        json.dump(datos, archivo, indent=2, ensure_ascii=False)

def contar_puestos_por_sector():
    datos = leer_datos()
    conteo = {1: 0, 2: 0, 3: 0}
    for puesto in datos['puestos']:
        if puesto['id_sector'] in conteo:
            conteo[puesto['id_sector']] += 1
    return conteo

def verificar_cupo_disponible(id_sector, modulos_necesarios):
    conteo = contar_puestos_por_sector()
    limite = LIMITES_SECTOR[id_sector]["maximo"]
    disponibles = limite - conteo[id_sector]
    return disponibles >= modulos_necesarios

# ============ RUTAS DE LA API ============

@app.route('/')
def interfaz():
    return render_template_string(INTERFAZ_HTML)

@app.route('/api/capacidad', methods=['GET'])
def obtener_capacidad():
    conteo = contar_puestos_por_sector()
    total_ocupados = sum(conteo.values())
    
    return jsonify({
        "frutas_max": LIMITES_SECTOR[1]["maximo"],
        "frutas_ocupados": conteo[1],
        "carnes_max": LIMITES_SECTOR[2]["maximo"],
        "carnes_ocupados": conteo[2],
        "textiles_max": LIMITES_SECTOR[3]["maximo"],
        "textiles_ocupados": conteo[3],
        "total_max": TOTAL_MAXIMO_LOCALES,
        "total_ocupados": total_ocupados
    })

@app.route('/api/vendedores', methods=['GET'])
def listar_vendedores():
    datos = leer_datos()
    vendedores = []
    vendedores_dict = {}
    
    for puesto in datos['puestos']:
        nombre = puesto['nombre_vendedor']
        if nombre not in vendedores_dict:
            sector_nombre = ""
            for s in datos['sectores']:
                if s['id'] == puesto['id_sector']:
                    sector_nombre = s['nombre']
                    break
            
            vendedores_dict[nombre] = {
                "id": puesto['id'],
                "nombre": nombre,
                "sector": sector_nombre,
                "modulos": 1,
                "ids": [puesto['id']]
            }
        else:
            vendedores_dict[nombre]["modulos"] += 1
            vendedores_dict[nombre]["ids"].append(puesto['id'])
    
    for v in vendedores_dict.values():
        vendedores.append(v)
    
    return jsonify(vendedores)

@app.route('/api/vendedor/<int:id>', methods=['GET'])
def obtener_vendedor_por_id(id):
    datos = leer_datos()
    puesto = next((p for p in datos['puestos'] if p['id'] == id), None)
    
    if not puesto:
        return jsonify({"error": "Vendedor no encontrado"}), 404
    
    puestos_vendedor = [p for p in datos['puestos'] if p['nombre_vendedor'] == puesto['nombre_vendedor']]
    
    sector_nombre = ""
    for s in datos['sectores']:
        if s['id'] == puesto['id_sector']:
            sector_nombre = s['nombre']
            break
    
    return jsonify({
        "id": id,
        "nombre": puesto['nombre_vendedor'],
        "sector": sector_nombre,
        "modulos": len(puestos_vendedor),
        "ids": [p['id'] for p in puestos_vendedor],
        "ancho": puesto['dimensiones']['ancho'],
        "largo": puesto['dimensiones']['largo'],
        "metros_cuadrados": puesto['dimensiones']['metros_cuadrados']
    })

@app.route('/api/vendedor/<int:id>/aumentar', methods=['PUT'])
def aumentar_modulos(id):
    datos = leer_datos()
    puesto = next((p for p in datos['puestos'] if p['id'] == id), None)
    
    if not puesto:
        return jsonify({"error": "Vendedor no encontrado"}), 404
    
    puestos_vendedor = [p for p in datos['puestos'] if p['nombre_vendedor'] == puesto['nombre_vendedor']]
    modulos_actuales = len(puestos_vendedor)
    
    if modulos_actuales >= 4:
        return jsonify({"error": "No se puede aumentar. Máximo 4 módulos por vendedor"}), 400
    
    if not verificar_cupo_disponible(puesto['id_sector'], modulos_actuales + 1):
        limite = LIMITES_SECTOR[puesto['id_sector']]["maximo"]
        conteo = contar_puestos_por_sector()
        disponibles = limite - conteo[puesto['id_sector']]
        return jsonify({"error": f"No hay espacio disponible. Solo quedan {disponibles} espacios en este sector"}), 400
    
    ultimo_id = max([p['id'] for p in datos['puestos']])
    nuevo_id = ultimo_id + 1
    
    nuevos_modulos = modulos_actuales + 1
    ancho = 5
    largo = nuevos_modulos * 5
    
    nuevo_puesto = {
        "id": nuevo_id,
        "id_sector": puesto['id_sector'],
        "nombre_vendedor": puesto['nombre_vendedor'],
        "giro_negocio": puesto['giro_negocio'],
        "dimensiones": {
            "ancho": ancho,
            "largo": largo,
            "metros_cuadrados": round(ancho * largo, 2)
        }
    }
    datos['puestos'].append(nuevo_puesto)
    
    for p in datos['puestos']:
        if p['nombre_vendedor'] == puesto['nombre_vendedor']:
            p['dimensiones']['ancho'] = ancho
            p['dimensiones']['largo'] = largo
            p['dimensiones']['metros_cuadrados'] = round(ancho * largo, 2)
    
    guardar_datos(datos)
    
    return jsonify({
        "mensaje": f"✅ Se agregó 1 módulo a {puesto['nombre_vendedor']}. Ahora tiene {nuevos_modulos} módulos. Nuevo ID: {nuevo_id}",
        "nuevos_modulos": nuevos_modulos,
        "nuevas_dimensiones": f"{ancho}m x {largo}m"
    })

@app.route('/api/vendedor/<int:id>/reducir', methods=['PUT'])
def reducir_modulos(id):
    datos = leer_datos()
    puesto = next((p for p in datos['puestos'] if p['id'] == id), None)
    
    if not puesto:
        return jsonify({"error": "Vendedor no encontrado"}), 404
    
    puestos_vendedor = [p for p in datos['puestos'] if p['nombre_vendedor'] == puesto['nombre_vendedor']]
    modulos_actuales = len(puestos_vendedor)
    
    if modulos_actuales <= 1:
        return jsonify({"error": "No se puede reducir. El vendedor ya tiene solo 1 módulo"}), 400
    
    puestos_vendedor.sort(key=lambda x: x['id'])
    puesto_a_eliminar = puestos_vendedor[-1]
    datos['puestos'] = [p for p in datos['puestos'] if p['id'] != puesto_a_eliminar['id']]
    
    nuevos_modulos = modulos_actuales - 1
    ancho = 5
    largo = nuevos_modulos * 5
    
    for p in datos['puestos']:
        if p['nombre_vendedor'] == puesto['nombre_vendedor']:
            p['dimensiones']['ancho'] = ancho
            p['dimensiones']['largo'] = largo
            p['dimensiones']['metros_cuadrados'] = round(ancho * largo, 2)
    
    guardar_datos(datos)
    
    return jsonify({
        "mensaje": f"✅ Se eliminó 1 módulo de {puesto['nombre_vendedor']}. Ahora tiene {nuevos_modulos} módulos",
        "nuevos_modulos": nuevos_modulos,
        "nuevas_dimensiones": f"{ancho}m x {largo}m"
    })

@app.route('/api/vendedor/<int:id>/eliminar', methods=['DELETE'])
def eliminar_vendedor_completo(id):
    datos = leer_datos()
    puesto = next((p for p in datos['puestos'] if p['id'] == id), None)
    
    if not puesto:
        return jsonify({"error": "Vendedor no encontrado"}), 404
    
    nombre_vendedor = puesto['nombre_vendedor']
    puestos_a_eliminar = [p for p in datos['puestos'] if p['nombre_vendedor'] == nombre_vendedor]
    cantidad = len(puestos_a_eliminar)
    
    datos['puestos'] = [p for p in datos['puestos'] if p['nombre_vendedor'] != nombre_vendedor]
    guardar_datos(datos)
    
    return jsonify({
        "mensaje": f"✅ Vendedor '{nombre_vendedor}' eliminado completamente. Se liberaron {cantidad} módulo(s)."
    })

@app.route('/api/sectores', methods=['GET'])
def listar_sectores():
    datos = leer_datos()
    return jsonify(datos['sectores'])

@app.route('/api/puestos', methods=['GET'])
def listar_puestos():
    datos = leer_datos()
    return jsonify(datos['puestos'])

@app.route('/api/asignacion/puesto', methods=['POST'])
def asignar_puesto():
    datos = leer_datos()
    nueva_asignacion = request.json
    
    campos_requeridos = ['id_sector', 'nombre_vendedor', 'giro_negocio', 'modulos']
    for campo in campos_requeridos:
        if campo not in nueva_asignacion:
            return jsonify({"error": f"Falta el campo: {campo}"}), 400
    
    modulos = nueva_asignacion['modulos']
    
    if modulos > 4:
        return jsonify({"error": "Máximo 4 módulos por vendedor"}), 400
    
    sector = next((s for s in datos['sectores'] 
                   if s['id'] == nueva_asignacion['id_sector']), None)
    
    if not sector:
        return jsonify({"error": "El sector no existe"}), 404
    
    if nueva_asignacion['giro_negocio'] != sector['categoria']:
        return jsonify({
            "error": f"❌ El giro no coincide con la zona '{sector['nombre']}'"
        }), 400
    
    if not verificar_cupo_disponible(nueva_asignacion['id_sector'], modulos):
        limite = LIMITES_SECTOR[nueva_asignacion['id_sector']]["maximo"]
        conteo = contar_puestos_por_sector()
        disponibles = limite - conteo[nueva_asignacion['id_sector']]
        return jsonify({
            "error": f"❌ No hay suficiente espacio. Necesitas {modulos} módulo(s), solo hay {disponibles} disponible(s)"
        }), 400
    
    ultimo_id = max([p['id'] for p in datos['puestos']]) if datos['puestos'] else 0
    nuevos_ids = []
    
    for i in range(modulos):
        nuevo_id = ultimo_id + i + 1
        nuevos_ids.append(nuevo_id)
        
        ancho = 5
        largo = modulos * 5
        
        nuevo_puesto = {
            "id": nuevo_id,
            "id_sector": nueva_asignacion['id_sector'],
            "nombre_vendedor": nueva_asignacion['nombre_vendedor'],
            "giro_negocio": nueva_asignacion['giro_negocio'],
            "dimensiones": {
                "ancho": ancho,
                "largo": largo,
                "metros_cuadrados": round(ancho * largo, 2)
            }
        }
        datos['puestos'].append(nuevo_puesto)
    
    guardar_datos(datos)
    
    return jsonify({
        "mensaje": f"✅ {nueva_asignacion['nombre_vendedor']} asignado con {modulos} módulo(s) (IDs: {nuevos_ids})",
        "ids_asignados": nuevos_ids
    }), 201

@app.route('/api/inventario/categorias', methods=['GET'])
def buscar_producto():
    producto = request.args.get('producto', '').lower()
    
    if not producto:
        return jsonify({"error": "Debes especificar un producto"}), 400
    
    datos = leer_datos()
    
    mapa_productos = {
        'manzana': 'frutas_verduras',
        'pera': 'frutas_verduras',
        'platano': 'frutas_verduras',
        'lechuga': 'frutas_verduras',
        'tomate': 'frutas_verduras',
        'res': 'carnes',
        'pollo': 'carnes',
        'cerdo': 'carnes',
        'camisa': 'textiles',
        'pantalon': 'textiles'
    }
    
    if producto in mapa_productos:
        categoria = mapa_productos[producto]
        sector_encontrado = next((s for s in datos['sectores'] if s['categoria'] == categoria), None)
        
        if sector_encontrado:
            return jsonify({
                "producto": producto,
                "categoria": categoria,
                "sector": sector_encontrado['nombre'],
                "ubicacion": f"Zona {sector_encontrado['id']}"
            })
    
    return jsonify({
        "error": f"Producto '{producto}' no encontrado",
        "productos_disponibles": list(mapa_productos.keys())
    }), 404

@app.route('/api/estadisticas', methods=['GET'])
def estadisticas():
    datos = leer_datos()
    
    total_puestos = len(datos['puestos'])
    total_sectores = len(datos['sectores'])
    conteo = contar_puestos_por_sector()
    
    return jsonify({
        "total_sectores": total_sectores,
        "total_puestos": total_puestos,
        "limite_total_mercado": TOTAL_MAXIMO_LOCALES,
        "puestos_por_sector": conteo,
        "modulo_base": "5m x 5m (ancho fijo 5m)"
    })

# ============ EJECUTAR LA APLICACIÓN ============

if __name__ == '__main__':
    print("=" * 50)
    print("🏪 MercatoLogic API - Sistema de Gestión de Mercados")
    print("=" * 50)
    print("📍 Interfaz web: http://localhost:5001")
    print("=" * 50)
    print("📊 CONFIGURACIÓN DE DIMENSIONES:")
    print("   📐 Ancho FIJO: 5 metros")
    print("   📏 Largo variable: módulos x 5 metros")
    print("   1 módulo → 5m x 5m = 25m²")
    print("   2 módulos → 5m x 10m = 50m²")
    print("   3 módulos → 5m x 15m = 75m²")
    print("   4 módulos → 5m x 20m = 100m²")
    print("   ⚠️ Máximo: 4 módulos por vendedor")
    print("=" * 50)
    print("   🥬 Frutas y Verduras: 8 locales")
    print("   🥩 Carnes: 8 locales")
    print("   👕 Textiles: 4 locales")
    print(f"   🏪 TOTAL: {TOTAL_MAXIMO_LOCALES} locales")
    print("=" * 50)
    print("Presiona CTRL+C para detener el servidor")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5001)
