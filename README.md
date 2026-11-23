# Predicción de supervivencia en el Titanic

Proyecto de Machine Learning que predice si un pasajero del Titanic **sobreviviría** o **no sobreviviría**, cubriendo el ciclo completo: experimento en notebook, script de entrenamiento ejecutable, modelo serializado, interfaz Streamlit y API REST con FastAPI.

Dataset: [Titanic (Kaggle)](https://www.kaggle.com/datasets/heptapod/titanic) — versión clásica de 891 pasajeros en `data/titanic.csv`.

---

## Estructura del proyecto

```
Practica_1/
├── AGENTS.md                         # Reglas y contexto del proyecto
├── README.md
├── requirements.txt
├── data/
│   └── titanic.csv                   # Dataset original (no se modifica)
├── notebooks/
│   └── experimento_titanic.ipynb     # Experimento: EDA, comparación y evaluación
├── scripts/
│   └── entrenar.py                   # Entrenamiento ejecutable
├── modelos/
│   ├── modelo_titanic.joblib         # Pipeline serializado
│   └── metricas.json                 # Métricas del entrenamiento
├── .streamlit/
│   └── config.toml                   # Tema visual de Streamlit
├── app/
│   ├── app.py                        # Interfaz Streamlit
│   └── ilustracion.py                # Escena cartoon en SVG (modo ilustrado)
├── api/
│   └── api.py                        # API REST FastAPI
└── promps/                           # Instrucciones usadas en cada etapa
    ├── 01_experimento_notebook.md
    ├── 02_script_entrenamiento.md
    ├── 03_interfaz_streamlit.md
    ├── 04_api_fastapi.md
    ├── 05_mejora_interfaz.md
    ├── 06_modo_ilustrado.md
    └── 07_documentacion_api.md
```

---

## Requisitos

- Python 3.10+ (entorno Conda `mlops`: `C:\Users\OMEN\anaconda3\envs\mlops\python.exe`)
- Dependencias:

```bash
conda activate mlops
pip install -r requirements.txt
```

> Todos los comandos se ejecutan desde la raíz del proyecto (`Practica_1/`).

---

## 1. Experimento (notebook)

`notebooks/experimento_titanic.ipynb` documenta paso a paso:

1. Exploración de datos y valores faltantes.
2. Análisis visual (supervivencia por sexo, clase y edad).
3. Selección de variables y preprocesamiento.
4. Comparación de modelos con validación cruzada.
5. Evaluación del modelo seleccionado, interpretación y serialización.

```bash
jupyter notebook notebooks/experimento_titanic.ipynb
```

### Variables

| Tipo | Variables |
|---|---|
| Objetivo | `Survived` (1 = sobrevive, 0 = no sobrevive) |
| Numéricas | `Age`, `SibSp`, `Parch`, `Fare` |
| Categóricas | `Pclass`, `Sex`, `Embarked` |
| Descartadas | `PassengerId`, `Name`, `Ticket`, `Cabin` (identificadores, texto libre o 77 % de faltantes) |

### Preprocesamiento (dentro del `Pipeline`)

- **Numéricas:** imputación por mediana (`Age` tiene 177 faltantes) + `StandardScaler`.
- **Categóricas:** imputación por moda (`Embarked` tiene 2 faltantes) + `OneHotEncoder`.

Al estar integrado en el Pipeline, el mismo preprocesamiento se aplica automáticamente en Streamlit y en la API.

---

## 2. Resultados

### Comparación de modelos (validación cruzada estratificada, 5 particiones)

| Modelo | Accuracy | F1 | ROC-AUC |
|---|---|---|---|
| **Regresión Logística** | 0.802 ± 0.014 | 0.730 ± 0.022 | 0.853 ± 0.022 |
| Random Forest | 0.815 ± 0.032 | 0.734 ± 0.045 | 0.869 ± 0.024 |

**Criterio de selección:** Random Forest se elige solo si mejora el F1 medio en al menos 0.02. La mejora fue de 0.004 (y todas las diferencias son menores que la variabilidad entre particiones), por lo que se seleccionó la **Regresión Logística**: rendimiento equivalente, más simple, más liviana e interpretable.

### Evaluación en prueba (179 pasajeros)

| Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---|---|---|---|
| 0.80 | 0.79 | 0.67 | 0.72 | 0.84 |

### Interpretación

- Ser **mujer** (+1.36) y viajar en **primera clase** (+1.04) son los factores que más aumentan la probabilidad de sobrevivir.
- Ser **hombre** (−1.24), viajar en **tercera clase** (−1.06) y una mayor **edad** (−0.49) la reducen.

---

## 3. Entrenamiento ejecutable

`scripts/entrenar.py` reproduce el experimento de forma automatizada: carga y valida los datos, compara ambos modelos, selecciona el mejor, lo evalúa, lo reentrena con todos los datos y lo serializa.

```bash
python scripts/entrenar.py
```

## 4. Modelo serializado

Se guarda con Joblib en `modelos/modelo_titanic.joblib` como un diccionario:

```python
{
    "modelo": Pipeline,                # preprocesamiento + clasificador
    "columnas": [...],                 # orden de columnas esperado
    "nombre_modelo": "Regresión Logística",
    "version": "20261122T005351Z",     # fecha UTC del entrenamiento
}
```

Las métricas se guardan en `modelos/metricas.json`.

---

## 5. Interfaz Streamlit

Interfaz profesional y adaptada a móviles (diseño centrado, máximo dos columnas que se apilan en pantallas pequeñas y tema propio en `.streamlit/config.toml`).

Dos botones al inicio de la pestaña **Predicción** permiten elegir la vista (el de la vista ilustrada se destaca para invitar a probarla):

- **📋 Clásico (por defecto):** formulario con botón y resultado en formato de tarjetas.
- **🎨 Ilustrado:** la escena se muestra junto a los controles (en móviles se apilan) y un personaje cartoon en SVG (`app/ilustracion.py`, sin librerías adicionales) cambia en vivo según los datos: sexo (cabello y ropa), edad (niño, adulto o mayor con canas, lentes y bastón), clase (sombrero de copa, bombín o gorra; ropa elegante o con parches), familiares a bordo (acompañantes), tarifa (boleto) y puerto (banderín). Si sobrevive aparece en un bote salvavidas de día; si no, en el agua de noche junto al barco hundiéndose, con un nivel de agua proporcional a la probabilidad. Incluye un resumen en lenguaje natural de lo que más ayudó y perjudicó.

Se organiza en tres pestañas:

| Pestaña | Contenido |
|---|---|
| 🔮 **Predicción** | Pasajeros de ejemplo con un clic, formulario (datos personales y del viaje), tarjeta de resultado con probabilidad y nivel de confianza, comparación con pasajeros reales del mismo perfil, gráfico **“¿Por qué este resultado?”** (aporte de cada variable) y simulación de la probabilidad según la edad. |
| 📊 **¿Quién sobrevive?** | Indicadores generales y tasas de supervivencia por sexo, clase, clase y sexo, rango de edad y puerto, con la explicación de cómo influye cada variable. |
| 🧠 **Sobre el modelo** | Algoritmo, fecha de entrenamiento, métricas en prueba explicadas y comparación de modelos. |

```bash
streamlit run app/app.py
```

Abrir: http://localhost:8501 · Desde un celular en la misma red: usar la **Network URL** que muestra Streamlit al iniciar.

> **Limitación conocida:** la Regresión Logística suma el efecto de cada variable por separado, por lo que no capta bien combinaciones específicas. Por ejemplo, el 100 % de los niños de segunda clase sobrevivió, pero el modelo les asigna ≈ 36 %. La aplicación lo advierte cuando la estimación difiere ≥ 30 puntos de lo observado.

---

## 6. API REST (FastAPI)

```bash
uvicorn api.api:app --reload
```

Documentación interactiva: http://127.0.0.1:8000/docs (Swagger) · http://127.0.0.1:8000/redoc (ReDoc)

La documentación utiliza únicamente funcionalidades nativas de OpenAPI/Swagger, sin alterar el comportamiento de la API: descripción breve en español, etiquetas por grupo, descripción detallada de cada campo (qué representa y valores aceptados), **ejemplos seleccionables** en `POST /predict` (mujer 1.ª clase, hombre 3.ª clase, niño 2.ª clase y un caso inválido) y esquemas documentados para cada respuesta. Los controles de Swagger UI y lo generado automáticamente por FastAPI (como `422 Validation Error`) permanecen en inglés, ya que la herramienta no ofrece cambio de idioma.

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/` | Información de la API |
| GET | `/health` | Estado del servicio y del modelo (503 si no está cargado) |
| POST | `/predict` | Predicción de supervivencia de un pasajero |

### Ejemplo de petición (PowerShell)

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/predict -Method Post -ContentType "application/json" `
  -Body '{"Pclass":1,"Sex":"female","Age":30,"SibSp":0,"Parch":0,"Fare":80,"Embarked":"C"}'
```

### Ejemplo de petición (curl)

```bash
curl -X POST http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d "{\"Pclass\":1,\"Sex\":\"female\",\"Age\":30,\"SibSp\":0,\"Parch\":0,\"Fare\":80,\"Embarked\":\"C\"}"
```

### Respuesta

```json
{
  "prediccion": "Sobrevive",
  "sobrevive": true,
  "probabilidad_supervivencia": 0.9526,
  "modelo": "Regresión Logística",
  "version": "20261122T005351Z"
}
```

### Validaciones

| Campo | Valores permitidos |
|---|---|
| `Pclass` | 1, 2, 3 |
| `Sex` | `male`, `female` |
| `Age` | 0 – 100 |
| `SibSp`, `Parch` | 0 – 10 |
| `Fare` | ≥ 0 |
| `Embarked` | `S`, `C`, `Q` |

Datos fuera de rango responden **422** con el formato estándar de FastAPI: cada elemento de `detail` indica el campo (`loc`), el motivo (`msg`) y el valor recibido (`input`). Los errores `500` y `503` responden `{"detail": "<mensaje>"}`.

---

## Casos de prueba

| Pasajero | Pclass | Sex | Age | SibSp | Parch | Fare | Embarked | Resultado esperado |
|---|---|---|---|---|---|---|---|---|
| Hombre joven, 3.ª clase | 3 | male | 25 | 0 | 0 | 7.25 | S | No sobrevive (≈ 10.5 %) |
| Mujer adulta, 1.ª clase | 1 | female | 30 | 0 | 0 | 80 | C | Sobrevive (≈ 95.3 %) |

Las predicciones son idénticas en el notebook, el script, Streamlit y la API.
