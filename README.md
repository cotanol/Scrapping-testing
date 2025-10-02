# 🚀 Royo Products Scraper + PrestaShop + FTP

**Proyecto optimizado para extraer productos Royo con formato PrestaShop y subida automática a FTP**

Este proyecto automatiza completamente la extracción de 48 productos de la marca Royo desde todomueblesdebano.com, los convierte al formato PrestaShop (66 columnas productos + 22 columnas combinaciones) y los sube automáticamente al servidor FTP.

## 📁 Estructura del Proyecto (Optimizada)

### ✅ **Archivos Esenciales:**

- `royo_prestashop_ftp.py` - **Script principal integrado** (scraping + PrestaShop + FTP)
- `get_urls_by_brand.py` - Extractor de URLs de productos por marca
- `ftp_config.txt` - Configuración del servidor FTP
- `requirements.txt` - Dependencias de Python
- `chromedriver.exe` - Driver de Chrome para Selenium

### 📋 **Archivos Generados:**

- `products_import.csv` - Productos en formato PrestaShop (66 columnas)
- `combinations_import.csv` - Combinaciones de productos (22 columnas)

## 🚀 Instalación Rápida

1. **Entorno virtual** (recomendado):

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   py -m pip install --upgrade pip
   ```

2. **Instalar dependencias**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Verificar Chrome Driver**: Asegúrate que `chromedriver.exe` sea compatible con tu Chrome.

4. **Configurar FTP** - El archivo `ftp_config.txt` ya está configurado:
   ```txt
   servidor=ftp.threeveloxcode.com
   usuario=tester23@threeveloxcode.com
   contraseña=Mb4lj1i]k.@q
   ruta_remota=/
   ```

## ⚡ Uso Ultra Simple

**¡Una sola línea para todo el proceso!**

```bash
python royo_prestashop_ftp.py
```

### 🎯 **Flujo Automático Completo:**

1. 🔍 **Extrae 48 URLs** de productos Royo
2. 🕷️ **Procesa cada producto** con formato PrestaShop avanzado
3. � **Genera 2 CSVs**:
   - `products_import.csv` (66 columnas PrestaShop)
   - `combinations_import.csv` (22 columnas combinaciones)
4. 📤 **Sube automáticamente** ambos archivos al FTP
5. ✅ **Proceso completo en ~5-6 minutos**

## 📋 Formato PrestaShop Generado

### 🛍️ **Productos (66 columnas)**:

- ID, nombres, precios, categorías, descripciones SEO
- Imágenes, características técnicas, datos de envío
- Metadatos completos para PrestaShop

### 🔧 **Combinaciones (22 columnas)**:

- Variantes de productos (colores, tamaños, acabados)
- Precios diferenciados, referencias, stock
- Atributos y valores organizados

## ⚙️ Configuración Avanzada

### 🎯 **Cambiar marca objetivo**:

Edita en `royo_prestashop_ftp.py`:

```python
BRAND_URL_TO_SCRAPE = "https://www.todomueblesdebano.com/marcas/OTRA-MARCA/"
```

### 🔧 **Ajustar configuración FTP**:

Modifica `ftp_config.txt` según tu servidor.

## 🧪 URLs de Otras Marcas (Para Pruebas)

- **Sergio Luppi**: https://www.todomueblesdebano.com/marcas/sergio-luppi/ (menos productos)
- **Sagobar**: https://www.todomueblesdebano.com/marcas/sagobar/ (colección pequeña)
- **Oasis Star**: https://www.todomueblesdebano.com/marcas/oasis-star/ (ideal para pruebas)

## 📊 Estadísticas del Proyecto

- ✅ **48 productos Royo** procesados automáticamente
- ✅ **~5-6 minutos** tiempo total de ejecución
- ✅ **2 archivos CSV** generados en formato PrestaShop
- ✅ **Subida FTP automática** sin intervención manual
- ✅ **Formato optimizado** para importación directa en PrestaShop

## ⚠️ Notas Importantes

- 🌐 **Conexión estable** requerida durante la ejecución
- ⏱️ **Proceso automatizado** - no requiere supervisión
- 🔄 **Reintentos automáticos** en caso de errores de red
- 📁 **Archivos se sobrescriben** en cada ejecución
- 🛡️ **Configuración FTP** ya incluida y funcional

---

## 🎯 **¡Todo en 1 comando! ¡Lista para PrestaShop!**
