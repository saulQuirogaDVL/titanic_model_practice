"""Entrena, compara, evalúa y serializa el modelo de supervivencia del Titanic.

Reproduce las decisiones del experimento `notebooks/experimento_titanic.ipynb`.
Uso (desde la raíz del proyecto): python scripts/entrenar.py
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, classification_report, f1_score,
    precision_score, recall_score, roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

# Rutas relativas a la raíz del proyecto
RAIZ = Path(__file__).resolve().parent.parent
RUTA_DATOS = RAIZ / "data" / "titanic.csv"
CARPETA_MODELOS = RAIZ / "modelos"
RUTA_MODELO = CARPETA_MODELOS / "modelo_titanic.joblib"
RUTA_METRICAS = CARPETA_MODELOS / "metricas.json"

# Variables del modelo
COLUMNAS_NUMERICAS = ["Age", "SibSp", "Parch", "Fare"]
COLUMNAS_CATEGORICAS = ["Pclass", "Sex", "Embarked"]
COLUMNAS = COLUMNAS_NUMERICAS + COLUMNAS_CATEGORICAS
OBJETIVO = "Survived"

# Parámetros del experimento
SEMILLA = 42
TAMANO_PRUEBA = 0.20
UMBRAL_MEJORA = 0.02  # Mejora mínima de F1 para preferir Random Forest
METRICAS_CV = ["accuracy", "f1", "roc_auc"]


def cargar_datos():
    """Lee el dataset y valida columnas y clases."""
    if not RUTA_DATOS.exists():
        raise FileNotFoundError(f"No se encontró el dataset: {RUTA_DATOS}")

    datos = pd.read_csv(RUTA_DATOS)
    faltantes = set(COLUMNAS + [OBJETIVO]) - set(datos.columns)
    if faltantes:
        raise ValueError(f"Faltan columnas en el dataset: {sorted(faltantes)}")
    if datos[OBJETIVO].nunique() < 2:
        raise ValueError("La variable objetivo debe contener ambas clases.")

    logging.info("Datos cargados: %s registros", len(datos))
    return datos[COLUMNAS], datos[OBJETIVO]


def crear_preprocesador():
    """Imputación + escalado en numéricas; imputación + One-Hot en categóricas."""
    numericas = Pipeline([
        ("imputador", SimpleImputer(strategy="median")),
        ("escalador", StandardScaler()),
    ])
    categoricas = Pipeline([
        ("imputador", SimpleImputer(strategy="most_frequent")),
        ("codificador", OneHotEncoder(handle_unknown="ignore")),
    ])
    return ColumnTransformer([
        ("numericas", numericas, COLUMNAS_NUMERICAS),
        ("categoricas", categoricas, COLUMNAS_CATEGORICAS),
    ])


def crear_pipelines():
    """Devuelve un Pipeline nuevo (sin entrenar) por cada modelo candidato."""
    modelos = {
        "Regresión Logística": LogisticRegression(max_iter=1000, random_state=SEMILLA),
        "Random Forest": RandomForestClassifier(n_estimators=200, max_depth=6, random_state=SEMILLA),
    }
    return {
        nombre: Pipeline([("preprocesador", crear_preprocesador()), ("clasificador", modelo)])
        for nombre, modelo in modelos.items()
    }


def comparar_modelos(X_entrenamiento, y_entrenamiento):
    """Validación cruzada estratificada de 5 particiones sobre el entrenamiento."""
    validacion = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEMILLA)
    filas = []
    for nombre, pipeline in crear_pipelines().items():
        resultados = cross_validate(
            pipeline, X_entrenamiento, y_entrenamiento, cv=validacion, scoring=METRICAS_CV
        )
        fila = {"modelo": nombre}
        for metrica in METRICAS_CV:
            fila[f"{metrica}_media"] = resultados[f"test_{metrica}"].mean()
            fila[f"{metrica}_desv"] = resultados[f"test_{metrica}"].std()
        filas.append(fila)

    comparacion = pd.DataFrame(filas).set_index("modelo").round(4)
    logging.info("Comparación (validación cruzada):\n%s", comparacion.to_string())
    return comparacion


def seleccionar_modelo(comparacion):
    """Random Forest solo si mejora el F1 medio en al menos UMBRAL_MEJORA."""
    mejora_f1 = (
        comparacion.loc["Random Forest", "f1_media"]
        - comparacion.loc["Regresión Logística", "f1_media"]
    )
    nombre_modelo = "Random Forest" if mejora_f1 >= UMBRAL_MEJORA else "Regresión Logística"
    logging.info("Mejora de F1 de Random Forest: %.4f | Modelo seleccionado: %s", mejora_f1, nombre_modelo)
    return nombre_modelo


def evaluar_modelo(nombre_modelo, X_entrenamiento, X_prueba, y_entrenamiento, y_prueba):
    """Entrena el modelo seleccionado y calcula sus métricas en prueba."""
    modelo = crear_pipelines()[nombre_modelo]
    modelo.fit(X_entrenamiento, y_entrenamiento)
    y_prediccion = modelo.predict(X_prueba)
    y_probabilidad = modelo.predict_proba(X_prueba)[:, 1]

    metricas = {
        "accuracy": accuracy_score(y_prueba, y_prediccion),
        "precision": precision_score(y_prueba, y_prediccion),
        "recall": recall_score(y_prueba, y_prediccion),
        "f1": f1_score(y_prueba, y_prediccion),
        "roc_auc": roc_auc_score(y_prueba, y_probabilidad),
    }
    metricas = {clave: round(float(valor), 4) for clave, valor in metricas.items()}
    logging.info("Métricas en prueba: %s", metricas)
    logging.info(
        "Reporte de clasificación:\n%s",
        classification_report(y_prueba, y_prediccion, target_names=["No sobrevive", "Sobrevive"]),
    )
    return metricas


def guardar_modelo(nombre_modelo, X, y, comparacion, metricas_prueba, registros_entrenamiento, registros_prueba):
    """Reentrena con todos los datos y serializa el modelo y sus métricas."""
    modelo_final = crear_pipelines()[nombre_modelo]
    modelo_final.fit(X, y)

    version = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    CARPETA_MODELOS.mkdir(exist_ok=True)
    joblib.dump(
        {"modelo": modelo_final, "columnas": COLUMNAS, "nombre_modelo": nombre_modelo, "version": version},
        RUTA_MODELO,
    )

    metricas = {
        "modelo": nombre_modelo,
        "version": version,
        "validacion_cruzada": comparacion.reset_index().to_dict(orient="records"),
        "prueba": metricas_prueba,
        "registros_entrenamiento": registros_entrenamiento,
        "registros_prueba": registros_prueba,
    }
    RUTA_METRICAS.write_text(json.dumps(metricas, indent=2, ensure_ascii=False), encoding="utf-8")
    logging.info("Modelo guardado: %s | versión: %s", RUTA_MODELO, version)


def main():
    X, y = cargar_datos()
    X_entrenamiento, X_prueba, y_entrenamiento, y_prueba = train_test_split(
        X, y, test_size=TAMANO_PRUEBA, stratify=y, random_state=SEMILLA
    )
    logging.info("Entrenamiento: %s | Prueba: %s", len(X_entrenamiento), len(X_prueba))

    comparacion = comparar_modelos(X_entrenamiento, y_entrenamiento)
    nombre_modelo = seleccionar_modelo(comparacion)
    metricas_prueba = evaluar_modelo(nombre_modelo, X_entrenamiento, X_prueba, y_entrenamiento, y_prueba)
    guardar_modelo(
        nombre_modelo, X, y, comparacion, metricas_prueba,
        int(len(X_entrenamiento)), int(len(X_prueba)),
    )


if __name__ == "__main__":
    main()
