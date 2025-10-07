"""
Módulo para extraer complementos de productos desde la API de Decorabano
y generar CSV para importación en PrestaShop
"""

import json
import csv
import re
import time
import requests
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ================================
# CONFIGURACIÓN
# ================================
TAX_RATE = 1.21
COMPLEMENT_START_ID = 5001  # IDs de PrestaShop para complementos

# Mapeo de tipos de complementos a categorías de PrestaShop (según imagen)
COMPLEMENT_CATEGORY_MAP = {
    'grifos': 11,           # Grifos de baño
    'espejos': 12,          # Espejos de baño
    'lavabos': 15,          # Lavabos de baño
    'accesorios': 16,       # Accesorios de baño
    'columnas': 17,         # Columnas y auxiliares de baño
    'iluminación': 18,      # Iluminación de baño
    'válvulas': 19,         # Válvulas y Sifones de lavabo de baño
    'sifones': 19,          # Válvulas y Sifones de lavabo de baño
    'otros': 16             # Por defecto: Accesorios de baño
}

# ================================
# FUNCIONES PARA LIMPIAR TEXTO
# ================================
def clean_html_text(text):
    """Limpia texto HTML removiendo saltos de línea y caracteres problemáticos para CSV"""
    if not text or text is None:
        return ""
    text = str(text)
    cleaned = text.replace('&nbsp;', ' ')
    cleaned = cleaned.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    cleaned = cleaned.replace('"', '').replace(';', ',')
    cleaned = cleaned.replace('|', '-').replace('\x00', '').replace('\x0b', '').replace('\x0c', '')
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip()

def clean_dimension_value(value):
    """Limpia valores de dimensiones para que sean compatibles con PrestaShop"""
    if not value or value is None:
        return ""
    value = str(value).strip()
    value = value.replace(' cm', '').replace('cm', '').replace(' ', '')
    if not value:
        return ""
    try:
        float_val = float(value.replace(',', '.'))
        return str(float_val)
    except (ValueError, TypeError):
        return ""

