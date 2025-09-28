import csv
from ftplib import FTP

# Importamos nuestro scraper
from main_scrapper import main as ejecutar_scraper, CSV_FILENAME

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
        print("💡 Asegúrate de crear el archivo ftp_config.txt con el formato:")
        print("servidor=ftp.tuservidor.com")
        print("usuario=tu_usuario")
        print("contraseña=tu_contraseña")
        print("ruta_remota=/uploads")
        return None

# ================================
# 2. Ejecutar web scraping de productos reales
# ================================
def ejecutar_scraping():
    print("🕷️  Ejecutando web scraping...")
    try:
        ejecutar_scraper()  # Ejecuta el scraper y crea el CSV
        print(f"✅ Web scraping completado. Archivo generado: {CSV_FILENAME}")
        return True
    except Exception as e:
        print(f"❌ Error en el web scraping: {e}")
        return False

# ================================
# 3. Subir CSV a servidor FTP (mejorado)
# ================================
def subir_csv_a_ftp(nombre_archivo_csv, servidor, usuario, contraseña, ruta_remota="/"):
    try:
        # Conexión al servidor FTP
        ftp = FTP(servidor)
        ftp.login(usuario, contraseña)
        print(f"🔗 Conectado al servidor FTP: {servidor}")

        # Mostrar directorio actual
        directorio_actual = ftp.pwd()
        print(f"📁 Directorio actual: {directorio_actual}")

        # Cambiar al directorio remoto si se especifica y no es raíz
        if ruta_remota and ruta_remota != "/" and ruta_remota.strip():
            try:
                ftp.cwd(ruta_remota)
                print(f"📁 Cambiado al directorio remoto: {ruta_remota}")
            except Exception as e:
                print(f"⚠️  No se pudo cambiar al directorio '{ruta_remota}': {e}")
                print(f"📁 Usando directorio actual: {directorio_actual}")

        # Abrir y subir el archivo
        with open(nombre_archivo_csv, 'rb') as archivo:
            ftp.storbinary(f'STOR {nombre_archivo_csv}', archivo)

        print(f"✅ Archivo '{nombre_archivo_csv}' subido correctamente al FTP.")
        
        # Verificar que el archivo se subió
        archivos = ftp.nlst()
        if nombre_archivo_csv in archivos:
            print(f"✅ Archivo verificado en el servidor.")
        
        ftp.quit()
        return True

    except Exception as e:
        print(f"❌ Error al subir el archivo al FTP: {e}")
        print("💡 Sugerencias:")
        print("   • Verificar credenciales en ftp_config.txt")
        print("   • Cambiar ruta_remota=/ para usar directorio raíz")
        print("   • Comprobar permisos del usuario FTP")
        return False

# ================================
# 4. Ejecutar todo: Scraping + FTP
# ================================

print("🚀 INICIANDO: Web Scraping + FTP Upload")
print("=" * 40)

# Paso 1: Ejecutar scraping
if ejecutar_scraping():
    
    # Paso 2: Leer configuración FTP
    print("\n📋 Cargando configuración FTP...")
    config = leer_configuracion_ftp("ftp_config.txt")
    
    if config:
        # Paso 3: Subir archivo al FTP
        print("\n📤 Subiendo archivo al FTP...")
        if subir_csv_a_ftp(
            CSV_FILENAME,
            servidor=config.get("servidor"),
            usuario=config.get("usuario"),
            contraseña=config.get("contraseña"),
            ruta_remota=config.get("ruta_remota", "/")
        ):
            print("\n🎉 PROCESO COMPLETADO: Scraping + FTP exitoso!")
        else:
            print(f"\n⚠️  Scraping exitoso, pero falló la subida FTP.")
            print(f"📄 El archivo '{CSV_FILENAME}' está disponible localmente.")
    else:
        print(f"\n⚠️  Scraping exitoso, pero no se pudo cargar configuración FTP.")
        print(f"📄 El archivo '{CSV_FILENAME}' está disponible localmente.")
else:
    print("\n❌ El web scraping falló. No se puede continuar.")

print("\n👋 Proceso terminado.")