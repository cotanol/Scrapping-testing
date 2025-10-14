import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# ==============================================================================
# --- CONFIGURACIÓN ---
# Pega aquí la URL del producto que quieres analizar
PRODUCT_URL = "https://www.todomueblesdebano.com/conjunto-mueble-de-bano-royo-alfa-2-cajones-1-puerta.html" 
# ==============================================================================

def main():
    """
    Script de prueba para visitar una URL de producto, extraer el objeto __NUXT__
    y guardarlo en un archivo JSON para su análisis.
    """
    print(f"🚀 Iniciando análisis para: {PRODUCT_URL}")
    
    # --- Configuración de Selenium ---
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Ejecutar en modo oculto, sin abrir ventana
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--log-level=3") # Suprimir mensajes innecesarios en la consola
    
    driver = None
    
    try:
        # --- Inicializar el navegador ---
        # Asegúrate de que 'chromedriver.exe' esté en la misma carpeta o en el PATH del sistema
        service = Service(executable_path='chromedriver.exe')
        driver = webdriver.Chrome(service=service, options=options)
        
        # --- Visitar la URL ---
        print("   [*] Navegando a la página...")
        driver.get(PRODUCT_URL)
        
        # --- Esperar a que el objeto __NUXT__ esté disponible ---
        print("   [*] Esperando a que la página cargue los datos...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "__nuxt"))
        )
        
        # --- ¡La Magia! Extraer el objeto __NUXT__ ya "traducido" ---
        # El navegador ya ha ejecutado el Javascript, así que obtenemos el objeto final.
        print("   [*] Extrayendo el objeto __NUXT__...")
        nuxt_data = driver.execute_script("return window.__NUXT__;")
        
        if not nuxt_data:
            print("   [❌] ERROR: No se pudo extraer el objeto __NUXT__.")
            return

        # --- Guardar los datos en un archivo JSON para un análisis fácil ---
        output_filename = "nuxt_data.json"
        print(f"   [*] Guardando los datos en el archivo '{output_filename}'...")
        
        with open(output_filename, 'w', encoding='utf-8') as f:
            # json.dumps lo formatea de manera legible (pretty-print)
            # ensure_ascii=False es crucial para guardar correctamente tildes y caracteres especiales
            json.dump(nuxt_data, f, indent=2, ensure_ascii=False)
            
        print(f"\n✅ ¡Análisis completado! Abre el archivo '{output_filename}' en VS Code para inspeccionar los datos.")

    except Exception as e:
        print(f"\n❌ Ocurrió un error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # --- Cerrar el navegador ---
        if driver:
            driver.quit()
        print("\n👋 Script finalizado.")

if __name__ == "__main__":
    main()