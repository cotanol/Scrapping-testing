import time
import json
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

# --- IMPORTAMOS NUESTROS MÓDULOS EXPERTOS ---
# Asegúrate de que los nombres de los archivos .py coincidan
from colecciones_marcas import get_all_product_urls_from_brand
from royo_scrapper_avanzado import scrape_all_product_combinations

# --- CONFIGURACIÓN ---
BRAND_URL_TO_SCRAPE = "https://www.todomueblesdebano.com/marcas/royo/" # Puedes cambiar esto a cualquier marca
CSV_FILENAME = "reporte_final_marca.csv"

# --- NUEVA FUNCIÓN PARA DATOS BÁSICOS ---
def scrape_basic_product_details(soup):
    """
    Extrae los datos básicos visibles en la página de detalles de un producto.
    """
    details = {}
    try:
        title_element = soup.select_one("h1 span.font-semibold")
        details['Nombre'] = title_element.text.strip() if title_element else 'No disponible'
        
        subtitle_element = soup.select_one("h1 span.subname")
        details['Subtitulo'] = subtitle_element.text.strip() if subtitle_element else ''

        price_element = soup.select_one("span.price")
        details['Precio Actual'] = price_element.text.strip() if price_element else 'No disponible'

        old_price_element = soup.select_one("span.line-through")
        details['Precio Antiguo'] = old_price_element.text.strip() if old_price_element else ''

        discount_element = soup.select_one("span.bg-yellow-300")
        details['Descuento'] = discount_element.text.strip().replace('\n', '').replace(' ', '') if discount_element else ''

        ref_element = soup.select_one("div.ref-container")
        details['Referencia'] = ref_element.text.strip() if ref_element else ''

    except Exception as e:
        print(f"  -> Advertencia: No se pudieron extraer todos los datos básicos. Error: {e}")
    return details

# --- FUNCIÓN PRINCIPAL / ORQUESTADOR ---
def main():
    print(f"--- INICIANDO SCRAPER MASIVO PARA LA MARCA: {BRAND_URL_TO_SCRAPE} ---")
    service = Service(executable_path='chromedriver.exe')
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()

    # --- FASE 1: OBTENER TODAS LAS URLS DE PRODUCTOS DE LA MARCA ---
    # Usamos nuestro primer módulo experto
    product_urls_with_context = get_all_product_urls_from_brand(driver, BRAND_URL_TO_SCRAPE)

    all_products_final_data = []

    # --- FASE 2: RECORRER CADA URL DE PRODUCTO PARA EXTRAER DETALLES ---
    for product_info in product_urls_with_context:
        product_url = product_info['url']
        brand_name = product_info['marca']
        collection_name = product_info['coleccion']
        
        print(f"\n--- PROCESANDO PRODUCTO ---")
        print(f"  Marca: {brand_name}, Colección: {collection_name}")
        
        driver.get(product_url)
        time.sleep(2) # Pausa para que la página cargue
        
        # 1. Extraemos los datos básicos de la página
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        basic_details = scrape_basic_product_details(soup)
        
        # 2. Llamamos a nuestro segundo módulo experto para las combinaciones
        combinations_data = scrape_all_product_combinations(driver, product_url)
        
        # 3. Unimos toda la información
        final_product_data = {
            'Marca': brand_name,
            'Coleccion': collection_name,
            'Nombre': basic_details.get('Nombre', 'No disponible'),
            'Subtitulo': basic_details.get('Subtitulo', ''),
            'Referencia': basic_details.get('Referencia', ''),
            'Precio Actual': basic_details.get('Precio Actual', 'No disponible'),
            'Precio Antiguo': basic_details.get('Precio Antiguo', ''),
            'Descuento': basic_details.get('Descuento', ''),
            'Combinaciones (JSON)': json.dumps(combinations_data, ensure_ascii=False),
            'Enlace': product_url
        }
        all_products_final_data.append(final_product_data)

    # --- FASE 3: GUARDAR TODO EN UN ARCHIVO CSV ---
    if all_products_final_data:
        print(f"\n--- PROCESO COMPLETADO: Se procesaron {len(all_products_final_data)} productos. Guardando en CSV... ---")
        headers = list(all_products_final_data[0].keys())
        try:
            with open(CSV_FILENAME, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(all_products_final_data)
            print(f"¡ÉXITO! ✨ Datos guardados en '{CSV_FILENAME}'")
        except IOError as e:
            print(f"ERROR al escribir el archivo CSV: {e}")

    driver.quit()

if __name__ == "__main__":
    main()