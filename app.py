from flask import Flask, jsonify, request
import json

app = Flask(__name__)

# Nombre del archivo de base de datos
ARCHIVO_DB = 'database.json'

# ============ FUNCIONES PARA MANEJAR LA BASE DE DATOS ============

def leer_datos():
    """Lee los datos del archivo database.json"""
    with open(ARCHIVO_DB, 'r', encoding='utf-8') as archivo:
        return json.load(archivo)

def guardar_datos(datos):
    """Guarda los datos en el archivo database.json"""
    with open(ARCHIVO_DB, 'w', encoding='utf-8') as archivo:
        json.dump(datos, archivo, indent=2, ensure_ascii=False)

# ============ RUTA DE BIENVENIDA ============

@app.route('/')
def bienvenida():
    return jsonify({"mensaje": "Bienvenido a MercatoLogic API", 
                    "version": "1.0",
                    "estado": "funcionando"})

# ============ ENDPOINTS DE SECTORES ============
# Responsable: Sergio Enriquez

@app.route('/api/sectores', methods=['GET'])
def listar_sectores():
    """Lista todos los sectores del mercado"""
    datos = leer_datos()
    return jsonify(datos['sectores'])

@app.route('/api/sectores/<int:id>', methods=['GET'])
def obtener_sector(id):
    """Obtiene un sector específico por su ID"""
    datos = leer_datos()
    sector = next((s for s in datos['sectores'] if s['id'] == id), None)
    
    if sector:
        return jsonify(sector)
    return jsonify({"error": "Sector no encontrado"}), 404

# ============ ENDPOINTS DE PUESTOS ============

@app.route('/api/puestos', methods=['GET'])
def listar_puestos():
    """Lista todos los puestos del mercado"""
    datos = leer_datos()
    return jsonify(datos['puestos'])

@app.route('/api/puestos/<int:id>', methods=['GET'])
def obtener_puesto(id):
    """Obtiene un puesto específico por su ID"""
    datos = leer_datos()
    puesto = next((p for p in datos['puestos'] if p['id'] == id), None)
    
    if puesto:
        return jsonify(puesto)
    return jsonify({"error": "Puesto no encontrado"}), 404

# ============ ASIGNAR VENDEDOR A UN PUESTO ============
# Responsable: Andy Betancourt y Cristian Saúl

@app.route('/api/asignacion/puesto', methods=['POST'])
def asignar_puesto():
    """
    Asigna un vendedor a un puesto.
    Valida que el giro del negocio coincida con la categoría del sector.
    """
    datos = leer_datos()
    nueva_asignacion = request.json
    
    # Validar que llegaron los datos necesarios
    campos_requeridos = ['id_sector', 'nombre_vendedor', 'giro_negocio']
    for campo in campos_requeridos:
        if campo not in nueva_asignacion:
            return jsonify({"error": f"Falta el campo: {campo}"}), 400
    
    # Validar que el sector exista
    sector = next((s for s in datos['sectores'] 
                   if s['id'] == nueva_asignacion['id_sector']), None)
    
    if not sector:
        return jsonify({"error": "El sector no existe"}), 404
    
    # Validar que el giro del negocio coincida con la categoría del sector
    if nueva_asignacion['giro_negocio'] != sector['categoria']:
        return jsonify({
            "error": f"El giro '{nueva_asignacion['giro_negocio']}' no coincide con la zona",
            "zona": sector['nombre'],
            "giro_permitido": sector['categoria']
        }), 400
    
    # Generar nuevo ID
    nuevo_id = max([p['id'] for p in datos['puestos']]) + 1 if datos['puestos'] else 1
    
    # Crear nuevo puesto con dimensiones por defecto
    nuevo_puesto = {
        "id": nuevo_id,
        "id_sector": nueva_asignacion['id_sector'],
        "nombre_vendedor": nueva_asignacion['nombre_vendedor'],
        "giro_negocio": nueva_asignacion['giro_negocio'],
        "dimensiones": {
            "ancho": 2.5,
            "largo": 2.0,
            "metros_cuadrados": 5.0
        }
    }
    
    datos['puestos'].append(nuevo_puesto)
    guardar_datos(datos)
    
    return jsonify({
        "mensaje": "Puesto asignado exitosamente",
        "puesto": nuevo_puesto
    }), 201

# ============ ACTUALIZAR DIMENSIONES DE UN PUESTO ============
# Responsable: Marvin Chamorro

