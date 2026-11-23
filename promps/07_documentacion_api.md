# 07_documentacion_api.md

Mejora la documentación OpenAPI (Swagger en `/docs` y ReDoc en `/redoc`) de `api/api.py` utilizando **únicamente los campos y funcionalidades nativas de OpenAPI/Swagger que ofrece FastAPI**, sin alterar el comportamiento de la API.

Antes de implementar, revisa `AGENTS.md` y el `api/api.py` actual.

## Alcance

- Solo documentación: no modificar la lógica, las validaciones, los formatos de respuesta ni el manejo de errores.
- Sin manejadores de excepciones personalizados: los errores mantienen el formato estándar de FastAPI (`422` con `detail` de Pydantic; `404`, `500` y `503` con `{"detail": "..."}`).
- La interfaz nativa de Swagger UI y los elementos generados automáticamente por FastAPI (por ejemplo, la respuesta `422 Validation Error`) permanecen en inglés: Swagger UI no ofrece selector de idioma.
- En español: títulos, descripciones, resúmenes y ejemplos definidos en el código.

## Funcionalidades nativas a utilizar

### Aplicación (`FastAPI(...)`)
- `title`, `version` y una `description` breve (una línea con el propósito y el modelo). La información detallada se documenta en los campos, endpoints y respuestas, no en la portada.
- `openapi_tags` con descripción por grupo: **General** (`/`, `/health`) y **Predicción** (`/predict`).
- `swagger_ui_parameters`: endpoints expandidos en lista, duración de las peticiones visible y "Try it out" habilitado por defecto.

### Campos de entrada (`DatosPasajero` con `Field`)
`title`, `description` (qué representa, valores aceptados y su significado), `examples` y restricciones (`ge`, `le`, `Literal`) que Swagger muestra como rangos y valores permitidos:

| Campo | Representa | Valores aceptados |
|---|---|---|
| `Pclass` | Clase del boleto (nivel socioeconómico y ubicación del camarote) | `1` Primera, `2` Segunda, `3` Tercera |
| `Sex` | Sexo del pasajero | `"male"` Hombre, `"female"` Mujer |
| `Age` | Edad en años (admite decimales para bebés) | 0 – 100 |
| `SibSp` | Hermanos o cónyuges a bordo | Entero 0 – 10 |
| `Parch` | Padres o hijos a bordo | Entero 0 – 10 |
| `Fare` | Tarifa pagada en libras esterlinas (1912) | ≥ 0 (en el dataset: 0 – 512.33) |
| `Embarked` | Puerto de embarque | `"S"` Southampton, `"C"` Cherbourg, `"Q"` Queenstown |

### Endpoints
- `tags`, `summary`, `description` y `response_description` en español.
- `response_model` con modelos Pydantic documentados para `/`, `/health` y `/predict`.
- `openapi_examples` en `POST /predict` (lista desplegable en Swagger): mujer de 1.ª clase, hombre de 3.ª clase, niño de 2.ª clase y un caso inválido.
- `responses` para documentar `503` y `500` con su esquema y ejemplo. El `422` lo documenta FastAPI de forma automática.

## Restricciones

- No modificar la lógica de predicción ni el modelo.
- No agregar librerías.

## Validación

- Verificar que las respuestas de la API sean idénticas a las de la versión anterior (predicciones, formato de errores, campos extra ignorados).
- Verificar el esquema `/openapi.json` (etiquetas, ejemplos, respuestas y esquemas).
- Revisar visualmente `/docs`.
- Actualizar el `README.md`.
