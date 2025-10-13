import json
import csv
import re
import time
import os
from datetime import datetime
from ftplib import FTP
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Importamos el módulo para obtener URLs
from get_urls_by_brand import get_all_product_urls_from_brand

# ================================
# 1. FUNCIÓN PARA LIMPIAR TEXTO HTML
# ================================
def clean_html_text(text):
    """Limpia texto HTML removiendo saltos de línea y caracteres problemáticos para CSV"""
    if not text or text is None:
        return ""
    # Convertir a string si no lo es
    text = str(text)
    
    # Reemplazar &nbsp; por espacios normales
    cleaned = text.replace('&nbsp;', ' ')
    
    # Remover caracteres HTML y problemáticos
    cleaned = cleaned.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    # Remover comillas dobles y punto y coma que rompen CSV
    cleaned = cleaned.replace('"', '').replace(';', ',')
    # Remover otros caracteres problemáticos
    cleaned = cleaned.replace('|', '-').replace('\x00', '').replace('\x0b', '').replace('\x0c', '')
    # Remover espacios múltiples
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip()

def clean_dimension_value(value):
    """Limpia valores de dimensiones para que sean compatibles con PrestaShop"""
    if not value or value is None:
        return ""
    
    # Convertir a string y limpiar
    value = str(value).strip()
    
    # Remover "cm" y otros textos
    value = value.replace(' cm', '').replace('cm', '').replace(' ', '')
    
    # Si queda vacío, devolver vacío
    if not value:
        return ""
    
    # Intentar convertir a float para validar que sea numérico
    try:
        float_val = float(value.replace(',', '.'))  # Cambiar comas por puntos
        return str(float_val)
    except (ValueError, TypeError):
        return ""  # Si no se puede convertir, devolver vacío

# --- CONFIGURACIÓN ---
BRAND_URL_TO_SCRAPE = "https://www.todomueblesdebano.com/marcas/royo/"
TAX_RATE = 1.21

# Generar nombres de archivo con fecha y hora
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
PRODUCT_OUTPUT_FILENAME = f'{timestamp}-royo-products_import.csv'
COMBINATION_OUTPUT_FILENAME = f'{timestamp}-royo-combinations_import.csv'

# --- CABECERAS CSV PRESTASHOP ---
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

COMBINATION_CSV_HEADERS = [
    'Id del Producto','Referencia del Producto','Atributo (Nombre:Tipo:Posicion)*','Valor (Valor:Posicion)*',
    'Ref proveedor','Referencia','EAN13','UPC','MPN','Precio de coste','Impacto en el precio','Ecotasa',
    'Cantidad','Cantidad minima','Nivel de stock bajo','Enviame un mensaje de correo electronico',
    'Impacto en el peso','Predeterminado (0=No, 1=Si)','Fecha de disponibilidad de la combinacion',
    'Elegir entre imagenes de productos por posicion(1,2,3)','URLs de las imagenes(x,y,z...)','Textos alternativos de imagen(x,y,z...)',
    'Id / Nombre de la tienda'
]

# ================================
# 1. FUNCIÓN FTP
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
        print(f"❌ Error al leer configuración FTP: {e}")
        return None

def subir_archivo_ftp(nombre_archivo, servidor, usuario, contraseña, ruta_remota="/"):
    try:
        ftp = FTP(servidor)
        ftp.login(usuario, contraseña)
        print(f"🔗 Conectado al FTP: {servidor}")
        
        directorio_actual = ftp.pwd()
        print(f"📁 Directorio actual: {directorio_actual}")
        
        if ruta_remota and ruta_remota != "/" and ruta_remota.strip():
            try:
                ftp.cwd(ruta_remota)
                print(f"📁 Cambiado a: {ruta_remota}")
            except Exception as e:
                print(f"⚠️  No se pudo cambiar a '{ruta_remota}': {e}")
                print(f"📁 Usando directorio actual: {directorio_actual}")
        
        with open(nombre_archivo, 'rb') as archivo:
            ftp.storbinary(f'STOR {nombre_archivo}', archivo)
        
        print(f"✅ Archivo '{nombre_archivo}' subido correctamente al FTP.")
        ftp.quit()
        return True
    except Exception as e:
        print(f"❌ Error al subir '{nombre_archivo}' al FTP: {e}")
        return False

