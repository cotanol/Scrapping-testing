import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# --- CONFIGURACIÓN ---
URL_BASE = "https://www.todomueblesdebano.com/marcas/royo/"
CSV_FILENAME = 'productos_royo_completos_detallado.csv'

def get_collection_links(driver, url):
    """
    Fase 1: Navega a la URL principal, hace clic en "Ver más colecciones" 
    y extrae todos los enlaces a las páginas de cada colección.
    """
    driver.get(url)
    print(f"Accediendo a la página principal de la marca: {url}")
    
    try:
        print("Buscando y aceptando el banner de cookies...")
        accept_cookies_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "accept-cookies"))
        )
        accept_cookies_button.click()
        print("Cookies aceptadas.")
    except Exception:
        print("No se encontró el banner de cookies o ya fue aceptado.")
        
    print("Buscando y haciendo clic en 'Ver más colecciones'...")
    while True:
        try:
            load_more_collections_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.load-more"))
            )
            driver.execute_script("arguments[0].scrollIntoView();", load_more_collections_button)
            time.sleep(1)
            load_more_collections_button.click()
            print("Botón 'Ver más colecciones' presionado.")
            time.sleep(2)
        except Exception:
            print("No se encontró más el botón 'Ver más colecciones'.")
            break
            
    print("\nExtrayendo enlaces de todas las colecciones...")
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    
    collection_links = []
    link_elements = soup.select("a[title^='Ver Colección']")
    
    base_url = "https://www.todomueblesdebano.com"
    for link in link_elements:
        href = link.get('href')
        if href:
            full_url = base_url + href
            if full_url not in collection_links:
                collection_links.append(full_url)
                
    print(f"Se encontraron {len(collection_links)} enlaces de colecciones.")
    return collection_links

def scrape_products_from_collection(driver, url, all_products_data):
    """
    Fase 2: Navega a la URL de una colección y extrae TODOS los datos detallados de sus productos.
    """
    driver.get(url)
    print(f"\n--- Accediendo a la colección: {url} ---")
    
    while True:
        try:
            load_more_products_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-load-more"))
            )
            driver.execute_script("arguments[0].scrollIntoView();", load_more_products_button)
            time.sleep(1)
            load_more_products_button.click()
            print("Botón 'Cargar más' (productos) presionado.")
            time.sleep(2)
        except Exception:
            print("No se encontró más el botón 'Cargar más' (productos) en esta página.")
            break
            
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    
    product_containers = soup.select('div.product-snippet')
    print(f"Se encontraron {len(product_containers)} productos en esta colección.")
    
    for container in product_containers:
        try:
            # --- EXTRACCIÓN DE DATOS MEJORADA ---

            # Nombre (desde metaetiqueta, más fiable)
            name_element = container.select_one('meta[itemprop="name"]')
            name = name_element['content'].strip() if name_element else 'No disponible'

            # Descripción corta
            desc_element = container.select_one('p.text-sm.mb-1\.5')
            description = desc_element.text.strip() if desc_element else 'No disponible'
            
            # Precio
            price_element = container.select_one('p span.font-bold')
            price = price_element.text.strip() if price_element else 'No disponible'
            
            # Enlace
            link_element = container.select_one('a[title^="Ir a"]')
            link = link_element['href'] if link_element else 'No disponible'
            base_url = "https://www.todomueblesdebano.com"
            if link != 'No disponible' and not link.startswith('http'):
                link = base_url + link

            # Valoración (conteo de estrellas)
            stars_elements = container.select('div.testimonial img')
            stars = len(stars_elements) if stars_elements else 0
            
            # Número de opiniones
            reviews_element = container.select_one('div.testimonial p span.grey')
            reviews_count = reviews_element.text.strip() if reviews_element else '(0)'

            # Colores (se unen en un solo texto)
            color_elements = container.select('div.colour-list div.colour')
            colors = [color['title'] for color in color_elements if 'title' in color.attrs]
            colors_text = ', '.join(colors) if colors else 'No disponible'

            # Se añaden todos los datos a la lista principal
            all_products_data.append([name, description, price, link, stars, reviews_count, colors_text])

        except Exception as e:
            print(f"ADVERTENCIA: No se pudieron extraer todos los datos de un producto. Error: {e}")
            continue

def main():
    """
    Función principal que orquesta todo el proceso.
    """
    print("Iniciando el proceso de scraping...")
    
    service = Service(executable_path='chromedriver.exe')
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    
    collection_links = get_collection_links(driver, URL_BASE)
    
    all_products_data = []
    for link in collection_links:
        scrape_products_from_collection(driver, link, all_products_data)
        
    print(f"\nProceso completado. Se encontraron un total de {len(all_products_data)} productos.")
    try:
        with open(CSV_FILENAME, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Escribimos las nuevas cabeceras del CSV
            writer.writerow(['Nombre', 'Descripción', 'Precio', 'Enlace', 'Valoración (Estrellas)', 'Número de Opiniones', 'Colores Disponibles'])
            writer.writerows(all_products_data)
        print(f"¡ÉXITO! ✨ Se han guardado todos los productos en el archivo '{CSV_FILENAME}'")
    except IOError as e:
        print(f"\nERROR: No se pudo escribir en el archivo CSV. Error: {e}")

    driver.quit()

if __name__ == "__main__":
    main()