# ================================
# FUNCIONES DE API CON PARÁMETROS CORRECTOS
# ================================
def get_complement_types(product_uuid):
    """
    Obtiene los tipos de complementos disponibles para un producto
    desde la API de Decorabano CON los parámetros store y language
    """
    url = f"https://api.decorabano.com/catalog/v1/products/{product_uuid}/complement_types/"
    params = {
        'store': 'ESTM',
        'language': 'es'
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # La respuesta viene en formato {"complement_types": [...]}
            return data.get('complement_types', [])
        else:
            print(f"    [!] API complement_types retornó status {response.status_code}")
            return []
    except Exception as e:
        print(f"    [ERROR] Error llamando API complement_types: {e}")
        return []

def get_complements_by_type(product_uuid, complement_type_id):
    """
    Obtiene los complementos de un tipo específico para un producto
    """
    url = f"https://api.decorabano.com/catalog/v1/products/{product_uuid}/complements/"
    params = {
        'store': 'ESTM',
        'language': 'es',
        'complement_type': complement_type_id
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            # La respuesta es directamente un array de complementos
            return response.json()
        else:
            print(f"    [!] API complements retornó status {response.status_code}")
            return []
    except Exception as e:
        print(f"    [ERROR] Error llamando API complements: {e}")
        return []

# ================================
# FUNCIONES PARA GENERAR CLAVES ÚNICAS
# ================================
def generate_unique_key(complement_data):
    """
    Genera una clave única para identificar complementos duplicados.
    Prioridad: REF > SLUG > NAME
    """
    ref = complement_data.get('ref', '')
    if ref and str(ref).strip():
        return f"REF:{ref}", "by_ref"
    
    slug = complement_data.get('slug', '')
    if slug and str(slug).strip():
        return f"SLUG:{slug}", "by_slug"
    
    name = complement_data.get('name', '')
    if name and str(name).strip():
        # Normalizar nombre para evitar duplicados por espacios/mayúsculas
        normalized_name = re.sub(r'\s+', ' ', str(name).lower())
        return f"NAME:{normalized_name}", "by_name"
    
    # Si no hay ningún identificador, usar UUID (aunque debería ser raro)
    uuid = complement_data.get('id', '') or complement_data.get('uuid', '') or complement_data.get('product_id', '')
    return f"UUID:{uuid}", "by_uuid"

def get_complement_category(complement_type_name):
    """
    Determina la categoría de PrestaShop según el tipo de complemento
    Mapeo basado en los nombres que devuelve la API
    """
    type_lower = complement_type_name.lower()
    
    # Grifos compatibles → ID 11
    if 'grifo' in type_lower or 'faucet' in type_lower or 'tap' in type_lower:
        return COMPLEMENT_CATEGORY_MAP['grifos']
    
    # Espejos compatibles → ID 12
    elif 'espejo' in type_lower or 'mirror' in type_lower:
        return COMPLEMENT_CATEGORY_MAP['espejos']
    
    # Lavabos → ID 15
    elif 'lavabo' in type_lower or 'sink' in type_lower or 'basin' in type_lower:
        return COMPLEMENT_CATEGORY_MAP['lavabos']
    
    # Accesorios de baño → ID 16
    elif 'accesorio' in type_lower or 'accessory' in type_lower:
        return COMPLEMENT_CATEGORY_MAP['accesorios']
    
    # Columnas y auxiliares → ID 17
    elif 'columna' in type_lower or 'column' in type_lower or 'auxiliar' in type_lower:
        return COMPLEMENT_CATEGORY_MAP['columnas']
    
    # Iluminación → ID 18
    elif 'luz' in type_lower or 'iluminación' in type_lower or 'light' in type_lower or 'iluminacion' in type_lower:
        return COMPLEMENT_CATEGORY_MAP['iluminación']
    
    # Válvulas y Sifones → ID 19
    elif 'válvula' in type_lower or 'valvula' in type_lower or 'sifon' in type_lower or 'sifón' in type_lower:
        return COMPLEMENT_CATEGORY_MAP['válvulas']
    
    # Por defecto: Accesorios de baño (ID 16)
    else:
        return COMPLEMENT_CATEGORY_MAP['otros']

# ================================
# CABECERAS CSV PRESTASHOP
# ================================
PRODUCT_CSV_HEADERS = [
    'Product ID','Active (0/1)','Name *','Categories (x,y,z...)','Price tax excluded','Tax rules ID','Wholesale price',
    'On sale (0/1)','Discount amount','Discount percent','Discount from (yyyy-mm-dd)','Discount to (yyyy-mm-dd)',
    'Reference #','Supplier reference #','Supplier','Manufacturer','EAN13','UPC','MPN','Ecotax','Width','Height','Depth',
    'Weight','Delivery time of in-stock products','Delivery time of out-of-stock products with allowed orders',
    'Quantity','Minimal quantity','Low stock level','Send me an email when the quantity is under this level',
    'Visibility','Additional shipping cost','Unity','Unit price','Summary','Description','Tags (x,y,z...)',
    'Meta title','Meta keywords','Meta description','URL rewritten','Text when in stock','Text when backorder allowed',
    'Available for order (0 = No, 1 = Yes)','Product available date','Product creation date',
    'Show price (0 = No, 1 = Yes)','Image URLs (x,y,z...)','Image alt texts (x,y,z...)',
    'Delete existing images (0 = No, 1 = Yes)','Feature(Name:Value:Position)','Available online only (0 = No, 1 = Yes)',
    'Condition','Customizable (0 = No, 1 = Yes)','Uploadable files (0 = No, 1 = Yes)','Text fields (0 = No, 1 = Yes)',
    'Out of stock action','Virtual product','File URL','Number of allowed downloads','Expiration date','Number of days',
    'ID / Name of shop','Advanced stock management','Depends On Stock','Warehouse','Acessories  (x,y,z...)'
]

# ================================
# EXTRACCIÓN DE COMPLEMENTOS
# ================================
def extract_complements_from_product(driver, product_url):
    """
    Extrae todos los complementos de un producto individual usando la API
    con los parámetros correctos (store=ESTM&language=es)
    Retorna: lista de complementos con sus datos completos
    """
    try:
        # Cargar la página del producto
        driver.get(product_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "__nuxt")))
        
        # Extraer datos __NUXT__
        nuxt_data = driver.execute_script("return window.__NUXT__;")
        product_data = nuxt_data['state']['product']['product']
        
        # Extraer UUID del producto
        product_uuid = product_data.get('id', '') or product_data.get('uuid', '')
        product_name = product_data.get('name', 'Unknown')
        
        if not product_uuid:
            print(f"    [!] No se encontró UUID para el producto")
            return []
        
        print(f"    >> {product_name}")
        print(f"       UUID: {product_uuid}")
        
        # Obtener tipos de complementos desde la API (con parámetros correctos)
        complement_types = get_complement_types(product_uuid)
        
        if not complement_types or not isinstance(complement_types, list):
            print(f"       [i] No hay complementos disponibles")
            return []
        
        all_complements = []
        
        # Para cada tipo de complemento, obtener los complementos
        for comp_type in complement_types:
            type_id = comp_type.get('id')
            type_name = comp_type.get('web_name', 'Unknown')
            
            print(f"       - Tipo: {type_name} (ID: {type_id})")
            
            complements_data = get_complements_by_type(product_uuid, type_id)
            
            if complements_data and isinstance(complements_data, list):
                for complement in complements_data:
                    # Validar que sea un diccionario válido
                    if not isinstance(complement, dict):
                        continue
                    
                    # Añadir información del tipo al complemento
                    complement['complement_type_name'] = type_name
                    complement['complement_type_id'] = type_id
                    all_complements.append(complement)
                
                print(f"         >> {len(complements_data)} complementos encontrados")
            else:
                print(f"         [!] No se pudieron obtener complementos de este tipo")
        
        return all_complements
        
    except Exception as e:
        print(f"    [ERROR] Error extrayendo complementos: {e}")
        return []