# ================================
# 2. EXTRACCIÓN DATOS PRESTASHOP
# ================================
def extract_product_data(nuxt_data, numeric_product_id, driver=None):
    try:
        product_data = nuxt_data['state']['product']['product']
        prices = product_data.get('prices', {})
        seo_data = product_data.get('seo', {})
        technical_data = nuxt_data['state']['product'].get('technical_data', [])
        
        # Extraer complementos (espejos, grifos, etc.)
        configuration = nuxt_data.get('state', {}).get('product', {}).get('configuration', {})
        complements = configuration.get('options', {}).get('complements', [])
        
    except (KeyError, TypeError): 
        return None

    tech_data_map = {item['attribute']['name'].lower(): item['options'][0]['option']['value_string'] 
                     for item in technical_data if item.get('attribute') and item.get('options')}
    
    # EXTRAER PRECIO VISUAL DEL HTML (precio ORIGINAL sin descuento, para que PrestaShop aplique el descuento)
    price_with_tax = 0
    if driver:
        try:
            # Primero intentar obtener el precio TACHADO (precio original sin descuento)
            # Este es el precio que debe ir en "Price tax excluded" para que PrestaShop aplique el descuento
            try:
                original_price_element = driver.find_element(By.CSS_SELECTOR, "span.line-through")
                price_text = original_price_element.text.strip()
                print(f"    🏷️  Precio ORIGINAL (tachado) encontrado: {price_text}")
            except:
                # Si no hay precio tachado, usar el precio normal (producto sin descuento)
                price_element = driver.find_element(By.CSS_SELECTOR, "span.price")
                price_text = price_element.text.strip()
                print(f"    💰 Precio (sin descuento en web): {price_text}")
            
            # Extraer número del texto (ej: "609,84€" → 609.84)
            # Reemplazar separador de miles (.) y decimal (,) al formato estándar
            price_text_clean = price_text.replace('€', '').strip()
            
            # Si tiene punto como separador de miles y coma como decimal: "1.234,56" → "1234.56"
            if ',' in price_text_clean and '.' in price_text_clean:
                price_text_clean = price_text_clean.replace('.', '').replace(',', '.')
            # Si solo tiene coma como decimal: "609,84" → "609.84"
            elif ',' in price_text_clean:
                price_text_clean = price_text_clean.replace(',', '.')
            
            price_with_tax = float(price_text_clean)
            print(f"    💰 Precio extraído (ORIGINAL con IVA): {price_with_tax}€")
        except Exception as e:
            print(f"    ⚠️  No se pudo extraer precio visual, usando pvp_web del __NUXT__")
    
    # Si se obtuvo precio visual (con IVA), calcular precio sin IVA
    if price_with_tax > 0:
        price_tax_excluded = round(price_with_tax / TAX_RATE, 6)
        price_final = price_with_tax  # Para cálculo de descuentos
    else:
        # Fallback: usar precio del __NUXT__
        price_final = prices.get('pvp_web', 0) / 100
        price_tax_excluded = round(price_final / TAX_RATE, 6) if price_final > 0 else 0
    
    on_sale = 1 if prices.get('pvp_supplier', 0) > prices.get('pvp_web', 0) else 0
    discount_amount = round((prices.get('pvp_supplier', 0) - prices.get('pvp_web', 0)) / 100, 2) if on_sale else 0

    # Usar categoría ID 13 de PrestaShop
    categories_str = "13"
    
    images_list = product_data.get('images', [])
    # Filtrar imagen problemática y generar URLs
    problematic_image = "products/f96cbc2f-a08e-4832-9d62-8cdeae03c4f2/Vitale_DetallePatas_1668600799.0959315"
    filtered_images = [
        f"https://cdn.todomueblesdebano.com/image/upload/f_auto%2Cq_auto/v1/{img['public_id']}" 
        for img in images_list 
        if img['public_id'] != problematic_image
    ]
    image_urls = ",".join(filtered_images)
    
    # Extraer características técnicas
    features_list = [f"{clean_html_text(item['attribute']['name'])}:{clean_html_text(item['options'][0]['option']['value_string'])}:{item.get('position', 0)}"
                     for item in technical_data if item.get('attribute') and item.get('options')]
    
    # Añadir complementos como características adicionales
    if complements:
        for complement_group in complements:
            group_name = complement_group.get('name', 'Complementos')
            options = complement_group.get('options', [])
            if options:
                complement_names = [opt.get('name', '') for opt in options if opt.get('name')]
                if complement_names:
                    # Añadir como una característica especial
                    features_list.append(f"{clean_html_text(group_name)}:Disponible ({', '.join(complement_names[:3])}):999")

    tags = list(set([word.lower() for word in re.split(r'\s|,', product_data.get('name', '')) if len(word) > 3]))
    tags.append("muebles")
    tags.append("baño")
    tags.append(product_data.get('supplier', {}).get('name', '').lower())

    delivery_time_obj = product_data.get('delivery_time', {})
    delivery_time = f"Entre {delivery_time_obj.get('min', '?')} y {delivery_time_obj.get('max', '?')} días" if delivery_time_obj else ""

    files_list = product_data.get('files', [])
    file_url = next((f['url'] for f in files_list if f.get('file_type') == 'data_sheet'), '')

    # Limitar URL rewritten a 128 caracteres máximo
    url_slug = product_data.get('slug', '') or ''
    if url_slug and len(url_slug) > 128:
        url_slug = url_slug[:128]

    # Construir Summary a partir de sub_name + differential_values
    sub_name = product_data.get('sub_name', '')
    differential_values = seo_data.get('differential_values', '')
    
    # Combinar sub_name y differential_values con coma
    if sub_name and differential_values:
        summary_text = f"{sub_name}, {differential_values}"
    elif sub_name:
        summary_text = sub_name
    elif differential_values:
        summary_text = differential_values
    else:
        # Fallback a short_description si no hay sub_name ni differential_values
        summary_text = seo_data.get('short_description', '') or ''
        if summary_text and len(summary_text) > 800:
            summary_text = summary_text[:800] + '...'

    return {
        'Product ID': numeric_product_id, 'Active (0/1)': 1, 'Name *': clean_html_text(product_data.get('name', '')),
        'Categories (x,y,z...)': categories_str, 'Price tax excluded': price_tax_excluded, 'Tax rules ID': 1,
        'Wholesale price': '', 'On sale (0/1)': on_sale, 'Discount amount': discount_amount if on_sale else '',
        'Discount percent': prices.get('web_discount', '') if on_sale else '', 'Discount from (yyyy-mm-dd)': '',
        'Discount to (yyyy-mm-dd)': '', 'Reference #': product_data.get('ref', ''), 'Supplier reference #': '',
        'Supplier': clean_html_text(product_data.get('supplier', {}).get('name', '')), 'Manufacturer': clean_html_text(product_data.get('supplier', {}).get('name', '')),
        'EAN13': product_data.get('ean', ''), 'UPC': '', 'MPN': '', 'Ecotax': '', 
        'Width': clean_dimension_value(tech_data_map.get('ancho seleccionable estándar', '')),
        'Height': clean_dimension_value(tech_data_map.get('alto seleccionable estándar', '')),
        'Depth': clean_dimension_value(tech_data_map.get('fondo seleccionable estándar', '')), 'Weight': 0,
        'Delivery time of in-stock products': clean_html_text(delivery_time),
        'Delivery time of out-of-stock products with allowed orders': '', 'Quantity': 0, 'Minimal quantity': 1,
        'Low stock level': '', 'Send me an email when the quantity is under this level': 0, 'Visibility': 'both',
        'Additional shipping cost': '', 'Unity': '', 'Unit price': '', 'Summary': clean_html_text(summary_text),
        'Description': clean_html_text(seo_data.get('description', '')), 'Tags (x,y,z...)': ",".join(list(set(tags))),
        'Meta title': clean_html_text(seo_data.get('meta_title', '')), 'Meta keywords': '', 'Meta description': clean_html_text(seo_data.get('meta_description', '')),
        'URL rewritten': url_slug, 'Text when in stock': 'Disponible', 'Text when backorder allowed': '',
        'Available for order (0 = No, 1 = Yes)': 1, 'Product available date': '', 'Product creation date': '',
        'Show price (0 = No, 1 = Yes)': 1, 'Image URLs (x,y,z...)': image_urls, 'Image alt texts (x,y,z...)': '',
        'Delete existing images (0 = No, 1 = Yes)': 1, 'Feature(Name:Value:Position)': ";".join(features_list),
        'Available online only (0 = No, 1 = Yes)': 0, 'Condition': 'new', 'Customizable (0 = No, 1 = Yes)': 0,
        'Uploadable files (0 = No, 1 = Yes)': 0, 'Text fields (0 = No, 1 = Yes)': 0, 'Out of stock action': 0,
        'Virtual product': 0 if not file_url else 1, 'File URL': file_url, 'Number of allowed downloads': '', 'Expiration date': '',
        'Number of days': '', 'ID / Name of shop': 1, 'Advanced stock management': 0, 'Depends On Stock': 0,
        'Warehouse': 0, 'Acessories  (x,y,z...)': ''
    }

