import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# --- CONFIGURACIÓN ---
URL_MARCA_ROYO = "https://www.todomueblesdebano.com/marcas/royo/"
CSV_FILENAME = 'productos_royo_detallado.csv'
BASE_DOMAIN = "https://www.todomueblesdebano.com"

# --- VARIABLES GLOBALES DE TIEMPO ---
WAIT_FOR_ELEMENT = 10
WAIT_FOR_BUTTON = 5
PAUSE_AFTER_CLICK = 3
PAUSE_SHORT = 1

def get_collection_data(driver, brand_url):
    """
    FASE 1: Navega a la URL de la marca y extrae el NOMBRE y el ENLACE de cada colección.
    """
    driver.get(brand_url)
    print(f"FASE 1: Accediendo a la marca: {brand_url}")
    
    try:
        WebDriverWait(driver, WAIT_FOR_ELEMENT).until(EC.element_to_be_clickable((By.ID, "accept-cookies"))).click()
        print("Cookies aceptadas.")
    except Exception:
        print("No se encontró el banner de cookies o ya fue aceptado.")
        
    while True:
        try:
            load_more_button = WebDriverWait(driver, WAIT_FOR_BUTTON).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.load-more")))
            driver.execute_script("arguments[0].scrollIntoView();", load_more_button)
            time.sleep(PAUSE_SHORT)
            load_more_button.click()
            print("  -> Clic en 'Ver más colecciones'...")
            time.sleep(PAUSE_AFTER_CLICK)
        except Exception:
            print("  -> No hay más colecciones que cargar.")
            break
            
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    
    collections_data = []
    collection_containers = soup.select("div.col-span-12.md\\:col-span-6.lg\\:col-span-3")

    for container in collection_containers:
        name_element = container.select_one("h3")
        link_element = container.select_one("a[title^='Ver Colección']")
        
        if name_element and link_element:
            collection_name = name_element.text.strip()
            href = link_element.get('href')
            full_url = BASE_DOMAIN + href
            
            if not any(d['name'] == collection_name for d in collections_data):
                collections_data.append({'name': collection_name, 'url': full_url})
                
    print(f"  -> Se encontraron {len(collections_data)} colecciones.")
    return collections_data

def get_product_urls_from_collection(driver, collection_url):
    """
    FASE 2: Navega a una colección, carga todos los productos y extrae sus URLs.
    """
    driver.get(collection_url)
    print(f"\n    FASE 2: Accediendo a la colección: {collection_url}")
    
    while True:
        try:
            load_more_button = WebDriverWait(driver, WAIT_FOR_BUTTON).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'load-more') and contains(text(), 'Cargar Mas')]"))
            )
            driver.execute_script("arguments[0].scrollIntoView();", load_more_button)
            time.sleep(PAUSE_SHORT)
            load_more_button.click()
            print("      -> Clic en 'Cargar Mas' productos...")
            time.sleep(PAUSE_AFTER_CLICK)
        except Exception:
            print("      -> No hay más productos que cargar.")
            break
            
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    
    product_urls = []
    product_containers = soup.select('div.product-snippet')
    
    for container in product_containers:
        link_element = container.select_one('a[title^="Ir a"]')
        if link_element and link_element.get('href'):
            product_url = BASE_DOMAIN + link_element['href']
            product_urls.append(product_url)
    
    print(f"      -> Se encontraron {len(product_urls)} URLs de productos.")
    return product_urls