def extract_all_complements(driver, product_urls):
    """
    Extrae TODOS los complementos únicos de una lista de URLs de productos.
    
    Retorna:
        - unique_complements: dict con complementos únicos {unique_key: complement_data}
        - complement_mapping: dict que mapea product_uuid a lista de complement_keys
        - key_to_uuid: dict que mapea unique_key a complement_uuid
        - stats: estadísticas del proceso
    """
    print(f"\n[PASO 2] Extrayendo complementos de cada producto...")
    
    unique_complements = {}  # {unique_key: complement_data}
    complement_mapping = {}  # {product_uuid: [list of unique_keys]}
    key_to_uuid = {}  # {unique_key: complement_uuid}
    
    # Estadísticas
    stats = {
        'total_products_processed': 0,
        'total_products_with_complements': 0,
        'total_complements_extracted': 0,
        'total_unique_complements': 0,
        'unique_keys_by_type': {'by_ref': 0, 'by_slug': 0, 'by_name': 0, 'by_uuid': 0}
    }
    
    for i, product_url in enumerate(product_urls, 1):
        print(f"\n  [{i}/{len(product_urls)}] {product_url}")
        
        try:
            # Obtener el UUID del producto primero
            driver.get(product_url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "__nuxt")))
            nuxt_data = driver.execute_script("return window.__NUXT__;")
            product_data = nuxt_data['state']['product']['product']
            product_uuid = product_data.get('id', '') or product_data.get('uuid', '')
            
            # Extraer complementos
            complements = extract_complements_from_product(driver, product_url)
            
            stats['total_products_processed'] += 1
            stats['total_complements_extracted'] += len(complements)
            
            if complements:
                stats['total_products_with_complements'] += 1
                complement_mapping[product_uuid] = []
                
                for complement in complements:
                    # Generar clave única
                    unique_key, key_type = generate_unique_key(complement)
                    
                    # Si es la primera vez que vemos este complemento, guardarlo
                    if unique_key not in unique_complements:
                        unique_complements[unique_key] = complement
                        complement_uuid = complement.get('id', '') or complement.get('uuid', '')
                        key_to_uuid[unique_key] = complement_uuid
                        stats['unique_keys_by_type'][key_type] += 1
                    
                    # Mapear este complemento al producto
                    if unique_key not in complement_mapping[product_uuid]:
                        complement_mapping[product_uuid].append(unique_key)
            
        except Exception as e:
            print(f"    [ERROR] Error procesando producto: {e}")
            continue
        
        time.sleep(1)  # Pausa entre productos
    
    stats['total_unique_complements'] = len(unique_complements)
    
    return unique_complements, complement_mapping, key_to_uuid, stats

