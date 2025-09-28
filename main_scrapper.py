import time
import json
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# --- IMPORTAMOS NUESTROS MÓDULOS EXPERTOS ---
from get_urls_by_brand import get_all_product_urls_from_brand
from producto_combinaciones_final import scrape_all_product_combinations

# --- CONFIGURACIÓN ---
BRAND_URL_TO_SCRAPE = "https://www.todomueblesdebano.com/marcas/sagobar/"
CSV_FILENAME = "reporte_final_marca_completo.csv"
WAIT_TIMEOUT = 10
PAUSE_DURATION = 2

def scrape_basic_product_details(soup):
    """Extrae los datos básicos visibles en la página de detalles de un producto."""
    details = {}
    
    details['Nombre'] = soup.select_one("h1 span.font-semibold").text.strip() if soup.select_one("h1 span.font-semibold") else 'No disponible'
    details['Subtitulo'] = soup.select_one("h1 span.subname").text.strip() if soup.select_one("h1 span.subname") else ''
    details['Precio Actual'] = soup.select_one("span.price").text.strip() if soup.select_one("span.price") else 'No disponible'
    details['Precio Antiguo'] = soup.select_one("span.line-through").text.strip() if soup.select_one("span.line-through") else ''
    details['Descuento'] = soup.select_one("span.bg-yellow-300").text.strip().replace('\n', '').replace(' ', '') if soup.select_one("span.bg-yellow-300") else ''
    details['Referencia'] = soup.select_one("div.ref-container").text.strip() if soup.select_one("div.ref-container") else 'No disponible'
    
    testimonial_div = soup.select_one("div.testimonial")
    if testimonial_div:
        rating_value_element = testimonial_div.select_one("span.bold.text-lg")
        if rating_value_element:
            details['Valoración'] = rating_value_element.text.strip()
        else:
            stars_elements = testimonial_div.select('img[alt="Trustpilot"]')
            details['Valoración'] = f"{len(stars_elements)}/5"

        opinions_element = testimonial_div.find("p", class_="mt-2 text-sm")
        details['Número de Opiniones'] = opinions_element.text.strip() if opinions_element else 'No disponible'
    else:
        details['Valoración'] = 'No disponible'
        details['Número de Opiniones'] = 'No disponible'
        
    return details

# --- NUEVA FUNCIÓN PARA EXTRAER IMÁGENES ---
def scrape_image_urls(soup):
    """
    Busca el carrusel de imágenes y extrae las URLs de todas las imágenes en alta resolución.
    """
    image_urls = []
    # Selector para encontrar las etiquetas <img> dentro del carrusel de miniaturas
    image_elements = soup.select("div.swipe-carousel-content img")

    for img in image_elements:
        if img.has_attr('src'):
            # La URL en 'src' es de una miniatura. La modificamos para obtener la versión grande.
            # ej: .../c_fill,f_auto,h_80,q_auto,w_80/...
            # La cambiamos a: .../f_auto,q_auto/...
            thumbnail_url = img['src']
            parts = thumbnail_url.split('/')
            # Buscamos la parte de la URL con las transformaciones de imagen
            for i, part in enumerate(parts):
                if 'c_fill' in part or 'h_80' in part:
                    # Reemplazamos las transformaciones por unas más genéricas para alta calidad
                    parts[i] = 'f_auto,q_auto'
                    break
            
            high_res_url = '/'.join(parts)
            image_urls.append(high_res_url)
    
    # Devolvemos una sola cadena de texto con las URLs separadas por coma
    return ", ".join(image_urls) if image_urls else "No disponible"

