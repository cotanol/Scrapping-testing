# Checklist: Verificar atributo "Espejo" en PrestaShop

## ✅ PASO 1: Verificar valores del atributo "Espejo"

1. Ve a: **Catálogo → Atributos y Características**
2. Busca **"Espejo" (ID 7)**
3. Haz clic en **"Ver valores"** (o el icono de lista al lado)
4. Verifica lo siguiente:

### Cosas a comprobar:

- [ ] ¿Cuántos valores tiene el atributo "Espejo"? (Debería tener al menos 3-4)
- [ ] ¿Los nombres están completos o cortados?
- [ ] ¿Hay caracteres extraños (/, ñ, acentos) que puedan estar mal codificados?
- [ ] ¿Todos los valores están marcados como "Públicos"?

### Valores esperados según el CSV:

1. **Espejo oferta del pack**
2. **Sin espejo / ver otras opciones en complementos** ← ⚠️ SOSPECHOSO (tiene `/`)
3. **Espejo oferta pack premium Lys LED (Royo)** ← ⚠️ SOSPECHOSO (tiene `()`)
4. **Espejo oferta del pack sin led**
5. **Espejo de 120 cm oferta pack con 2 apliques de luz LED de 30cm**

---

## ✅ PASO 2: Verificar configuración del atributo "Espejo"

1. En **Atributos → Espejo**, haz clic en **"Editar"** (icono del lápiz)
2. Verifica:

### Configuración que DEBE tener:

- [ ] **Grupo público:** ☑️ SÍ (checkbox marcado)
- [ ] **Tipo de atributo:** "Lista desplegable" o "Botón de radio"
- [ ] **Posición:** 2 (después de Medida=0 y Acabado=1)

---

## ✅ PASO 3: Comparar con "Medida" y "Acabado"

1. Ve a **Catálogo → Atributos**
2. Compara la configuración de:
   - **Medida** (el que SÍ funciona)
   - **Acabado** (el que SÍ funciona)
   - **Espejo** (el que NO funciona)

### ¿Qué diferencias ves?

- [ ] Tipo de atributo diferente
- [ ] "Grupo público" no marcado en Espejo
- [ ] Cantidad de valores (¿Espejo tiene muchos más valores que los otros?)

---

## ✅ PASO 4: Verificar en el frontend (DevTools)

1. Abre el producto 132 en el **frontend**
2. Presiona **F12** para abrir DevTools
3. Ve a la pestaña **"Elements"** o **"Inspector"**
4. Busca el HTML de los selectores de atributos

### ¿Qué ves?

- [ ] Hay un `<select>` o `<div>` para "Medida" ✅
- [ ] Hay un `<select>` o `<div>` para "Acabado" ✅
- [ ] ¿Hay un `<select>` o `<div>` para "Espejo"? ❌
- [ ] Si NO existe el elemento HTML, el problema es del backend
- [ ] Si SÍ existe pero está oculto (`display: none`), el problema es CSS/JS

---

## ✅ PASO 5: Verificar errores en JavaScript

1. En el mismo producto, ve a la pestaña **"Console"** de DevTools
2. Busca errores rojos

### Posibles errores relacionados:

```
Uncaught TypeError: Cannot read property 'Espejo' of undefined
SyntaxError: Unexpected token '/' in JSON
```

Si ves errores, cópialos y pégalos aquí.

---

## ✅ PASO 6: Prueba simplificar nombres largos

Si los nombres tienen caracteres especiales, prueba renombrarlos:

### En PrestaShop (sin reimportar):

1. Ve a **Catálogo → Atributos → Espejo → Ver valores**
2. Edita el valor: **"Sin espejo / ver otras opciones en complementos"**
3. Cambia a: **"Sin espejo"** (más corto, sin `/`)
4. Edita el valor: **"Espejo oferta pack premium Lys LED (Royo)"**
5. Cambia a: **"Espejo pack premium Lys LED"** (sin `()`)
6. Guarda y limpia caché
7. Prueba en el frontend

---

## 🎯 RESUMEN DE DIAGNÓSTICO

Si el problema es solo con "Espejo":

### Causa más probable:

1. **Nombres de valores con caracteres especiales** (`/`, `()`)
2. **Nombres demasiado largos** (más de 50 caracteres)
3. **Codificación UTF-8 incorrecta** en la importación
4. **Configuración "Grupo público" no marcada**

### Solución rápida:

1. Simplifica los nombres de los valores en PrestaShop manualmente
2. Limpia caché
3. Si funciona, regeneramos el CSV con nombres más cortos

---

## 📊 Información a reportar:

Por favor, dime:

1. ¿Cuántos valores tiene el atributo "Espejo" en PrestaShop?
2. ¿Los nombres están completos o cortados?
3. ¿Hay errores en la consola del navegador (F12)?
4. ¿El elemento HTML `<select>` existe pero está oculto, o NO existe?
5. ¿Qué tema de PrestaShop usas? (Classic, otro)