# ================================
# GENERACIÓN DE CSV
# ================================
def convert_complement_to_prestashop_format(complement_data, prestashop_id):
    """
    Convierte datos de un complemento de la API al formato de PrestaShop CSV
    """
    # Extraer datos básicos (estructura de la API real)
    name = complement_data.get('name', '')
    ref = complement_data.get('ref', '')
    slug = complement_data.get('slug', '')
    complement_type_name = complement_data.get('complement_type_name', 'Complemento')
    
    # Precios (vienen en centavos en la API)
    price_cents = complement_data.get('price', 0)  # precio con descuento
    pvp_supplier_cents = complement_data.get('pvp_supplier', 0)  # precio sin descuento
    
    price_final = price_cents / 100
    price_tax_excluded = round(price_final / TAX_RATE, 6) if price_final > 0 else 0
    
    # Descuentos
    on_sale = 1 if pvp_supplier_cents > price_cents else 0
    discount_amount = round((pvp_supplier_cents - price_cents) / 100, 2) if on_sale else 0
    web_discount = complement_data.get('web_discount', 0)
    
    # Categoría según tipo de complemento
    category_id = get_complement_category(complement_type_name)
    
    # Imágenes - el campo 'img' contiene el public_id de Cloudinary
    img_public_id = complement_data.get('img', '')
    image_url = ""
    if img_public_id:
        image_url = f"https://cdn.todomueblesdebano.com/image/upload/f_auto%2Cq_auto/v1/{img_public_id}"
    
    # EAN
    ean = complement_data.get('ean', '')
    
    # Brand/Supplier
    brand = complement_data.get('brand', '') or complement_data.get('main_brand', '')
    
    # Descripción básica
    sub_name = complement_data.get('sub_name', '')
    description = f"{name} {sub_name}".strip()
    
    # Limitar campos largos
    if slug and len(slug) > 128:
        slug = slug[:128]
    if description and len(description) > 800:
        short_description = description[:800] + '...'
    else:
        short_description = description
    
    # Tags
    tags = ['complemento', 'baño', complement_type_name.lower()]
    if brand:
        tags.append(brand.lower())
    
    # Delivery time
    delivery_time_data = complement_data.get('delivery_time', {})
    delivery_time = ""
    if delivery_time_data:
        min_days = delivery_time_data.get('min', '')
        max_days = delivery_time_data.get('max', '')
        if min_days and max_days:
            delivery_time = f"Entre {min_days} y {max_days} días"
    
    return {
        'Product ID': prestashop_id,
        'Active (0/1)': 1,
        'Name *': clean_html_text(name),
        'Categories (x,y,z...)': str(category_id),
        'Price tax excluded': price_tax_excluded,
        'Tax rules ID': 1,
        'Wholesale price': '',
        'On sale (0/1)': on_sale,
        'Discount amount': discount_amount if on_sale else '',
        'Discount percent': web_discount if on_sale else '',
        'Discount from (yyyy-mm-dd)': '',
        'Discount to (yyyy-mm-dd)': '',
        'Reference #': ref,
        'Supplier reference #': '',
        'Supplier': clean_html_text(brand),
        'Manufacturer': clean_html_text(brand),
        'EAN13': ean,
        'UPC': '',
        'MPN': complement_data.get('mpn', ''),
        'Ecotax': '',
        'Width': '',
        'Height': '',
        'Depth': '',
        'Weight': 0,
        'Delivery time of in-stock products': clean_html_text(delivery_time),
        'Delivery time of out-of-stock products with allowed orders': '',
        'Quantity': 100,
        'Minimal quantity': 1,
        'Low stock level': '',
        'Send me an email when the quantity is under this level': 0,
        'Visibility': 'both',
        'Additional shipping cost': '',
        'Unity': '',
        'Unit price': '',
        'Summary': clean_html_text(short_description),
        'Description': clean_html_text(description),
        'Tags (x,y,z...)': ",".join(list(set(tags))),
        'Meta title': clean_html_text(name),
        'Meta keywords': '',
        'Meta description': clean_html_text(description),
        'URL rewritten': slug,
        'Text when in stock': 'Disponible',
        'Text when backorder allowed': '',
        'Available for order (0 = No, 1 = Yes)': 1,
        'Product available date': '',
        'Product creation date': '',
        'Show price (0 = No, 1 = Yes)': 1,
        'Image URLs (x,y,z...)': image_url,
        'Image alt texts (x,y,z...)': '',
        'Delete existing images (0 = No, 1 = Yes)': 1,
        'Feature(Name:Value:Position)': '',
        'Available online only (0 = No, 1 = Yes)': 0,
        'Condition': 'new',
        'Customizable (0 = No, 1 = Yes)': 0,
        'Uploadable files (0 = No, 1 = Yes)': 0,
        'Text fields (0 = No, 1 = Yes)': 0,
        'Out of stock action': 0,
        'Virtual product': 0,
        'File URL': '',
        'Number of allowed downloads': '',
        'Expiration date': '',
        'Number of days': '',
        'ID / Name of shop': 1,
        'Advanced stock management': 0,
        'Depends On Stock': 0,
        'Warehouse': 0,
        'Acessories  (x,y,z...)': ''
    }

