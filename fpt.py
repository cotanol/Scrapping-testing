import csv
from ftplib import FTP

# ================================
# 1. Leer configuración FTP desde un archivo de texto
# ================================
def leer_configuracion_ftp(archivo_config):
    config = {}
    try:
        with open(archivo_config, "r", encoding="utf-8") as f:
            for linea in f:
                if "=" in linea:
                    clave, valor = linea.strip().split("=", 1)
                    config[clave.strip()] = valor.strip()
        return config
    except Exception as e:
        print(f"❌ Error al leer el archivo de configuración: {e}")
        return None

# ================================
# 2. Simulación de datos del scraping
# ================================
datos_scrapeados = [
    ["Nombre", "Edad", "Ciudad"],
    ["Juan", 30, "Madrid"],
    ["Ana", 25, "Barcelona"],
    ["Luis", 40, "Valencia"]
]

# ================================
# 3. Crear el archivo CSV localmente
# ================================
nombre_archivo_csv = "datos_scrapeados.csv"

def guardar_datos_en_csv(nombre_archivo, datos):
    try:
        with open(nombre_archivo, mode='w', newline='', encoding='utf-8') as archivo_csv:
            escritor = csv.writer(archivo_csv)
            escritor.writerows(datos)
        print(f"✅ Archivo CSV '{nombre_archivo}' creado correctamente.")
    except Exception as e:
        print(f"❌ Error al crear el CSV: {e}")

guardar_datos_en_csv(nombre_archivo_csv, datos_scrapeados)

# ================================
# 4. Subir CSV a servidor FTP
# ================================
def subir_csv_a_ftp(nombre_archivo_csv, servidor, usuario, contraseña, ruta_remota="/"):
    try:
        # Conexión al servidor FTP
        ftp = FTP(servidor)
        ftp.login(usuario, contraseña)
        print(f"🔗 Conectado al servidor FTP: {servidor}")

        # Cambiar al directorio remoto si se especifica
        if ruta_remota:
            ftp.cwd(ruta_remota)
            print(f"📁 Cambiado al directorio remoto: {ruta_remota}")

        # Abrir y subir el archivo
        with open(nombre_archivo_csv, 'rb') as archivo:
            ftp.storbinary(f'STOR {nombre_archivo_csv}', archivo)

        print(f"✅ Archivo '{nombre_archivo_csv}' subido correctamente al FTP.")
        ftp.quit()

    except Exception as e:
        print(f"❌ Error al subir el archivo al FTP: {e}")

# ================================
# 5. Ejecutar todo
# ================================

# Leer configuración
config = leer_configuracion_ftp("ftp_config.txt")

if config:
    subir_csv_a_ftp(
        nombre_archivo_csv,
        servidor=config.get("servidor"),
        usuario=config.get("usuario"),
        contraseña=config.get("contraseña"),
        ruta_remota=config.get("ruta_remota", "/")
    )
