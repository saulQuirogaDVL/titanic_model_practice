# 06_modo_ilustrado.md

Agrega a la interfaz Streamlit un **modo ilustrado**, más familiar y divertido, en el que un personaje de estilo cartoon (SVG) cambie su apariencia según los datos del pasajero y la escena refleje la predicción del modelo.

Antes de implementar, revisa `AGENTS.md`, `app/app.py` y `promps/05_mejora_interfaz.md`.

## Restricciones

- No agregar librerías: el SVG se genera con texto en Python y se muestra con componentes nativos de Streamlit.
- No utilizar imágenes externas ni JavaScript. Las animaciones, si existen, deben ser CSS dentro del propio SVG.
- No modificar la lógica de predicción: reutilizar las funciones existentes (`predecir`, `contribuciones`, etc.).
- Crear la ilustración en un módulo separado `app/ilustracion.py` con funciones pequeñas y documentadas.
- No modificar `notebooks/`, `scripts/`, `api/`, `modelos/` ni `data/`.

## Selector de estilo

- Debajo del título, un `st.segmented_control` con las opciones **"🎨 Ilustrado"** (por defecto) y **"📋 Clásico"**.
- **Clásico:** mantiene la interfaz actual (formulario con botón).
- **Ilustrado:** sin botón; la escena y la predicción se actualizan en vivo al cambiar cualquier dato.
- Las pestañas "¿Quién sobrevive?" y "Sobre el modelo" se mantienen igual en ambos modos.

## Personaje (cambia según los parámetros)

| Parámetro | Cambio visual |
|---|---|
| `Sex` | Mujer: cabello largo y vestido. Hombre: cabello corto, saco y pantalón. |
| `Age` | Niño (≤ 12): personaje más pequeño. Adulto. Mayor (≥ 60): canas, lentes y bastón. |
| `Pclass` | 1.ª: sombrero de copa / sombrero con pluma, ropa elegante (moño o collar). 2.ª: bombín / capota, ropa formal sencilla. 3.ª: gorra / pañuelo, tirantes o delantal y parches. |
| `SibSp` | Figuras acompañantes de tamaño adulto. |
| `Parch` | Figuras acompañantes pequeñas. Máximo 4 acompañantes visibles; el resto como "+N". |
| `Fare` | Boleto con la clase y la tarifa pagada. |
| `Embarked` | Banderín con el nombre del puerto de embarque. |

## Escena (según la predicción)

- **Sobrevive:** día soleado, mar en calma, personaje sonriente saludando dentro de un bote salvavidas que se balancea.
- **No sobrevive:** noche, barco inclinado e iceberg de fondo, personaje preocupado en el agua con un salvavidas. El **nivel del agua** depende de la probabilidad (a menor probabilidad, más alto).
- Insignia con la probabilidad de supervivencia.
- La escena debe escalar al ancho de la pantalla (responsive) y mantener la proporción.

## Resultado en modo ilustrado

1. Pasajeros de ejemplo (mismos botones del modo clásico).
2. Escena ilustrada.
3. Mensaje amigable con el resultado y la probabilidad (por ejemplo: "¡La pasajera consigue un lugar en un bote salvavidas!").
4. Resumen en lenguaje natural de las variables que más ayudaron y más perjudicaron, a partir de las contribuciones del modelo.
5. Controles del pasajero en dos columnas (se apilan en móvil).
6. Expansor "Ver análisis detallado" con la comparación con pasajeros reales, el gráfico "¿Por qué este resultado?" y la simulación por edad.

## Validación

- `AppTest`: ambos modos cargan sin excepciones; los pasajeros de ejemplo producen los resultados esperados; cambiar entre modos no genera errores.
- Validar que el SVG generado sea XML válido para combinaciones de sexo, edad, clase, familia y resultado.
- Capturas de pantalla (navegador headless) en escritorio y móvil para revisar el aspecto visual.
- Actualizar el `README.md`.