def generate_complements_csv(unique_complements, timestamp):
    """
    Genera el CSV de complementos para importar en PrestaShop.
    
    Retorna:
        - filename: nombre del archivo CSV generado
        - key_to_prestashop_id: mapeo de unique_key a PrestaShop ID
    """
    print(f"\n[PASO 3] Generando CSV de complementos...")
    
    filename = f'{timestamp}-royo-complements_import.csv'
    key_to_prestashop_id = {}
    all_complements_data = []
    
    current_id = COMPLEMENT_START_ID
    
    for unique_key, complement_data in unique_complements.items():
        # Convertir a formato PrestaShop
        prestashop_data = convert_complement_to_prestashop_format(complement_data, current_id)
        all_complements_data.append(prestashop_data)
        
        # Mapear la clave única al ID de PrestaShop
        key_to_prestashop_id[unique_key] = current_id
        
        current_id += 1
    
    # Escribir CSV
    if all_complements_data:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=PRODUCT_CSV_HEADERS, delimiter=';', quoting=csv.QUOTE_ALL)
            writer.writeheader()
            writer.writerows(all_complements_data)
        
        print(f"[OK] {filename} generado ({len(all_complements_data)} complementos únicos)")
        print(f"     IDs asignados: {COMPLEMENT_START_ID} - {current_id - 1}")
    
    return filename, key_to_prestashop_id

# ================================
# FUNCIÓN PRINCIPAL PARA TESTING
# ================================
if __name__ == "__main__":
    print("=" * 80)
    print("MÓDULO DE EXTRACCIÓN DE COMPLEMENTOS")
    print("=" * 80)
    print("\nEste módulo se debe usar importándolo desde el script principal.")
    print("Ejemplo de uso:")
    print("""
    from get_complementos import extract_all_complements, generate_complements_csv
    
    # Después de obtener las URLs de productos:
    unique_complements, complement_mapping, key_to_uuid, stats = extract_all_complements(driver, product_urls)
    complements_csv, key_to_prestashop_id = generate_complements_csv(unique_complements, timestamp)
    """)