def extract_combinations_data(nuxt_data, numeric_product_id):
    try:
        product_data = nuxt_data['state']['product']['product']
        variants = product_data.get('variants', [])
        if not variants: return []
        
        base_price_cents = product_data.get('prices', {}).get('pvp_web', 0)
        all_combinations = []
        
        # Obtener la URL de la imagen principal del producto (filtrar imagen problemática)
        images_list = product_data.get('images', [])
        main_image_url = ""
        problematic_image = "products/f96cbc2f-a08e-4832-9d62-8cdeae03c4f2/Vitale_DetallePatas_1668600799.0959315"
        
        if images_list:
            # Buscar la primera imagen válida (que no sea la problemática)
            for img in images_list:
                if img['public_id'] != problematic_image:
                    main_image_url = f"https://cdn.todomueblesdebano.com/image/upload/f_auto%2Cq_auto/v1/{img['public_id']}"
                    break
        
    except (KeyError, TypeError) as e:
        print(f"    ❌ Error extrayendo combinaciones: {e}")
        return []

    # Crear mapping de atributos de forma más directa desde las variantes
    # Examinar la primera variante para obtener los IDs y nombres de atributos
    attribute_mapping = {}
    if variants and len(variants) > 0:
        first_variant = variants[0]
        if 'options' in first_variant and 'options' in first_variant['options']:
            options_list = first_variant['options']['options']
            
            # Para cada opción en la primera variante, extraer información del atributo
            for index, option in enumerate(options_list):
                attr_id = option.get('attribute_id')
                if not attr_id:
                    continue
                
                # Intentar múltiples formas de obtener el nombre del atributo
                friendly_name = None
                
                # Método 1: Buscar en toda la lista de variantes un campo "attribute" con nombre
                for variant in variants[:5]:  # Revisar las primeras 5 variantes
                    for opt in variant.get('options', {}).get('options', []):
                        if opt.get('attribute_id') == attr_id:
                            # Intentar extraer nombre de diferentes ubicaciones
                            if 'attribute' in opt and isinstance(opt['attribute'], dict):
                                attr_name = opt['attribute'].get('name') or opt['attribute'].get('label')
                                if attr_name:
                                    friendly_name = clean_html_text(attr_name)
                                    break
                            # Intentar desde attribute_name
                            if not friendly_name and 'attribute_name' in opt:
                                friendly_name = clean_html_text(opt['attribute_name'])
                                break
                    if friendly_name:
                        break
                
                # Si no se encontró nombre, usar valor por defecto descriptivo
                if not friendly_name:
                    # Intentar inferir del tipo de valores (si son medidas, colores, etc.)
                    sample_value = option.get('name', '').lower()
                    if any(unit in sample_value for unit in ['cm', 'mm', 'm ']):
                        friendly_name = "Medida"
                    elif any(color in sample_value for color in ['blanco', 'negro', 'gris', 'azul', 'rojo', 'verde', 'amarillo', 'nogal', 'roble', 'wengue', 'antracita']):
                        friendly_name = "Acabado"
                    elif 'espejo' in sample_value:
                        friendly_name = "Espejo"
                    else:
                        friendly_name = f"Opción {index+1}"
                
                attribute_mapping[attr_id] = {"name": friendly_name, "type": "select", "position": index}
    
    attributes_header = ",".join([f"{v['name']}:{v['type']}:{v['position']}" for v in attribute_mapping.values()])

    default_assigned = False
    for index, variant in enumerate(variants):
        values_list = []
        for option in variant.get('options', {}).get('options', []):
            attr_id = option.get('attribute_id')
            if attr_id in attribute_mapping:
                pos = attribute_mapping[attr_id]['position']
                values_list.append(f"{option.get('name', '')}:{pos}")
        values_str = ",".join(sorted(values_list, key=lambda x: x.split(':')[1]))
        
        variant_price_cents = variant.get('prices', {}).get('pvp_web', 0)
        price_impact = round((variant_price_cents - base_price_cents) / 100, 6) if base_price_cents > 0 else 0
        
        is_default = 0
        if not default_assigned and price_impact == 0:
            is_default = 1
            default_assigned = True
        
        # Usar siempre la imagen principal del producto (posición 1) para todas las combinaciones
        image_position = 1
            
        all_combinations.append({
            'Id del Producto': numeric_product_id, 
            'Referencia del Producto': '', 
            'Atributo (Nombre:Tipo:Posicion)*': attributes_header,
            'Valor (Valor:Posicion)*': values_str, 
            'Ref proveedor': '', 
            'Referencia': variant.get('ref', ''), 
            'EAN13': variant.get('ean', ''),
            'UPC': '', 
            'MPN': '',
            'Precio de coste': '', 
            'Impacto en el precio': price_impact, 
            'Ecotasa': 0,
            'Cantidad': 100,
            'Cantidad minima': 1, 
            'Nivel de stock bajo': '', 
            'Enviame un mensaje de correo electronico': '',
            'Impacto en el peso': 0, 
            'Predeterminado (0=No, 1=Si)': is_default, 
            'Fecha de disponibilidad de la combinacion': '',
            'Elegir entre imagenes de productos por posicion(1,2,3)': '', 
            'URLs de las imagenes(x,y,z...)': '', 
            'Textos alternativos de imagen(x,y,z...)': '', 
            'Id / Nombre de la tienda': 1
        })
    return all_combinations

