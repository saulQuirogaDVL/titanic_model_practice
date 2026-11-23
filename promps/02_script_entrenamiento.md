# 02_script_entrenamiento.md

Convierte el experimento `notebooks/experimento_titanic.ipynb` en el script ejecutable `scripts/entrenar.py`.

Antes de implementar, revisa `AGENTS.md` y el notebook para reutilizar exactamente las mismas decisiones (variables, preprocesamiento, modelos, criterio de selección y formato de serialización).

## Requisitos

1. Crear `scripts/entrenar.py` ejecutable con `python scripts/entrenar.py` desde la raíz del proyecto.
2. Estructurar el código en funciones pequeñas y una función `main()` protegida con `if __name__ == "__main__":`:
   - `cargar_datos()`: lee `data/titanic.csv` y valida que existan las columnas requeridas y ambas clases de `Survived`.
   - `crear_preprocesador()`: mismo `ColumnTransformer` del notebook (mediana + `StandardScaler` en numéricas; moda + `OneHotEncoder(handle_unknown="ignore")` en categóricas).
   - `crear_pipelines()`: Pipelines de `LogisticRegression(max_iter=1000, random_state=42)` y `RandomForestClassifier(n_estimators=200, max_depth=6, random_state=42)`.
   - `comparar_modelos()`: validación cruzada estratificada de 5 particiones (Accuracy, F1, ROC-AUC) sobre el conjunto de entrenamiento.
   - `seleccionar_modelo()`: Random Forest solo si mejora el F1 medio en al menos `0.02`; en caso contrario, Regresión Logística.
   - `evaluar_modelo()`: entrenamiento y métricas en prueba (Accuracy, Precision, Recall, F1, ROC-AUC) y reporte de clasificación.
   - `guardar_modelo()`: reentrenamiento con todos los datos y serialización.
3. División entrenamiento/prueba 80/20 con `stratify=y` y `random_state=42`.
4. Serializar con Joblib en `modelos/modelo_titanic.joblib` el diccionario `{"modelo", "columnas", "nombre_modelo", "version"}` (versión con fecha UTC `%Y%m%dT%H%M%SZ`).
5. Guardar las métricas en `modelos/metricas.json` con la misma estructura que genera el notebook.
6. Definir constantes al inicio del archivo: rutas, columnas numéricas, columnas categóricas, semilla y umbral de mejora.
7. Construir las rutas con `pathlib` a partir de la ubicación del script, para que funcione desde cualquier directorio.
8. Utilizar `logging` en lugar de `print` para informar cada etapa (carga, comparación, modelo seleccionado, métricas y ruta del modelo guardado).
9. Manejar errores básicos: archivo de datos inexistente y columnas faltantes, con mensajes claros.
10. Agregar un docstring de módulo y docstrings breves por función.

## Validación

- Ejecutar `python scripts/entrenar.py` con el intérprete indicado en `AGENTS.md`.
- Verificar que las métricas obtenidas coincidan con las del notebook.
- Verificar que el modelo guardado se pueda cargar y predecir un pasajero de ejemplo.

## Restricciones

- No modificar el notebook ni `data/titanic.csv`.
- No agregar modelos ni hiperparámetros distintos a los del notebook.
- No crear archivos adicionales fuera de `scripts/entrenar.py` y los artefactos de `modelos/`.
- Mantener el código corto, sencillo y educativo, con nombres en español.