def scrape_product_details(driver, product_url):
    """
    FASE 3: Visita la página de un producto individual y extrae todos los datos detallados.
    """
    driver.get(product_url)
    print(f"\n        FASE 3: Extrayendo datos de: {product_url}")
    time.sleep(PAUSE_SHORT) # Pequeña espera para que todo cargue
    
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    
    details = {}
    
    # --- Extracción de datos principales ---
    title_element = soup.select_one("h1 span.font-semibold")
    details['Nombre'] = title_element.text.strip() if title_element else 'No disponible'
    
    subtitle_element = soup.select_one("h1 span.subname")
    details['Subtitulo'] = subtitle_element.text.strip() if subtitle_element else 'No disponible'
    
    price_element = soup.select_one("span.price")
    details['Precio'] = price_element.text.strip() if price_element else 'No disponible'

    old_price_element = soup.select_one("span.line-through")
    details['Precio Antiguo'] = old_price_element.text.strip() if old_price_element else 'No disponible'

    color_elements = soup.select('div.colour-list div.colour')
    colors = [color['title'].replace('color ', '') for color in color_elements if 'title' in color.attrs]
    details['Colores'] = ', '.join(colors) if colors else 'No disponible'

    # --- Lógica para hacer clic en "Ver ficha técnica" y extraer datos ---
    ficha_tecnica = {}
    url_montaje = 'No disponible'
    url_ficha = 'No disponible'
    try:
        # 1. Hacer clic en el botón
        tech_sheet_button = WebDriverWait(driver, WAIT_FOR_BUTTON).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.extra-tech-data"))
        )
        tech_sheet_button.click()
        print("          -> Clic en 'Ver ficha técnica'.")
        time.sleep(PAUSE_AFTER_CLICK)

        # 2. Leer el HTML del panel lateral que apareció
        sidebar_soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # 3. Extraer los datos de la lista
        tech_items = sidebar_soup.select("div.product-description-component li")
        for item in tech_items:
            key_element = item.select_one("span.font-bold")
            if key_element:
                key = key_element.text.strip().replace(':', '')
                value = key_element.next_sibling.strip() if key_element.next_sibling else ''
                ficha_tecnica[key] = value

        # 4. Extraer los enlaces de descarga
        montaje_link = sidebar_soup.find('a', text=lambda t: t and 'instrucciones de montaje' in t.lower())
        if montaje_link:
            url_montaje = montaje_link['href']

        ficha_link = sidebar_soup.find('a', text=lambda t: t and 'descargar ficha tecnica' in t.lower())
        if ficha_link:
            url_ficha = ficha_link['href']

    except Exception as e:
        print(f"          -> No se encontró o no se pudo procesar la ficha técnica. Error: {e}")

    details['Ficha Tecnica'] = ficha_tecnica
    details['URL Montaje'] = url_montaje
    details['URL Ficha Tecnica'] = url_ficha

    return details


def main():
    print("Iniciando scraper específico para ROYO...")
    service = Service(executable_path='chromedriver.exe')
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    
    # FASE 1: Obtener las colecciones de Royo
    collections = get_collection_data(driver, URL_MARCA_ROYO)
    
    all_products_details = []
    for collection in collections:
        collection_name = collection['name']
        collection_url = collection['url']
        
        # FASE 2: Obtener las URLs de los productos de la colección
        product_urls = get_product_urls_from_collection(driver, collection_url)
        
        # FASE 3: Visitar cada URL de producto y extraer sus detalles
        for product_url in product_urls:
            product_details = scrape_product_details(driver, product_url)
            # Añadimos los datos que ya conocíamos
            product_details['Marca'] = 'Royo Group'
            product_details['Coleccion'] = collection_name
            product_details['Enlace Producto'] = product_url
            all_products_details.append(product_details)

    print(f"\nPROCESO COMPLETADO. Se extrajeron detalles de {len(all_products_details)} productos.")
    
    # Guardar en CSV
    if all_products_details:
        # Las cabeceras se basan en las claves del primer diccionario de producto
        headers = list(all_products_details[0].keys())
        try:
            with open(CSV_FILENAME, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(all_products_details)
            print(f"¡ÉXITO! ✨ Datos guardados en '{CSV_FILENAME}'")
        except IOError as e:
            print(f"\nERROR al escribir el archivo CSV: {e}")

    driver.quit()

if __name__ == "__main__":
    main()