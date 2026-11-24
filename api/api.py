"""API REST para predecir la supervivencia de un pasajero del Titanic.

Uso (desde la raíz del proyecto): uvicorn api.api:app --reload
Documentación interactiva: http://127.0.0.1:8000/docs (Swagger) y /redoc (ReDoc)
"""

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

import joblib
import pandas as pd
from fastapi import Body, FastAPI, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict, Field

# Ruta relativa a la raíz del proyecto
RAIZ = Path(__file__).resolve().parent.parent
RUTA_MODELO = RAIZ / "modelos" / "modelo_titanic.joblib"
VERSION_API = "1.1.0"


# ---------------------------------------------------------------- Documentación general
DESCRIPCION = (
    "Predice si un pasajero del Titanic habría sobrevivido al naufragio, "
    "utilizando un modelo de Regresión Logística entrenado con Scikit-learn."
)

ETIQUETAS = [
    {"name": "General", "description": "Información del servicio y estado del modelo."},
    {"name": "Predicción", "description": "Estimación de supervivencia de un pasajero."},
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Carga el modelo una sola vez al iniciar la aplicación."""
    app.state.paquete = joblib.load(RUTA_MODELO) if RUTA_MODELO.exists() else None
    yield


app = FastAPI(
    title="API de Supervivencia del Titanic",
    description=DESCRIPCION,
    version=VERSION_API,
    openapi_tags=ETIQUETAS,
    lifespan=lifespan,
    swagger_ui_parameters={
        "docExpansion": "list",           # endpoints visibles al abrir
        "defaultModelsExpandDepth": 1,    # esquemas listados, sin expandir
        "displayRequestDuration": True,   # muestra el tiempo de respuesta
        "tryItOutEnabled": True,          # formularios editables de inmediato
    },
)


# ---------------------------------------------------------------- Esquemas de entrada
class DatosPasajero(BaseModel):
    """Datos de un pasajero. Los nombres respetan las columnas originales del dataset."""

    model_config = ConfigDict(title="Datos del pasajero")

    Pclass: Literal[1, 2, 3] = Field(
        ..., title="Clase del boleto",
        description="Clase del boleto, asociada al nivel socioeconómico y a la ubicación del camarote "
                    "(la primera clase estaba más cerca de los botes salvavidas). "
                    "Valores: `1` = Primera, `2` = Segunda, `3` = Tercera.",
        examples=[1],
    )
    Sex: Literal["male", "female"] = Field(
        ..., title="Sexo",
        description="Sexo del pasajero. Valores: `\"male\"` = Hombre, `\"female\"` = Mujer.",
        examples=["female"],
    )
    Age: float = Field(
        ..., ge=0, le=100, title="Edad",
        description="Edad del pasajero en años, de 0 a 100. Admite decimales (por ejemplo, `0.5` para un bebé de 6 meses).",
        examples=[30],
    )
    SibSp: int = Field(
        ..., ge=0, le=10, title="Hermanos o cónyuges a bordo",
        description="Número de hermanos, hermanas, esposo o esposa que viajaban con el pasajero. Entero de 0 a 10.",
        examples=[0],
    )
    Parch: int = Field(
        ..., ge=0, le=10, title="Padres o hijos a bordo",
        description="Número de padres o hijos que viajaban con el pasajero. Entero de 0 a 10.",
        examples=[0],
    )
    Fare: float = Field(
        ..., ge=0, title="Tarifa",
        description="Tarifa pagada por el boleto, en libras esterlinas de 1912. "
                    "Debe ser mayor o igual a 0.",
        examples=[80.0],
    )
    Embarked: Literal["S", "C", "Q"] = Field(
        ..., title="Puerto de embarque",
        description="Puerto donde el pasajero subió al barco. "
                    "Valores: `\"S\"` = Southampton, `\"C\"` = Cherbourg, `\"Q\"` = Queenstown.",
        examples=["C"],
    )


EJEMPLOS_PASAJERO = {
    "mujer_primera": {
        "summary": "Mujer · 1.ª clase (sobrevive)",
        "description": "Mujer de 30 años en primera clase, embarcada en Cherbourg.",
        "value": {"Pclass": 1, "Sex": "female", "Age": 30, "SibSp": 0, "Parch": 0, "Fare": 80.0, "Embarked": "C"},
    },
    "hombre_tercera": {
        "summary": "Hombre · 3.ª clase (no sobrevive)",
        "description": "Hombre de 25 años en tercera clase, viajando solo desde Southampton.",
        "value": {"Pclass": 3, "Sex": "male", "Age": 25, "SibSp": 0, "Parch": 0, "Fare": 7.25, "Embarked": "S"},
    },
    "nino_segunda": {
        "summary": "Niño · 2.ª clase con familia",
        "description": "Niño de 6 años en segunda clase, con un hermano y uno de sus padres a bordo.",
        "value": {"Pclass": 2, "Sex": "male", "Age": 6, "SibSp": 1, "Parch": 1, "Fare": 30.0, "Embarked": "S"},
    },
    "invalido": {
        "summary": "Datos inválidos (error 422)",
        "description": "Ejemplo con valores fuera de rango para observar la respuesta de validación (422).",
        "value": {"Pclass": 4, "Sex": "otro", "Age": -1, "SibSp": 0, "Parch": 0, "Fare": 7.25, "Embarked": "X"},
    },
}


# ---------------------------------------------------------------- Esquemas de respuesta
class RespuestaPrediccion(BaseModel):
    model_config = ConfigDict(title="Resultado de la predicción")

    prediccion: Literal["Sobrevive", "No sobrevive"] = Field(
        ..., title="Predicción", description="Resultado en texto, listo para mostrar al usuario.", examples=["Sobrevive"])
    sobrevive: bool = Field(
        ..., title="¿Sobrevive?", description="`true` si el modelo predice supervivencia; útil para lógica en el cliente.", examples=[True])
    probabilidad_supervivencia: float = Field(
        ..., ge=0, le=1, title="Probabilidad de supervivencia",
        description="Probabilidad estimada entre 0 y 1 (4 decimales). La predicción es \"Sobrevive\" cuando supera 0.5.",
        examples=[0.9526])
    modelo: str = Field(..., title="Modelo", description="Algoritmo utilizado.", examples=["Regresión Logística"])
    version: str = Field(..., title="Versión", description="Versión del modelo (fecha UTC de entrenamiento).",
                         examples=["20261122T005351Z"])


class RespuestaInicio(BaseModel):
    model_config = ConfigDict(title="Información de la API")

    nombre: str = Field(..., description="Nombre del servicio.")
    version: str = Field(..., description="Versión de la API.")
    descripcion: str = Field(..., description="Propósito del servicio.")
    endpoints: dict[str, str] = Field(..., description="Endpoints disponibles y su función.")


class RespuestaSalud(BaseModel):
    model_config = ConfigDict(title="Estado del servicio")

    estado: Literal["activo"] = Field(..., description="Estado del servicio.")
    modelo_cargado: bool = Field(..., description="Indica si el modelo está disponible para predecir.")
    modelo: str = Field(..., description="Algoritmo cargado.", examples=["Regresión Logística"])
    version: str = Field(..., description="Versión del modelo cargado.", examples=["20261122T005351Z"])


class ErrorSimple(BaseModel):
    """Formato estándar de FastAPI para errores lanzados con HTTPException."""

    model_config = ConfigDict(title="Error del servicio")

    detail: str = Field(..., description="Descripción del error.")


RESPUESTA_503 = {
    "model": ErrorSimple,
    "description": "El modelo no está disponible.",
    "content": {"application/json": {"example": {
        "detail": "El modelo no está disponible. Ejecute: python scripts/entrenar.py"}}},
}


def obtener_paquete(request: Request):
    """Devuelve el modelo cargado o responde 503 si no está disponible."""
    paquete = request.app.state.paquete
    if paquete is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El modelo no está disponible. Ejecute: python scripts/entrenar.py",
        )
    return paquete


# ---------------------------------------------------------------- Endpoints
@app.get(
    "/", tags=["General"], response_model=RespuestaInicio,
    summary="Información de la API",
    description="Devuelve el nombre, la versión y la lista de endpoints disponibles.",
    response_description="Información general del servicio.",
)
def inicio():
    return {
        "nombre": "API de Supervivencia del Titanic",
        "version": VERSION_API,
        "descripcion": "Predice si un pasajero del Titanic habría sobrevivido al naufragio.",
        "endpoints": {
            "GET /": "Información básica de la API",
            "GET /health": "Estado del servicio y del modelo",
            "POST /predict": "Predicción de supervivencia de un pasajero",
            "GET /docs": "Documentación interactiva (Swagger)",
            "GET /redoc": "Documentación de referencia (ReDoc)",
        },
    }


@app.get(
    "/health", tags=["General"], response_model=RespuestaSalud,
    summary="Estado del servicio",
    description="Indica si el servicio está activo y si el modelo está cargado, con su nombre y versión. "
                "Se recomienda consultarlo antes de enviar predicciones.",
    response_description="El servicio y el modelo están disponibles.",
    responses={503: RESPUESTA_503},
)
def estado_salud(request: Request):
    paquete = obtener_paquete(request)
    return {
        "estado": "activo",
        "modelo_cargado": True,
        "modelo": paquete["nombre_modelo"],
        "version": paquete["version"],
    }


@app.post(
    "/predict", tags=["Predicción"], response_model=RespuestaPrediccion,
    summary="Predecir la supervivencia de un pasajero",
    description="Recibe los datos de un pasajero y devuelve si habría sobrevivido junto con la probabilidad estimada.\n\n"
                "Seleccione uno de los **ejemplos** en el cuerpo de la petición para probar distintos perfiles, "
                "incluido un caso inválido que muestra la respuesta de validación.",
    response_description="Predicción realizada correctamente.",
    responses={  # el 422 lo documenta FastAPI de forma nativa (HTTPValidationError)
        503: RESPUESTA_503,
        500: {
            "model": ErrorSimple,
            "description": "Error inesperado durante la predicción.",
            "content": {"application/json": {"example": {"detail": "Error durante la predicción: <detalle técnico>"}}},
        },
    },
)
def predecir(request: Request, pasajero: DatosPasajero = Body(..., openapi_examples=EJEMPLOS_PASAJERO)):
    paquete = obtener_paquete(request)
    try:
        # DataFrame de una fila con el orden de columnas usado en el entrenamiento
        datos = pd.DataFrame([pasajero.model_dump()])[paquete["columnas"]]
        prediccion = int(paquete["modelo"].predict(datos)[0])
        probabilidad = float(paquete["modelo"].predict_proba(datos)[0, 1])
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error durante la predicción: {error}",
        )

    return RespuestaPrediccion(
        prediccion="Sobrevive" if prediccion == 1 else "No sobrevive",
        sobrevive=prediccion == 1,
        probabilidad_supervivencia=round(probabilidad, 4),
        modelo=paquete["nombre_modelo"],
        version=paquete["version"],
    )