def scrape_description_sidebar(driver):
    """Hace clic en 'Descripción', extrae el texto del panel y lo cierra."""
    try:
        print("    -> Buscando 'Descripción del producto'...")
        desc_button = WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH, "//h2[contains(., 'Descripción del producto')]"))
        )
        driver.execute_script("arguments[0].click();", desc_button)
        
        WebDriverWait(driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.body-sidebar")))
        print("    -> Panel de descripción abierto.")
        time.sleep(PAUSE_DURATION)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        desc_container = soup.select_one("div.body-sidebar div.text-base")
        description_text = desc_container.get_text(separator='\n', strip=True) if desc_container else "No disponible"
        
        close_button = driver.find_element(By.CSS_SELECTOR, "div.header-sidebar button[type='button']")
        driver.execute_script("arguments[0].click();", close_button)
        
        time.sleep(PAUSE_DURATION)
        print("    -> Panel de descripción cerrado.")
        return description_text
    except Exception:
        print("    -> No se encontró o no se pudo procesar la descripción completa.")
        return "No disponible"

def scrape_tech_sheet_sidebar(driver):
    """Hace clic en 'Ficha técnica', extrae los datos y enlaces del panel, y lo cierra."""
    tech_data_text = "No disponible"
    url_montaje = "No disponible"
    url_ficha = "No disponible"
    try:
        print("    -> Buscando 'Consulta la ficha técnica'...")
        sheet_button = WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH, "//h2[contains(., 'Consulta la ficha técnica')]"))
        )
        driver.execute_script("arguments[0].click();", sheet_button)

        WebDriverWait(driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.body-sidebar")))
        print("    -> Panel de ficha técnica abierto.")
        time.sleep(PAUSE_DURATION)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        tech_container = soup.select_one("div.product-description-component")
        if tech_container:
            tech_data_text = tech_container.get_text(separator='\n', strip=True)

        montaje_link = soup.find('a', string=lambda t: t and 'instrucciones de montaje' in t.lower().strip())
        if montaje_link:
            url_montaje = montaje_link['href']

        ficha_link = soup.find('a', string=lambda t: t and 'descargar ficha tecnica' in t.lower().strip())
        if ficha_link:
            url_ficha = ficha_link['href']

        close_button = driver.find_element(By.CSS_SELECTOR, "div.header-sidebar button[type='button']")
        driver.execute_script("arguments[0].click();", close_button)
        
        time.sleep(PAUSE_DURATION)
        print("    -> Panel de ficha técnica cerrado.")

    except Exception:
        print("    -> No se encontró o no se pudo procesar la ficha técnica.")
    
    return tech_data_text, url_montaje, url_ficha

# --- FUNCIÓN PRINCIPAL / ORQUESTADOR ---
def main():
    print(f"--- INICIANDO SCRAPER MASIVO PARA LA MARCA: {BRAND_URL_TO_SCRAPE} ---")
    service = Service(executable_path='chromedriver.exe')
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()

    product_urls_with_context = get_all_product_urls_from_brand(driver, BRAND_URL_TO_SCRAPE)
    all_products_final_data = []

    for product_info in product_urls_with_context:
        product_url = product_info['url']
        brand_name = product_info['marca']
        collection_name = product_info['coleccion']
        
        print(f"\n--- PROCESANDO PRODUCTO: {product_url} ---")
        driver.get(product_url)
        time.sleep(2)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        basic_details = scrape_basic_product_details(soup)
        image_urls = scrape_image_urls(soup) # <-- LLAMAMOS A LA NUEVA FUNCIÓN
        combinations_data = scrape_all_product_combinations(driver, product_url)
        full_description = scrape_description_sidebar(driver)
        time.sleep(1)
        tech_sheet_text, montaje_url, ficha_url = scrape_tech_sheet_sidebar(driver)
        
        final_product_data = {
            'Marca': brand_name,
            'Coleccion': collection_name,
            'Nombre': basic_details.get('Nombre', 'No disponible'),
            'Subtitulo': basic_details.get('Subtitulo', ''),
            'Referencia': basic_details.get('Referencia', ''),
            'Precio Actual': basic_details.get('Precio Actual', 'No disponible'),
            'Precio Antiguo': basic_details.get('Precio Antiguo', ''),
            'Descuento': basic_details.get('Descuento', ''),
            'Valoración': basic_details.get('Valoración', 'No disponible'),
            'Número de Opiniones': basic_details.get('Número de Opiniones', 'No disponible'),
            'Image URLs': image_urls, # <-- AÑADIMOS LA NUEVA COLUMNA
            'Combinaciones (JSON)': json.dumps(combinations_data, ensure_ascii=False),
            'Descripción Completa': json.dumps(full_description, ensure_ascii=False),
            'Ficha Técnica': json.dumps(tech_sheet_text, ensure_ascii=False),
            'URL Instrucciones Montaje': montaje_url,
            'URL Ficha Tecnica': ficha_url,
            'Enlace': product_url
        }
        all_products_final_data.append(final_product_data)

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