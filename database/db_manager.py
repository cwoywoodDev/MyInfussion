import os
import sqlite3
import uuid
import pandas as pd

# =========================================================
# 📁 RUTAS DE ALMACENAMIENTO LOCAL
# =========================================================
BASE_DIR = "BBDD_Infusiones"
DB_PATH = os.path.join(BASE_DIR, "recetario_herbal.db").replace("\\", "/")
MEDIA_DIR = os.path.join(BASE_DIR, "media_recetas").replace("\\", "/")

os.makedirs(MEDIA_DIR, exist_ok=True)


def get_connection():
    os.makedirs(BASE_DIR, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Tabla principal de infusiones
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS infusiones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria TEXT NOT NULL,
            horario TEXT NOT NULL,
            imagen_path TEXT,
            ingredientes TEXT NOT NULL,
            preparacion TEXT NOT NULL,
            beneficios TEXT NOT NULL,
            cuidados TEXT NOT NULL,
            observaciones TEXT
        )
    """)

    # Tablas de catálogos dinámicos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS horarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ingredientes_catalogo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bases_liquidas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tiempos_reposo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL
        )
    """)

    # Poblar valores iniciales por defecto si están vacíos
    categorias_default = [
        "Digestiva",
        "Relajante / Nocturna",
        "Energizante / Enfoque",
        "Respiratoria / Inmunidad",
        "Antiinflamatoria / Depurativa",
    ]
    for c in categorias_default:
        cursor.execute("INSERT OR IGNORE INTO categorias (nombre) VALUES (?)", (c,))

    horarios_default = [
        "Mañana (Ayunas / Desayuno)",
        "Después de las comidas",
        "Media tarde",
        "Noche (Antes de dormir)",
        "Cualquier momento del día",
    ]
    for h in horarios_default:
        cursor.execute("INSERT OR IGNORE INTO horarios (nombre) VALUES (?)", (h,))

    ingredientes_default = [
        "Manzanilla (flores)",
        "Cedrón / Hierba Luisa",
        "Menta / Hierbabuena",
        "Jengibre fresco",
        "Canela en rama",
        "Cúrcuma",
        "Té Verde (Sencha / Matcha)",
        "Lavanda",
        "Toronjil / Melisa",
        "Valeriana",
        "Boldo",
        "Poleo",
        "Limón (rodaja o jugo)",
        "Miel pura de abeja",
    ]
    for ing in ingredientes_default:
        cursor.execute("INSERT OR IGNORE INTO ingredientes_catalogo (nombre) VALUES (?)", (ing,))

    bases_default = [
        "250 ml de agua purificada (1 taza estándar)",
        "500 ml de agua purificada (tetera pequeña)",
        "1 litro de agua purificada (jarra)",
        "250 ml de bebida vegetal (almendras / coco / avena)",
    ]
    for b in bases_default:
        cursor.execute("INSERT OR IGNORE INTO bases_liquidas (nombre) VALUES (?)", (b,))

    tiempos_default = [
        "3 a 5 minutos (tapado)",
        "5 a 8 minutos (tapado)",
        "10 a 15 minutos (infusión concentrada)",
        "Hervir 5 minutos y reposar 5 minutos",
        "Macerar 4 a 8 horas en frío",
    ]
    for t in tiempos_default:
        cursor.execute("INSERT OR IGNORE INTO tiempos_reposo (nombre) VALUES (?)", (t,))

    conn.commit()
    conn.close()


# =========================================================
# 🖼️ GESTIÓN DE IMÁGENES (RUTAS COMPATIBLES WINDOWS/LINUX)
# =========================================================
def guardar_imagen_local(uploaded_file):
    if uploaded_file is None:
        return None
    os.makedirs(MEDIA_DIR, exist_ok=True)
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if not ext:
        ext = ".jpg"
    nombre_unico = f"{uuid.uuid4().hex}{ext}"
    ruta_completa = os.path.join(MEDIA_DIR, nombre_unico).replace("\\", "/")
    with open(ruta_completa, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return ruta_completa


# =========================================================
# 🍵 CRUD DE INFUSIONES
# =========================================================
def insertar_infusion(nombre, categoria, horario, imagen_path, ingredientes, preparacion, beneficios, cuidados, observaciones=""):
    conn = get_connection()
    cursor = conn.cursor()
    ruta_norm = str(imagen_path).replace("\\", "/") if imagen_path else None
    cursor.execute("""
        INSERT INTO infusiones (nombre, categoria, horario, imagen_path, ingredientes, preparacion, beneficios, cuidados, observaciones)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (nombre, categoria, horario, ruta_norm, ingredientes, preparacion, beneficios, cuidados, observaciones))
    conn.commit()
    conn.close()


def obtener_todas_infusiones():
    init_db()
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM infusiones ORDER BY id DESC", conn)
    conn.close()
    if not df.empty and "imagen_path" in df.columns:
        df["imagen_path"] = df["imagen_path"].apply(lambda x: str(x).replace("\\", "/") if pd.notna(x) and x else None)
    return df


def eliminar_infusion(id_receta):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT imagen_path FROM infusiones WHERE id = ?", (id_receta,))
    row = cursor.fetchone()
    if row and row[0]:
        ruta_img = str(row[0]).replace("\\", "/")
        if os.path.exists(ruta_img):
            try:
                os.remove(ruta_img)
            except OSError:
                pass
    cursor.execute("DELETE FROM infusiones WHERE id = ?", (id_receta,))
    conn.commit()
    conn.close()


# =========================================================
# 📋 FUNCIONES DE CATÁLOGOS DINÁMICOS
# =========================================================
def obtener_categorias():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM categorias ORDER BY nombre ASC")
    res = [r[0] for r in cursor.fetchall()]
    conn.close()
    return res


def agregar_categoria(nombre):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO categorias (nombre) VALUES (?)", (nombre.strip(),))
    conn.commit()
    conn.close()


def obtener_horarios():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM horarios ORDER BY id ASC")
    res = [r[0] for r in cursor.fetchall()]
    conn.close()
    return res


def agregar_horario(nombre):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO horarios (nombre) VALUES (?)", (nombre.strip(),))
    conn.commit()
    conn.close()


def obtener_ingredientes_catalogo():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM ingredientes_catalogo ORDER BY nombre ASC")
    res = [r[0] for r in cursor.fetchall()]
    conn.close()
    return res


def agregar_ingrediente_catalogo(nombre):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO ingredientes_catalogo (nombre) VALUES (?)", (nombre.strip(),))
    conn.commit()
    conn.close()


def obtener_bases_liquidas():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM bases_liquidas ORDER BY id ASC")
    res = [r[0] for r in cursor.fetchall()]
    conn.close()
    return res


def agregar_base_liquida(nombre):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO bases_liquidas (nombre) VALUES (?)", (nombre.strip(),))
    conn.commit()
    conn.close()


def obtener_tiempos_reposo():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM tiempos_reposo ORDER BY id ASC")
    res = [r[0] for r in cursor.fetchall()]
    conn.close()
    return res


def agregar_tiempo_reposo(nombre):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO tiempos_reposo (nombre) VALUES (?)", (nombre.strip(),))
    conn.commit()
    conn.close()