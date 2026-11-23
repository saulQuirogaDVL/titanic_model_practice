# 04_api_fastapi.md

Crea una API REST con FastAPI para predecir si un pasajero del Titanic sobreviviría.

Antes de implementar, revisa `AGENTS.md`, `scripts/entrenar.py` y `app/app.py` para respetar las columnas, categorías y el formato del modelo serializado.

## Contexto

El modelo está entrenado y serializado con Joblib en `modelos/modelo_titanic.joblib` como un diccionario `{"modelo", "columnas", "nombre_modelo", "version"}`.

## Requisitos

1. Crear `api/api.py` utilizando FastAPI y Pydantic.
2. Construir las rutas con `pathlib` a partir de la ubicación del archivo.
3. Cargar el modelo **una sola vez** al iniciar la aplicación mediante `lifespan`, guardándolo en `app.state`. Si el archivo no existe, la API debe iniciar igualmente y reportar el modelo como no disponible.
4. Endpoints:
   - `GET /`: información básica de la API y lista de endpoints.
   - `GET /health`: estado del servicio; indica si el modelo está cargado, su nombre y versión. Responder `503` si el modelo no está disponible.
   - `POST /predict`: recibe los datos de un pasajero en JSON y devuelve la predicción.
5. Definir un modelo Pydantic `DatosPasajero` con las variables originales del dataset y validaciones:

| Campo | Tipo | Validación |
|---|---|---|
| `Pclass` | `int` | `Literal[1, 2, 3]` |
| `Sex` | `str` | `Literal["male", "female"]` |
| `Age` | `float` | 0 – 100 |
| `SibSp` | `int` | 0 – 10 |
| `Parch` | `int` | 0 – 10 |
| `Fare` | `float` | ≥ 0 |
| `Embarked` | `str` | `Literal["S", "C", "Q"]` |

   Incluir descripciones en español en cada campo y un ejemplo en el esquema (`json_schema_extra`).
6. Definir un modelo Pydantic `RespuestaPrediccion` con:
   - `prediccion`: `"Sobrevive"` o `"No sobrevive"`.
   - `sobrevive`: `true` / `false`.
   - `probabilidad_supervivencia`: valor entre 0 y 1 (4 decimales).
   - `modelo` y `version`.
7. Convertir los datos recibidos en un DataFrame de una fila ordenado según `columnas` y utilizar `predict()` y `predict_proba()`.
8. Manejo de errores: `422` automático para datos inválidos, `503` si el modelo no está cargado, `500` con mensaje claro ante errores de inferencia.

## Condiciones

- No reentrenar el modelo.
- No modificar el notebook, el script de entrenamiento ni la app Streamlit.
- No crear archivos adicionales innecesarios.
- Mantener el código corto, sencillo, educativo y en español.
- Ejecutar con: `uvicorn api.api:app --reload` desde la raíz del proyecto (documentación interactiva en `/docs`).

## Validación

- Probar `GET /`, `GET /health` y `POST /predict` con los pasajeros de ejemplo (hombre, 3.ª clase → No sobrevive; mujer, 1.ª clase → Sobrevive) y verificar que coincidan con Streamlit.
- Probar un caso inválido (por ejemplo, `Sex = "otro"`) y verificar la respuesta `422`.
