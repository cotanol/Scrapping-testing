# Web Scraping Project - Todo Muebles de Baño

Este proyecto permite hacer scraping de productos de la página web todomueblesdebano.com para extraer información detallada de los productos organizados por marcas.

## 📁 Estructura del Proyecto

- `main_scrapper.py` - Archivo principal del scraper
- `requirements.txt` - Dependencias de Python
- `chromedriver.exe` - Driver de Chrome para Selenium
- `.gitignore` - Archivos y carpetas ignoradas por Git

## 🚀 Instalación

### 1. Configurar entorno virtual

```bash
python -m venv .venv
.venv\Scripts\activate
py -m pip install --upgrade pip
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Verificar ChromeDriver

Asegúrate de que el `chromedriver.exe` sea compatible con tu versión de Chrome. El incluido es la versión más actual.

## ⚙️ Configuración

En el archivo `main_scrapper.py`, modifica la variable global:

```python
BRAND_URL_TO_SCRAPE = "URL_DE_LA_MARCA"
```

## 🏃‍♂️ Ejecución

```bash
python main_scrapper.py
```

## 🧪 URLs de Prueba

Para realizar pruebas, se recomiendan estas marcas con pocas colecciones:

- **Sergio Luppi**: https://www.todomueblesdebano.com/marcas/sergio-luppi/
- **Sagobar**: https://www.todomueblesdebano.com/marcas/sagobar/
  _(Nota: Algunos productos tienen elementos duplicados como doble botón de ficha técnica)_
- **Oasis Star**: https://www.todomueblesdebano.com/marcas/oasis-star/

## 🎯 Objetivo Principal

**Marca Royo**: https://www.todomueblesdebano.com/marcas/royo/

- 48 productos en total
- Tiempo de ejecución considerable
- Se recomienda probar primero con marcas más pequeñas

## ⚠️ Notas Importantes

- El proceso puede tomar tiempo considerable dependiendo del número de productos
- Se recomienda hacer pruebas con marcas pequeñas antes de procesar colecciones grandes
- Asegúrate de tener una conexión estable a internet durante la ejecución
