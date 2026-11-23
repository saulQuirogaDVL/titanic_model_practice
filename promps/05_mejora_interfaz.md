# 05_mejora_interfaz.md

Mejora la interfaz `app/app.py` para que tenga una apariencia **profesional**, sea **responsive** (usable en móviles) y permita **analizar quién podría sobrevivir**, de modo que pueda compartirse con otras personas.

Antes de implementar, revisa `AGENTS.md`, el `app/app.py` actual, `scripts/entrenar.py` y `modelos/metricas.json`.

## Restricciones principales

- Utilizar **únicamente Streamlit, Pandas y Joblib** (componentes nativos: `st.tabs`, `st.columns`, `st.container(border=True)`, `st.metric`, `st.bar_chart`, `st.line_chart`, `st.dataframe`, etc.).
- No agregar librerías nuevas ni CSS/HTML personalizado (`unsafe_allow_html`).
- No reentrenar el modelo: solo cargar `modelos/modelo_titanic.joblib`.
- Mantener la lógica de predicción actual (mismas columnas y valores originales del dataset).
- Mantener el código sencillo, modular (funciones pequeñas) y en español.

## Estructura de la aplicación

### Encabezado
- Título con icono, subtítulo breve explicando qué hace la aplicación y una línea con el modelo y su versión.

### Pestaña 1 — "Predicción"
1. **Pasajeros de ejemplo**: botones que cargan perfiles predefinidos en el formulario mediante `st.session_state`:
   - "Mujer · 1.ª clase" (Pclass 1, female, 30 años, 0, 0, 80, C).
   - "Hombre · 3.ª clase" (Pclass 3, male, 25 años, 0, 0, 7.25, S).
   - "Niño · 2.ª clase" (Pclass 2, male, 6 años, 1, 1, 30, S).
2. **Formulario** (`st.form`) agrupado en dos secciones con subtítulos: *Datos personales* (sexo, edad) y *Datos del viaje* (clase, tarifa, puerto, hermanos/cónyuges, padres/hijos). Etiquetas en español, `help` en cada campo y valores originales enviados al modelo.
3. **Tarjeta de resultado** (`st.container(border=True)`):
   - Mensaje destacado: "Sobrevive" (`st.success`) o "No sobrevive" (`st.error`).
   - `st.metric` con la probabilidad de supervivencia y `st.progress`.
   - Nivel de confianza en texto: *Alta* (≥ 70 % o ≤ 30 %), *Media* (30–40 % o 60–70 %) o *Incierta* (40–60 %).
4. **"¿Por qué este resultado?"**: gráfico de barras horizontal (`st.bar_chart`) con la contribución de cada variable para ese pasajero, calculada como `coeficiente × valor transformado` del Pipeline (Regresión Logística). Agrupar las columnas One-Hot por variable original (Sexo, Clase, Edad, Hermanos/cónyuges, Padres/hijos, Tarifa, Puerto). Positivo = aumenta la probabilidad; negativo = la disminuye. Si el modelo no tiene `coef_` (Random Forest), mostrar la importancia de variables.
5. **Comparación con la realidad**: tasa de supervivencia real en `data/titanic.csv` de los pasajeros con el mismo sexo y clase (por ejemplo: "De los 94 pasajeros reales con este perfil, sobrevivió el 96.8 %").
6. **Simulación por edad**: `st.line_chart` con la probabilidad estimada del mismo pasajero variando la edad de 0 a 80 años.

### Pestaña 2 — "¿Quién sobrevive?"
Análisis exploratorio basado en `data/titanic.csv` (cargado con `@st.cache_data`):
- KPIs: total de pasajeros, sobrevivientes y tasa global de supervivencia.
- Tasa de supervivencia por sexo, por clase y por sexo y clase combinados (`st.bar_chart`).
- Tasa de supervivencia por rango de edad (0–12, 13–18, 19–30, 31–50, 51+).
- Tasa de supervivencia por puerto de embarque.
- Explicación breve (3–5 viñetas) de cómo influye cada variable: regla "mujeres y niños primero", ubicación de los camarotes según la clase, familias numerosas, y que la tarifa y el puerto reflejan principalmente la clase.

### Pestaña 3 — "Sobre el modelo"
- Algoritmo, versión y fecha de entrenamiento.
- Métricas en prueba (`st.metric`) con una explicación de una línea por métrica.
- Tabla de comparación de modelos (validación cruzada) leída de `modelos/metricas.json` y justificación de la elección.
- Nota de responsabilidad: el modelo es educativo y se basa en datos históricos.

## Diseño profesional y responsive

- `st.set_page_config(layout="centered")` para una lectura cómoda en escritorio y móvil.
- Utilizar como máximo **2 columnas** por fila (Streamlit las apila automáticamente en pantallas pequeñas).
- Botones del formulario y de ejemplos con `width="stretch"`.
- Evitar tablas anchas: mostrar solo las columnas necesarias y usar `hide_index=True`.
- Gráficos con ancho adaptable al contenedor (sin parámetros deprecados) y títulos cortos.
- Crear `.streamlit/config.toml` con un tema sobrio y consistente (color primario azul marino, fondo claro, fuente `sans serif`).
- Pie de página con `st.caption`: fuente de los datos y aviso de uso educativo.

## Validación

- Verificar con `streamlit.testing.v1.AppTest` que la aplicación carga sin excepciones y que los pasajeros de ejemplo producen los resultados esperados (mujer 1.ª clase → Sobrevive; hombre 3.ª clase → No sobrevive).
- Levantar la aplicación con `streamlit run app/app.py` y verificar que responde.
- Verificar que no aparezcan advertencias de funciones deprecadas en la versión instalada de Streamlit.
- Actualizar la sección de Streamlit del `README.md` describiendo las pestañas.

## No modificar

- `notebooks/`, `scripts/entrenar.py`, `api/api.py`, `modelos/` ni `data/titanic.csv`.
