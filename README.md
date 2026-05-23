# 🏪 MercatoLogic API

![Versión](https://img.shields.io/badge/versión-1.0-blue)
![Python](https://img.shields.io/badge/Python-3.14-green)
![Flask](https://img.shields.io/badge/Flask-3.x-purple)
![Licencia](https://img.shields.io/badge/Licencia-Universitaria-orange)

##  Descripción del Proyecto

**MercatoLogic API** es un sistema de gestión logística para mercados locales y ferias libres, desarrollado como proyecto para el curso de Programación 3. La API permite a los administradores organizar la distribución de puestos por categorías (frutas, verduras, carnes, textiles), validando que el giro comercial del vendedor coincida con la zona asignada.

###  Problema que resuelve

-  **Contaminación cruzada** - Mezcla de productos incompatibles
- **Dificultad de navegación** - Compradores no encuentran productos
- **Saturación de espacios** - Invasión de pasillos y salidas

###  Beneficios

- **Ordenamiento Urbano** - Pasillos despejados
- **Higiene y Salud** - Separación efectiva de productos
-  **Eficiencia Comercial** - Vendedores más localizables

---

##  Equipo de Desarrollo

| Integrante | Responsabilidad |
|------------|-----------------|
| **Andy Betancourt** | Estructura de archivos JSON, definición de modelos de datos |
| **Marvin Chamorro** | Endpoints de dimensiones y metraje de puestos |
| **Sergio Enriquez** | Endpoints de categorías y validación de giro comercial |
| **Saúl Cal** | Endpoints de consulta de productos y manejo de errores |
| **Leonel Obregón** | Pruebas de endpoints, documentación y soporte en interfaz |

**Docente:** Ing. Julio Cesar Estrada Marcial  
**Universidad:** Universidad San Pablo de Guatemala, Campus Escuintla  
**Facultad:** Ciencias Económicas  
**Curso:** Programación 3  
**Fecha:** Febrero 2026

---

## Tecnologías Utilizadas

| Categoría | Tecnología |
|-----------|------------|
| **Lenguaje** | Python 3.14.2 |
| **Framework** | Flask 3.x |
| **Base de Datos** | Archivos JSON |
| **Frontend** | HTML5, CSS3, JavaScript |
| **Control de Versiones** | Git + GitHub |
| **Pruebas** | Postman / Navegador Web |



--- SUPUESTOS ----

## 11. Verificación de Supuestos

| Supuesto | Estado | Evidencia |
|----------|--------|-----------|
| **Supuesto 1** (Sin autenticación) |  Cumple | No hay login ni contraseñas en el sistema |
| **Supuesto 2** (Solo JSON) |  Cumple | Base de datos en database.json, sin MySQL/PostgreSQL |
| **Supuesto 3** (Un admin a la vez) | Cumple | Sin mecanismos de bloqueo, se asume uso secuencial |
| **Supuesto 4** (Conocimientos Python) |  Cumple | El código utiliza variables, funciones, condicionales y archivos |

---

## Instalación y Configuración

### Requisitos Previos

- Python 3.x instalado
- Pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar o descargar el proyecto**
```bash
cd ~/Desktop
mkdir MERCATOLogic_API
cd MERCATOLogic_API



python3 -m pip install flask

MERCATOLogic_API/
├── app.py              # API + Interfaz web
├── database.json       # Base de datos
└── README.md           # Documentación


cd ~/Desktop/MERCATOLogic_API
python3 app.py

http://localhost:5001


Configuración del Mercado
Sector	Capacidad máxima
🥬 Frutas y Verduras	8 locales
🥩 Carnes	8 locales
👕 Textiles	4 locales
🏪 TOTAL	20 locales


Dimensiones de los locales
Módulos	Dimensiones	Área
1 módulo	5m (ancho) x 5m (largo)	25 m²
2 módulos	5m (ancho) x 10m (largo)	50 m²
3 módulos	5m (ancho) x 15m (largo)	75 m²
4 módulos	5m (ancho) x 20m (largo)	100 m²


Endpoints de la API
Método	Ruta	Descripción
GET	/	Interfaz web principal
GET	/api/sectores	Lista todos los sectores
GET	/api/sectores/{id}	Obtiene un sector específico
GET	/api/puestos	Lista todos los puestos
GET	/api/puestos/{id}	Obtiene un puesto específico
POST	/api/asignacion/puesto	Asigna un nuevo vendedor
PUT	/api/espacios/{id}/dimensiones	Actualiza dimensiones
GET	/api/inventario/categorias	Busca productos
GET	/api/estadisticas	Estadísticas del mercado
GET	/api/capacidad	Capacidad actual
GET	/api/vendedores	Lista de vendedores
PUT	/api/vendedor/{id}/aumentar	Aumenta 1 módulo
PUT	/api/vendedor/{id}/reducir	Reduce 1 módulo
DELETE	/api/vendedor/{id}/eliminar	Elimina vendedor


--- ejemplos de uso---


curl -X GET http://localhost:5001/api/sectores

. Asignar un nuevo vendedor

curl -X POST http://localhost:5001/api/asignacion/puesto \
  -H "Content-Type: application/json" \
  -d '{
    "id_sector": 1,
    "nombre_vendedor": "Juan Pérez",
    "giro_negocio": "frutas_verduras",
    "modulos": 2
  }'


3. Buscar un producto
bash
curl -X GET "http://localhost:5001/api/inventario/categorias?producto=manzana"



4. Actualizar dimensiones
bash
curl -X PUT http://localhost:5001/api/espacios/1/dimensiones \
  -H "Content-Type: application/json" \
  -d '{"modulos": 3}'