# ================================
# 3. FUNCIÓN PRINCIPAL INTEGRADA
# ================================
def main():
    print("🚀 INICIANDO: Scraper Royo + PrestaShop + FTP")
    print("=" * 50)
    
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--log-level=3")
    
    driver = None
    all_products_data = []
    all_combinations_data = []
    product_uuid_list = []  # Lista de (numeric_id, uuid) para luego obtener complementos
    
    try:
        # PASO 1: Obtener todas las URLs de productos
        print("🔍 PASO 1: Obteniendo URLs de productos...")
        service = Service(executable_path='chromedriver.exe')
        driver = webdriver.Chrome(service=service, options=options)
        
        product_urls_with_context = get_all_product_urls_from_brand(driver, BRAND_URL_TO_SCRAPE)
        print(f"✅ Se encontraron {len(product_urls_with_context)} productos")
        
        # PASO 2: UNA SOLA VISITA - Extraer productos + combinaciones + UUIDs
        print(f"\n🕷️ PASO 2: Procesando productos y recopilando UUIDs (1 VISITA por producto)...")
        for i, product_info in enumerate(product_urls_with_context, 1):
            product_url = product_info['url']
            numeric_product_id = 86 + i  # Empezar desde 87 (86+1=87)
            print(f"  [{i}/{len(product_urls_with_context)}] {product_url} (ID: {numeric_product_id})")
            
            try:
                driver.get(product_url)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "__nuxt")))
                nuxt_data = driver.execute_script("return window.__NUXT__;")
                
                # Obtener UUID del producto (usamos 'id' que es el UUID en __NUXT__)
                try:
                    product_uuid = nuxt_data['state']['product']['product']['id']
                except:
                    product_uuid = ''
                
                # Guardar UUID para luego obtener complementos
                if product_uuid:
                    product_uuid_list.append((numeric_product_id, product_uuid))
                
                # Extraer datos del producto (PASAMOS driver para obtener precio visual)
                product_data = extract_product_data(nuxt_data, numeric_product_id, driver)
                if product_data:
                    all_products_data.append(product_data)
                    print(f"    ✅ Producto procesado (UUID: {product_uuid[:8]}...)")
                else:
                    print(f"    ⚠️  No se pudieron extraer datos del producto")
                
                # Extraer combinaciones
                combinations_data = extract_combinations_data(nuxt_data, numeric_product_id)
                if combinations_data:
                    all_combinations_data.extend(combinations_data)
                    print(f"    ✅ {len(combinations_data)} combinaciones extraídas")
                
            except Exception as e:
                print(f"    ❌ Error: {e}")
                continue
            
            time.sleep(1)  # Pausa entre productos
        
        # PASO 3: Obtener complementos de todos los productos vía API
        print(f"\n🔧 PASO 3: Obteniendo complementos de {len(product_uuid_list)} productos vía API...")
        
        unique_complements = {}
        uuid_to_unique_key = {}
        product_to_complement_uuids = {}
        
        from get_complementos import get_complement_types, get_complements_by_type, generate_unique_key
        
        for i, (numeric_id, product_uuid) in enumerate(product_uuid_list, 1):
            print(f"  [{i}/{len(product_uuid_list)}] Producto ID {numeric_id} (UUID: {product_uuid[:8]}...)")
            
            try:
                complement_types_data = get_complement_types(product_uuid)
                
                if not complement_types_data:
                    continue
                
                product_complement_ids = []
                
                for comp_type in complement_types_data:
                    comp_type_id = comp_type.get('id', '')
                    comp_type_name = comp_type.get('web_name', 'Unknown')
                    
                    complements_list = get_complements_by_type(product_uuid, comp_type_id)
                    
                    if complements_list:
                        print(f"      - {comp_type_name}: {len(complements_list)} items")
                    
                    for complement in complements_list:
                        unique_key, key_type = generate_unique_key(complement)
                        comp_uuid = complement.get('id', '') or complement.get('uuid', '')
                        
                        if unique_key not in unique_complements:
                            unique_complements[unique_key] = complement
                            uuid_to_unique_key[comp_uuid] = unique_key
                        else:
                            uuid_to_unique_key[comp_uuid] = unique_key
                        
                        product_complement_ids.append(comp_uuid)
                
                if product_complement_ids:
                    product_to_complement_uuids[product_uuid] = product_complement_ids
                    print(f"      ✅ {len(product_complement_ids)} complementos recopilados")
            
            except Exception as e:
                print(f"      ❌ Error: {e}")
            
            time.sleep(0.5)
        
        print(f"\n✅ Complementos únicos obtenidos: {len(unique_complements)}")
        
        # PASO 4: Generar CSV de complementos
        print(f"\n📄 PASO 4: Generando CSV de complementos...")
        
        complement_csv_name = None
        key_to_prestashop_id = {}
        
        if unique_complements:
            from get_complementos import generate_complements_csv
            complement_csv_name, key_to_prestashop_id = generate_complements_csv(
                unique_complements,
                timestamp
            )
            print(f"✅ {complement_csv_name} generado con {len(unique_complements)} complementos (IDs: 136-{135+len(unique_complements)})")
        else:
            print(f"⚠️  No se encontraron complementos para generar CSV")
        
        # PASO 5: Actualizar productos con Accessories
        print(f"\n🔗 PASO 5: Actualizando productos con Accessories...")
        
        for product_data in all_products_data:
            numeric_id = product_data['Product ID']
            
            # Buscar el UUID de este producto
            product_uuid = None
            for pid, puuid in product_uuid_list:
                if pid == numeric_id:
                    product_uuid = puuid
                    break
            
            if not product_uuid:
                continue
            
            # Obtener complementos de este producto
            comp_uuids = product_to_complement_uuids.get(product_uuid, [])
            if not comp_uuids:
                continue
            
            # Mapear UUIDs a IDs de PrestaShop
            prestashop_ids = []
            for comp_uuid in comp_uuids:
                unique_key = uuid_to_unique_key.get(comp_uuid)
                if unique_key:
                    ps_id = key_to_prestashop_id.get(unique_key)
                    if ps_id and str(ps_id) not in prestashop_ids:
                        prestashop_ids.append(str(ps_id))
            
            # Actualizar el campo Accessories
            if prestashop_ids:
                product_data['Acessories  (x,y,z...)'] = ",".join(prestashop_ids)
                print(f"  • Producto ID {numeric_id} → {len(prestashop_ids)} accesorios")
        
        # PASO 6: Generar CSVs de productos y combinaciones
        print(f"\n📄 PASO 6: Generando CSVs de productos y combinaciones...")
        
        if all_products_data:
            with open(PRODUCT_OUTPUT_FILENAME, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=PRODUCT_CSV_HEADERS, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
                writer.writeheader()
                writer.writerows(all_products_data)
            print(f"✅ {PRODUCT_OUTPUT_FILENAME} generado ({len(all_products_data)} productos)")
        
        if all_combinations_data:
            with open(COMBINATION_OUTPUT_FILENAME, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=COMBINATION_CSV_HEADERS, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
                writer.writeheader()
                writer.writerows(all_combinations_data)
            print(f"✅ {COMBINATION_OUTPUT_FILENAME} generado ({len(all_combinations_data)} combinaciones)")
        
        # PASO 7: Subir a FTP en el orden correcto
        print(f"\n📤 PASO 7: Subiendo archivos al FTP...")
        config = leer_configuracion_ftp("ftp_config.txt")
        
        if config:
            # 1. Primero complementos
            if complement_csv_name and os.path.exists(complement_csv_name):
                print(f"  📤 Subiendo {complement_csv_name}...")
                subir_archivo_ftp(complement_csv_name, config.get("servidor"), 
                                config.get("usuario"), config.get("contraseña"), 
                                config.get("ruta_remota", "/"))
            
            # 2. Luego productos (con referencias a complementos)
            if all_products_data:
                print(f"  📤 Subiendo {PRODUCT_OUTPUT_FILENAME}...")
                subir_archivo_ftp(PRODUCT_OUTPUT_FILENAME, config.get("servidor"), 
                                config.get("usuario"), config.get("contraseña"), 
                                config.get("ruta_remota", "/"))
            
            # 3. Finalmente combinaciones
            if all_combinations_data:
                print(f"  📤 Subiendo {COMBINATION_OUTPUT_FILENAME}...")
                subir_archivo_ftp(COMBINATION_OUTPUT_FILENAME, config.get("servidor"), 
                                config.get("usuario"), config.get("contraseña"), 
                                config.get("ruta_remota", "/"))
            
            print(f"\n🎉 PROCESO COMPLETADO!")
            print(f"   • {len(unique_complements)} complementos")
            print(f"   • {len(all_products_data)} productos")
            print(f"   • {len(all_combinations_data)} combinaciones")
            print(f"   Todos los archivos subidos al FTP correctamente!")
        else:
            print(f"\n⚠️ Archivos generados pero sin configuración FTP.")
            print(f"📄 Archivos disponibles localmente:")
            if complement_csv_name:
                print(f"   • {complement_csv_name}")
            print(f"   • {PRODUCT_OUTPUT_FILENAME}")
            print(f"   • {COMBINATION_OUTPUT_FILENAME}")
    
    except Exception as e:
        print(f"❌ Error en el proceso: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()
            print("\n👋 Scraper finalizado.")

if __name__ == "__main__":
    main()