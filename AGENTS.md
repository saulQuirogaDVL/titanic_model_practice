# AGENTS.md — Predicción de supervivencia en el Titanic

## Contexto

Proyecto de clasificación binaria que predice si un pasajero del Titanic sobreviviría (`Survived`: 1 = sobrevive, 0 = no sobrevive) a partir de `data/titanic.csv` (891 registros, versión clásica de Kaggle).

Flujo del proyecto:

1. Experimento en notebook (exploración, comparación de modelos y evaluación).
2. Conversión del entrenamiento a un script ejecutable `.py`.
3. Serialización del modelo con Joblib.
4. Interfaz de predicción con Streamlit.
5. Endpoint de predicción con FastAPI.

## Tecnologías

- Python
- Pandas
- Scikit-learn
- Jupyter Notebook
- Matplotlib
- Joblib
- Streamlit
- FastAPI, Pydantic y Uvicorn

## Estructura

- `data/`: dataset original `titanic.csv` (no modificar).
- `notebooks/`: experimento `experimento_titanic.ipynb`.
- `scripts/`: entrenamiento ejecutable `entrenar.py`.
- `modelos/`: modelo serializado `modelo_titanic.joblib` y `metricas.json`.
- `app/`: interfaz Streamlit `app.py`.
- `api/`: API FastAPI `api.py`.
- `promps/`: instrucciones de desarrollo por etapa.

## Datos

- Variable objetivo: `Survived` (342 sobreviven / 549 no sobreviven).
- Variables predictoras: `Pclass`, `Sex`, `Age`, `SibSp`, `Parch`, `Fare`, `Embarked`.
- Columnas descartadas: `PassengerId`, `Name`, `Ticket`, `Cabin` (identificadores, texto libre o 77 % de valores faltantes).
- Valores faltantes: `Age` (177) se imputa con la mediana; `Embarked` (2) se imputa con la moda.
- Categorías válidas: `Sex` ∈ {male, female}; `Embarked` ∈ {S, C, Q}; `Pclass` ∈ {1, 2, 3}.

## Modelos

- Comparar únicamente dos modelos: `LogisticRegression` y `RandomForestClassifier`.
- Seleccionar el mejor mediante validación cruzada estratificada (5 particiones) usando Accuracy, F1 y ROC-AUC.
- Evaluar el modelo seleccionado sobre el conjunto de prueba (80/20, `stratify=y`, `random_state=42`).
- Si la diferencia entre ambos es mínima, preferir `LogisticRegression` por simplicidad e interpretabilidad, justificándolo en el notebook.

## Reglas

1. Mantener el preprocesamiento y el modelo dentro de un `Pipeline` de Scikit-learn (imputación, escalado y OneHotEncoder) para garantizar inferencias consistentes.
2. Serializar con Joblib un diccionario `{"modelo", "columnas", "nombre_modelo", "version"}`.
3. Streamlit y FastAPI solo cargan el modelo serializado: no reentrenan.
4. Utilizar nombres de variables en español, salvo las columnas originales del dataset.
5. Escribir explicaciones Markdown en tercera persona y comentarios técnicos breves.
6. Mantener código sencillo, legible y educativo.
7. Utilizar rutas relativas a la raíz del proyecto (construidas con `pathlib`).
8. No generar archivos adicionales sin necesidad.
9. No modificar `data/titanic.csv`.
10. Utilizar exclusivamente el intérprete Python indicado; no crear nuevos entornos.

## Entorno Python

Entorno Conda existente:

`C:\Users\OMEN\anaconda3\envs\mlops\python.exe`

## Ejecución

Los comandos se ejecutan desde la raíz del proyecto (`Practica_1/`).
