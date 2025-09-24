import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# --- CONFIGURACIÓN ---
URL_MARCAS = "https://www.todomueblesdebano.com/marcas/"
CSV_FILENAME = 'TODOS_LOS_PRODUCTOS.csv'
BASE_DOMAIN = "https://www.todomueblesdebano.com"

def get_brand_links(driver, url):
    """
    FASE 1: Navega a la página de marcas y extrae el nombre y la URL de cada una.
    """
    driver.get(url)
    print(f"FASE 1: Accediendo a la página de todas las marcas: {url}")
    
    try:
        print("Buscando y aceptando el banner de cookies...")
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "accept-cookies"))).click()
        print("Cookies aceptadas.")
    except Exception:
        print("No se encontró el banner de cookies o ya fue aceptado.")
        
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    
    brands_data = []
    # --- SELECTOR CORREGIDO AQUÍ ---
    # Buscamos cada 'caja' que contiene una marca.
    brand_containers = soup.select('div.text-center')
    
    for container in brand_containers:
        link_element = container.find('a', href=True)
        name_element = container.find('h3')
        if link_element and name_element:
            brand_name = name_element.text.strip()
            relative_url = link_element['href']
            full_url = BASE_DOMAIN + relative_url
            
            # Evitamos duplicados
            if not any(d['name'] == brand_name for d in brands_data):
                brands_data.append({'name': brand_name, 'url': full_url})
                
    print(f"Se encontraron {len(brands_data)} marcas.")
    return brands_data

def get_collection_links(driver, brand_url):
    """
    FASE 2: Navega a la URL de una marca y extrae los enlaces de sus colecciones.
    """
    driver.get(brand_url)
    print(f"\n  FASE 2: Accediendo a la marca: {brand_url}")
    
    while True:
        try:
            load_more_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.load-more")))
            driver.execute_script("arguments[0].scrollIntoView();", load_more_button)
            time.sleep(1)
            load_more_button.click()
            print("    -> Clic en 'Ver más colecciones'...")
            time.sleep(2)
        except Exception:
            print("    -> No hay más colecciones que cargar.")
            break
            
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    
    collection_links = []
    link_elements = soup.select("a[title^='Ver Colección']")
    
    for link in link_elements:
        href = link.get('href')
        if href:
            full_url = BASE_DOMAIN + href
            if full_url not in collection_links:
                collection_links.append(full_url)
                
    print(f"    -> Se encontraron {len(collection_links)} colecciones para esta marca.")
    return collection_links

def scrape_products_from_collection(driver, collection_url, brand_name, all_products_data):
    """
    FASE 3: Navega a una colección y extrae los datos de sus productos.
    """
    driver.get(collection_url)
    print(f"\n      FASE 3: Accediendo a la colección: {collection_url}")
    
    while True:
        try:
            load_more_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-load-more")))
            driver.execute_script("arguments[0].scrollIntoView();", load_more_button)
            time.sleep(1)
            load_more_button.click()
            print("        -> Clic en 'Cargar más' productos...")
            time.sleep(2)
        except Exception:
            print("        -> No hay más productos que cargar.")
            break
            
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    
    product_containers = soup.select('div.product-snippet')
    print(f"        -> Se encontraron {len(product_containers)} productos.")
    
    for container in product_containers:
        try:
            name_element = container.select_one('meta[itemprop="name"]')
            name = name_element['content'].strip() if name_element else 'No disponible'
            desc_element = container.select_one('p.text-sm.mb-1\.5')
            description = desc_element.text.strip() if desc_element else 'No disponible'
            price_element = container.select_one('p span.font-bold')
            price = price_element.text.strip() if price_element else 'No disponible'
            link_element = container.select_one('a[title^="Ir a"]')
            link = link_element['href'] if link_element else 'No disponible'
            if link != 'No disponible' and not link.startswith('http'):
                link = BASE_DOMAIN + link
            stars_elements = container.select('div.testimonial img')
            stars = len(stars_elements) if stars_elements else 0
            reviews_element = container.select_one('div.testimonial p span.grey')
            raw_reviews_count = reviews_element.text.strip() if reviews_element else '(0)'
            reviews_count = raw_reviews_count.strip('()')
            color_elements = container.select('div.colour-list div.colour')
            colors = [color['title'] for color in color_elements if 'title' in color.attrs]
            colors_text = ', '.join(colors) if colors else 'No disponible'

            all_products_data.append([brand_name, name, description, price, stars, reviews_count, colors_text, link])
        except Exception as e:
            print(f"ADVERTENCIA: No se pudieron extraer datos de un producto. Error: {e}")
            continue

def main():
    """
    Función principal que orquesta todo el proceso de 3 fases.
    """
    print("Iniciando el proceso de scraping masivo...")
    
    service = Service(executable_path='chromedriver.exe')
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    
    # FASE 1: Obtener todas las marcas
    brands_data = get_brand_links(driver, URL_MARCAS)
    
    all_products_data = []
    # Bucle principal que itera sobre cada marca
    for brand in brands_data:
        brand_name = brand['name']
        brand_url = brand['url']
        
        # FASE 2: Obtener todas las colecciones para la marca actual
        collection_links = get_collection_links(driver, brand_url)
        
        # Bucle secundario que itera sobre cada colección
        for collection_url in collection_links:
            # FASE 3: Obtener todos los productos, pasando el nombre de la marca
            scrape_products_from_collection(driver, collection_url, brand_name, all_products_data)
            
    print(f"\nPROCESO COMPLETADO. Se encontraron un total de {len(all_products_data)} productos.")
    try:
        with open(CSV_FILENAME, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Marca', 'Nombre', 'Descripción', 'Precio', 'Valoración (Estrellas)', 'Número de Opiniones', 'Colores Disponibles', 'Enlace'])
            writer.writerows(all_products_data)
        print(f"¡ÉXITO! ✨ Se han guardado todos los productos en el archivo '{CSV_FILENAME}'")
    except IOError as e:
        print(f"\nERROR: No se pudo escribir en el archivo CSV. Error: {e}")

    driver.quit()

if __name__ == "__main__":
    main()