@app.route('/api/espacios/<int:id>/dimensiones', methods=['PUT'])
def actualizar_dimensiones(id):
    """
    Actualiza las dimensiones de un puesto.
    Recalcula automáticamente los metros cuadrados.
    """
    datos = leer_datos()
    puesto = next((p for p in datos['puestos'] if p['id'] == id), None)
    
    if not puesto:
        return jsonify({"error": "Puesto no encontrado"}), 404
    
    nuevas_dimensiones = request.json
    
    # Actualizar dimensiones (mantener valores anteriores si no se envían)
    ancho = nuevas_dimensiones.get('ancho', puesto['dimensiones']['ancho'])
    largo = nuevas_dimensiones.get('largo', puesto['dimensiones']['largo'])
    
    # Validar que las dimensiones sean positivas
    if ancho <= 0 or largo <= 0:
        return jsonify({"error": "Las dimensiones deben ser mayores a 0"}), 400
    
    puesto['dimensiones']['ancho'] = ancho
    puesto['dimensiones']['largo'] = largo
    puesto['dimensiones']['metros_cuadrados'] = round(ancho * largo, 2)
    
    guardar_datos(datos)
    
    return jsonify({
        "mensaje": "Dimensiones actualizadas correctamente",
        "puesto": puesto
    })

# ============ BUSCAR PRODUCTOS POR CATEGORÍA ============
# Responsable: Saúl Cal

@app.route('/api/inventario/categorias', methods=['GET'])
def buscar_producto():
    """
    Permite a los compradores consultar en qué pasillo 
    se encuentra un tipo específico de producto.
    """
    producto = request.args.get('producto', '').lower()
    
    if not producto:
        return jsonify({"error": "Debes especificar un producto", 
                        "ejemplo": "/api/inventario/categorias?producto=manzana"}), 400
    
    datos = leer_datos()
    
    # Mapeo de productos a categorías
    mapa_productos = {
        # Frutas y verduras
        'manzana': 'frutas_verduras',
        'pera': 'frutas_verduras',
        'platano': 'frutas_verduras',
        'lechuga': 'frutas_verduras',
        'tomate': 'frutas_verduras',
        'cebolla': 'frutas_verduras',
        'zanahoria': 'frutas_verduras',
        # Carnes
        'res': 'carnes',
        'pollo': 'carnes',
        'cerdo': 'carnes',
        'pescado': 'carnes',
        # Textiles
        'camisa': 'textiles',
        'pantalon': 'textiles',
        'vestido': 'textiles',
        'zapatos': 'textiles'
    }
    
    if producto in mapa_productos:
        categoria = mapa_productos[producto]
        sector_encontrado = next((s for s in datos['sectores'] if s['categoria'] == categoria), None)
        
        if sector_encontrado:
            return jsonify({
                "producto": producto,
                "categoria": categoria,
                "sector": sector_encontrado['nombre'],
                "sector_id": sector_encontrado['id'],
                "pasillo": f"Zona {sector_encontrado['id']} - {sector_encontrado['nombre']}",
                "mensaje": f"El producto '{producto}' se encuentra en la {sector_encontrado['nombre']}"
            })
    
    # Si no se encuentra, mostrar productos disponibles
    productos_disponibles = list(mapa_productos.keys())
    return jsonify({
        "error": f"Producto '{producto}' no encontrado",
        "productos_disponibles": productos_disponibles[:10],  # Mostrar solo 10 ejemplos
        "sugerencia": "Prueba con: manzana, lechuga, tomate, res, pollo, camisa"
    }), 404

# ============ ENDPOINT EXTRA: ESTADÍSTICAS ============

@app.route('/api/estadisticas', methods=['GET'])
def estadisticas():
    """Muestra estadísticas básicas del mercado"""
    datos = leer_datos()
    
    total_puestos = len(datos['puestos'])
    total_sectores = len(datos['sectores'])
    
    # Contar puestos por sector
    puestos_por_sector = {}
    for sector in datos['sectores']:
        conteo = sum(1 for p in datos['puestos'] if p['id_sector'] == sector['id'])
        puestos_por_sector[sector['nombre']] = conteo
    
    return jsonify({
        "total_sectores": total_sectores,
        "total_puestos": total_puestos,
        "puestos_por_sector": puestos_por_sector,
        "capacidad_disponible": "Por definir"
    })

# ============ EJECUTAR LA APLICACIÓN ============

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 MercatoLogic API - Sistema de Gestión de Mercados")
    print("=" * 50)
    print("📍 Servidor corriendo en: http://localhost:5000")
    print("📋 Endpoints disponibles:")
    print("   GET  /api/sectores")
    print("   GET  /api/sectores/{id}")
    print("   GET  /api/puestos")
    print("   GET  /api/puestos/{id}")
    print("   POST /api/asignacion/puesto")
    print("   PUT  /api/espacios/{id}/dimensiones")
    print("   GET  /api/inventario/categorias?producto=nombre")
    print("   GET  /api/estadisticas")
    print("=" * 50)
    print("Presiona CTRL+C para detener el servidor")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)