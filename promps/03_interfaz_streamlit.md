# 03_interfaz_streamlit.md

Crea la interfaz `app/app.py` con Streamlit para predecir si un pasajero del Titanic sobreviviría.

Antes de implementar, revisa `AGENTS.md`, `scripts/entrenar.py` y `modelos/metricas.json` para respetar las columnas, categorías y el formato del modelo serializado.

## Requisitos

### Carga del modelo
1. Cargar `modelos/modelo_titanic.joblib` con Joblib utilizando `@st.cache_resource`.
2. Construir la ruta con `pathlib` a partir de la ubicación del archivo, para que funcione desde cualquier directorio.
3. Si el modelo no existe, mostrar un error indicando ejecutar `python scripts/entrenar.py` y detener la aplicación.
4. Leer las columnas esperadas desde la clave `columnas` del paquete serializado.

### Formulario (`st.form`)
Campos con etiquetas en español y valores por defecto razonables:

| Variable | Control | Valores |
|---|---|---|
| `Pclass` | `selectbox` | 1 (Primera), 2 (Segunda), 3 (Tercera) |
| `Sex` | `selectbox` | male (Hombre), female (Mujer) |
| `Age` | `number_input` | 0 – 100 |
| `SibSp` | `number_input` | Hermanos/cónyuges a bordo, 0 – 10 |
| `Parch` | `number_input` | Padres/hijos a bordo, 0 – 10 |
| `Fare` | `number_input` | Tarifa ≥ 0 |
| `Embarked` | `selectbox` | S (Southampton), C (Cherbourg), Q (Queenstown) |

- Mostrar etiquetas en español, pero enviar al modelo los valores originales del dataset (`male`, `S`, `1`, etc.).
- Botón: **"Predecir supervivencia"**.

### Resultado
1. Construir un DataFrame de una fila ordenado según `columnas`.
2. Utilizar `predict()` y `predict_proba()`.
3. Mostrar **"Sobrevive"** (`st.success`) o **"No sobrevive"** (`st.error`) junto con la probabilidad de supervivencia (`st.metric` y `st.progress`).
4. Mostrar un mensaje comprensible para el usuario.

### Información del modelo
- En la barra lateral, mostrar el nombre del modelo, su versión y las métricas en prueba leídas de `modelos/metricas.json` (si existe).

## Condiciones

- Interfaz sencilla, profesional y en español.
- No reentrenar el modelo desde Streamlit.
- No utilizar bases de datos.
- No crear archivos adicionales fuera de `app/app.py`.
- Ejecutar con: `streamlit run app/app.py` desde la raíz del proyecto.

## Validación

- Verificar que la aplicación inicia sin errores.
- Verificar la lógica de predicción con un pasajero de ejemplo (hombre, 3.ª clase → No sobrevive; mujer, 1.ª clase → Sobrevive).
