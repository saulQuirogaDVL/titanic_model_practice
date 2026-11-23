# 01_experimento_notebook.md

Crea el notebook `notebooks/experimento_titanic.ipynb` utilizando `data/titanic.csv`. Revisa antes `AGENTS.md`.

El notebook debe contener celdas Markdown y de código separadas, siguiendo estos pasos:

1. Objetivo del experimento.
2. Importación de librerías.
3. Carga de datos y visualización de los primeros registros.
4. Exploración: dimensiones, tipos de datos, valores faltantes y distribución de `Survived`.
5. Análisis visual breve: tasa de supervivencia por `Sex`, `Pclass` y distribución de `Age` (Matplotlib).
6. Selección de variables: descartar `PassengerId`, `Name`, `Ticket` y `Cabin`, justificando la decisión.
7. Separación de variables predictoras (`Pclass`, `Sex`, `Age`, `SibSp`, `Parch`, `Fare`, `Embarked`) y objetivo (`Survived`).
8. División entrenamiento/prueba 80/20 con `stratify=y` y `random_state=42`.
9. Preprocesamiento con `ColumnTransformer`:
   - Numéricas: imputación por mediana y `StandardScaler`.
   - Categóricas: imputación por moda y `OneHotEncoder(handle_unknown="ignore")`.
10. Definición de dos Pipelines:
    - `LogisticRegression(max_iter=1000, random_state=42)`.
    - `RandomForestClassifier(n_estimators=200, max_depth=6, random_state=42)`.
11. Comparación mediante validación cruzada estratificada de 5 particiones sobre el entrenamiento (Accuracy, F1, ROC-AUC), mostrando una tabla resumen.
12. Selección del mejor modelo, justificada en Markdown.
13. Entrenamiento del modelo seleccionado y evaluación en prueba: Accuracy, Precision, Recall, F1, ROC-AUC, reporte de clasificación y matriz de confusión.
14. Interpretación: coeficientes (Regresión Logística) o importancia de variables (Random Forest) del modelo seleccionado.
15. Serialización con Joblib en `modelos/modelo_titanic.joblib` del diccionario `{"modelo", "columnas", "nombre_modelo", "version"}` y de las métricas en `modelos/metricas.json`.
16. Prueba de carga del modelo serializado y predicción de un pasajero de ejemplo.
17. Conclusiones.

## Requisitos

- Código corto, sencillo y educativo.
- Explicaciones Markdown en tercera persona por etapa.
- Rutas relativas a la raíz del proyecto.
- No generar otros archivos de resultados.
