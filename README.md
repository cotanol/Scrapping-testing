# Web Scraping Project + FTP Integration

Este proyecto permite hacer scraping de productos de la página web todomueblesdebano.com y subirlos automáticamente a un servidor FTP.

## 📁 Estructura del Proyecto

- `scraper_ftp_simple.py` - **🆕 Archivo integrado simple** (scraping + FTP automático)
- `main_scrapper.py` - Módulo de web scraping original
- `ftp_config.txt` - Configuración del servidor FTP
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

Asegúrate de que el `chromedriver.exe` sea compatible con tu versión de Chrome.

### 4. Configurar FTP

Crea el archivo `ftp_config.txt` con la configuración de tu servidor:

```txt
servidor=ftp.tuservidor.com
usuario=tu_usuario
contraseña=tu_contraseña
ruta_remota=/uploads
```

## 🚀 Uso Simple

### Un Solo Comando

Ejecuta scraping + subida FTP automáticamente:

```bash
python scraper_ftp_simple.py
```

¡Eso es todo! El programa:

1. 🕷️ Ejecuta el web scraping
2. 📄 Genera el archivo CSV
3. 📤 Lo sube automáticamente al FTP

### Uso Individual

Si prefieres ejecutar solo el scraping:

```bash
python main_scrapper.py
```

## ⚙️ Configuración

### Cambiar URL a scrapear

En `main_scrapper.py`, modifica:

```python
BRAND_URL_TO_SCRAPE = "URL_DE_LA_MARCA"
```

## 🧪 URLs de Prueba

Para realizar pruebas, se recomiendan estas marcas con pocas colecciones:

- **Sergio Luppi**: https://www.todomueblesdebano.com/marcas/sergio-luppi/
- **Sagobar**: https://www.todomueblesdebano.com/marcas/sagobar/
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
- El archivo `ftp_config.txt` debe existir antes de ejecutar (no se incluye por seguridad)

## 🏃‍♂️ Ejecución

```bash
python main_scrapper.py
```

## 🧪 URLs de Prueba

Para realizar pruebas, se recomiendan estas marcas con pocas colecciones:

- **Sergio Luppi**: https://www.todomueblesdebano.com/marcas/sergio-luppi/
- **Sagobar**: https://www.todomueblesdebano.com/marcas/sagobar/
  _(Nota: Algunos productos tienen elementos duplicados como doble botón de ficha técnica, aunque parece que is funciona correctamente y no se duplica en su columna)_
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
