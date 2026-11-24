"""Interfaz Streamlit para predecir y analizar la supervivencia en el Titanic.

Uso (desde la raíz del proyecto): streamlit run app/app.py
"""

import json
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import streamlit as st

from ilustracion import escena, grupo_edad

# Rutas relativas a la raíz del proyecto
RAIZ = Path(__file__).resolve().parent.parent
RUTA_MODELO = RAIZ / "modelos" / "modelo_titanic.joblib"
RUTA_METRICAS = RAIZ / "modelos" / "metricas.json"
RUTA_DATOS = RAIZ / "data" / "titanic.csv"

# Etiquetas en español -> valores originales del dataset
CLASES = {1: "Primera clase", 2: "Segunda clase", 3: "Tercera clase"}
SEXOS = {"female": "Mujer", "male": "Hombre"}
PUERTOS = {"S": "Southampton", "C": "Cherbourg", "Q": "Queenstown"}
NOMBRES_VARIABLES = {
    "Sex": "Sexo", "Pclass": "Clase", "Age": "Edad", "SibSp": "Hermanos/cónyuges",
    "Parch": "Padres/hijos", "Fare": "Tarifa", "Embarked": "Puerto",
}
COLOR_POSITIVO, COLOR_NEGATIVO = "#2E7D32", "#C62828"
MODO_ILUSTRADO, MODO_CLASICO = "🎨 Ilustrado", "📋 Clásico"

# Perfiles predefinidos para demostraciones
EJEMPLOS = {
    "Mujer · 1.ª clase": {"Pclass": 1, "Sex": "female", "Age": 30.0, "SibSp": 0, "Parch": 0, "Fare": 80.0, "Embarked": "C"},
    "Hombre · 3.ª clase": {"Pclass": 3, "Sex": "male", "Age": 25.0, "SibSp": 0, "Parch": 0, "Fare": 7.25, "Embarked": "S"},
    "Niño · 2.ª clase": {"Pclass": 2, "Sex": "male", "Age": 6.0, "SibSp": 1, "Parch": 1, "Fare": 30.0, "Embarked": "S"},
}
VALORES_INICIALES = {"Pclass": 3, "Sex": "female", "Age": 30.0, "SibSp": 0, "Parch": 0, "Fare": 15.0, "Embarked": "S"}

METRICAS_DESCRIPCION = {
    "accuracy": ("Accuracy", "Proporción total de pasajeros clasificados correctamente."),
    "precision": ("Precision", "De los que el modelo predice que sobreviven, cuántos realmente sobrevivieron."),
    "recall": ("Recall", "De los que realmente sobrevivieron, cuántos detecta el modelo."),
    "f1": ("F1", "Equilibrio entre Precision y Recall."),
    "roc_auc": ("ROC-AUC", "Capacidad de ordenar pasajeros por probabilidad (1 = perfecto, 0.5 = azar)."),
}


# ---------------------------------------------------------------- Carga de recursos
@st.cache_resource
def cargar_modelo():
    return joblib.load(RUTA_MODELO)


@st.cache_data
def cargar_datos():
    return pd.read_csv(RUTA_DATOS)


@st.cache_data
def cargar_metricas():
    if RUTA_METRICAS.exists():
        return json.loads(RUTA_METRICAS.read_text(encoding="utf-8"))
    return None


# ---------------------------------------------------------------- Lógica del modelo
def predecir(modelo, columnas, pasajero):
    """Devuelve la clase predicha y la probabilidad de supervivencia."""
    datos = pd.DataFrame([pasajero])[columnas]
    return int(modelo.predict(datos)[0]), float(modelo.predict_proba(datos)[0, 1])


def nivel_confianza(probabilidad):
    distancia = abs(probabilidad - 0.5)
    if distancia >= 0.20:
        return "Alta"
    if distancia >= 0.10:
        return "Media"
    return "Incierta"


def contribuciones(modelo, columnas, pasajero):
    """Aporte de cada variable original a la predicción del pasajero."""
    preprocesador = modelo.named_steps["preprocesador"]
    clasificador = modelo.named_steps["clasificador"]
    nombres = [nombre.split("__", 1)[1] for nombre in preprocesador.get_feature_names_out()]

    if hasattr(clasificador, "coef_"):
        valores = preprocesador.transform(pd.DataFrame([pasajero])[columnas])
        valores = valores.toarray() if hasattr(valores, "toarray") else np.asarray(valores)
        aportes = clasificador.coef_[0] * valores[0]  # coeficiente × valor transformado
    else:
        aportes = clasificador.feature_importances_

    resultado = {}
    for columna in columnas:
        mascara = [n == columna or n.startswith(f"{columna}_") for n in nombres]
        resultado[columna] = float(np.sum(np.array(aportes)[mascara]))

    tabla = pd.DataFrame({
        "Columna": list(resultado),
        "Variable": [NOMBRES_VARIABLES[c] for c in resultado],
        "Aporte": list(resultado.values()),
    })
    tabla["Color"] = np.where(tabla["Aporte"] >= 0, COLOR_POSITIVO, COLOR_NEGATIVO)
    return tabla, hasattr(clasificador, "coef_")


def simular_edades(modelo, columnas, pasajero):
    """Probabilidad del mismo pasajero variando la edad de 0 a 80 años."""
    edades = np.arange(0, 81)
    datos = pd.DataFrame([{**pasajero, "Age": float(edad)} for edad in edades])[columnas]
    return pd.DataFrame({"Edad": edades, "Probabilidad (%)": modelo.predict_proba(datos)[:, 1] * 100})


def tasa_supervivencia(datos, columna, etiquetas=None):
    """Tasa de supervivencia (%) agrupada por una columna."""
    tabla = datos.groupby(columna, observed=True)["Survived"].mean().mul(100).round(1).reset_index()
    if etiquetas:
        tabla[columna] = tabla[columna].map(etiquetas)
    return tabla.rename(columns={"Survived": "Supervivencia (%)"})


# ---------------------------------------------------------------- Textos amigables
def sujeto(pasajero):
    if grupo_edad(pasajero["Age"]) == "nino":
        return "La niña" if pasajero["Sex"] == "female" else "El niño"
    return "La pasajera" if pasajero["Sex"] == "female" else "El pasajero"


def describir_factor(columna, pasajero):
    """Frase natural que describe el valor de una variable del pasajero."""
    valor = pasajero[columna]
    if columna == "Sex":
        return "ser mujer" if valor == "female" else "ser hombre"
    if columna == "Pclass":
        return f"viajar en {CLASES[valor].lower()}"
    if columna == "Age":
        return f"tener {valor:.0f} años"
    if columna == "SibSp":
        return "viajar sin hermanos ni cónyuge" if valor == 0 else f"viajar con {valor} hermano(s)/cónyuge"
    if columna == "Parch":
        return "viajar sin padres ni hijos" if valor == 0 else f"viajar con {valor} padre(s)/hijo(s)"
    if columna == "Fare":
        return f"haber pagado £{valor:.0f}"
    return f"embarcar en {PUERTOS[valor]}"


def resumen_factores(tabla, pasajero):
    """Variables que más ayudaron y más perjudicaron, en lenguaje natural."""
    ayudaron = tabla[tabla["Aporte"] > 0.05].nlargest(2, "Aporte")["Columna"]
    perjudicaron = tabla[tabla["Aporte"] < -0.05].nsmallest(2, "Aporte")["Columna"]
    unir = lambda columnas: " y ".join(describir_factor(c, pasajero) for c in columnas)
    lineas = []
    if len(ayudaron):
        lineas.append(f"👍 **Lo que más le ayudó:** {unir(ayudaron)}.")
    if len(perjudicaron):
        lineas.append(f"👎 **Lo que más le perjudicó:** {unir(perjudicaron)}.")
    return "  \n".join(lineas)


# ---------------------------------------------------------------- Interacción
def pasajero_actual():
    return {campo: st.session_state[campo] for campo in VALORES_INICIALES}


def aplicar_ejemplo(nombre):
    """Carga un perfil de ejemplo en los controles y solicita la predicción."""
    for campo, valor in EJEMPLOS[nombre].items():
        st.session_state[campo] = valor
    st.session_state["predecir_ejemplo"] = True


def mostrar_ejemplos():
    st.markdown("**Probar con un pasajero de ejemplo**")
    with st.container(horizontal=True):
        for nombre in EJEMPLOS:
            st.button(nombre, on_click=aplicar_ejemplo, args=(nombre,), width="stretch")


def mostrar_campos():
    """Controles del pasajero en dos columnas (se apilan en móviles)."""
    datos_personales, datos_viaje = st.columns(2, gap="medium")
    with datos_personales:
        st.markdown("**👤 Datos personales**")
        st.selectbox("Sexo", options=list(SEXOS), format_func=SEXOS.get, key="Sex",
                     help="Sexo del pasajero.")
        st.number_input("Edad (años)", min_value=0.0, max_value=100.0, step=1.0, format="%.0f", key="Age",
                        help="Edad del pasajero en años.")
        st.number_input("Hermanos / cónyuges a bordo", min_value=0, max_value=10, step=1, key="SibSp",
                        help="Cantidad de hermanos o cónyuges que viajaban con el pasajero.")
        st.number_input("Padres / hijos a bordo", min_value=0, max_value=10, step=1, key="Parch",
                        help="Cantidad de padres o hijos que viajaban con el pasajero.")
    with datos_viaje:
        st.markdown("**🎫 Datos del viaje**")
        st.selectbox("Clase del boleto", options=list(CLASES), format_func=CLASES.get, key="Pclass",
                     help="La clase determinaba la ubicación del camarote en el barco.")
        st.number_input("Tarifa pagada (libras)", min_value=0.0, max_value=600.0, step=1.0, key="Fare",
                        help="Precio del boleto. De 0 a 512 libras.")
        st.selectbox("Puerto de embarque", options=list(PUERTOS), format_func=PUERTOS.get, key="Embarked",
                     help="Puerto donde el pasajero subió al barco.")


def mostrar_comparacion(datos, pasajero, probabilidad):
    """Tasa real de supervivencia de pasajeros con el mismo perfil (niños ≤ 12 años como grupo propio)."""
    misma_clase = datos[datos["Pclass"] == pasajero["Pclass"]]
    if pasajero["Age"] <= 12:
        similares, perfil = misma_clase[misma_clase["Age"] <= 12], "niños de 0 a 12 años"
    else:
        similares = misma_clase[(misma_clase["Sex"] == pasajero["Sex"]) & (misma_clase["Age"].isna() | (misma_clase["Age"] > 12))]
        perfil = "mujeres" if pasajero["Sex"] == "female" else "hombres"
    if similares.empty:
        return
    tasa_real = similares["Survived"].mean()
    st.info(
        f"De los **{len(similares)}** pasajeros reales con este perfil "
        f"({perfil}, {CLASES[pasajero['Pclass']].lower()}), sobrevivió el **{tasa_real:.1%}**.",
        icon="📊",
    )
    if abs(tasa_real - probabilidad) >= 0.30:
        st.caption(
            "⚠️ La estimación del modelo difiere de lo observado en este grupo: la Regresión Logística "
            "suma el efecto de cada variable por separado y no capta bien combinaciones específicas "
            "(por ejemplo, edad y clase a la vez)."
        )


def mostrar_explicacion(tabla, es_lineal):
    with st.container(border=True):
        st.markdown("**¿Por qué este resultado?**")
        st.caption(
            "Barras verdes aumentan la probabilidad de sobrevivir; barras rojas la disminuyen."
            if es_lineal else "Importancia de cada variable en el modelo."
        )
        st.bar_chart(tabla, x="Variable", y="Aporte", color="Color", horizontal=True,
                     sort="-Aporte", x_label="Aporte a la predicción", y_label="", height=300)


def mostrar_simulacion(modelo, columnas, pasajero):
    with st.container(border=True):
        st.markdown("**¿Y si tuviera otra edad?**")
        st.caption("Probabilidad estimada para este mismo pasajero variando únicamente la edad.")
        st.line_chart(simular_edades(modelo, columnas, pasajero), x="Edad", y="Probabilidad (%)",
                      color=COLOR_POSITIVO, height=260)


# ---------------------------------------------------------------- Modos de la pestaña Predicción
def mostrar_modo_clasico(modelo, columnas, datos):
    """Formulario con botón y resultado detallado."""
    mostrar_ejemplos()
    with st.form("formulario_pasajero", border=True):
        mostrar_campos()
        enviado = st.form_submit_button("Predecir supervivencia", type="primary", width="stretch",
                                        icon=":material/query_stats:")
    if not (enviado or st.session_state.pop("predecir_ejemplo", False)):
        return

    pasajero = pasajero_actual()
    prediccion, probabilidad = predecir(modelo, columnas, pasajero)
    with st.container(border=True):
        if prediccion == 1:
            st.success("**Sobrevive** — el modelo estima que este pasajero habría sobrevivido.", icon="✅")
        else:
            st.error("**No sobrevive** — el modelo estima que este pasajero no habría sobrevivido.", icon="❌")
        with st.container(horizontal=True):
            st.metric("Probabilidad de supervivencia", f"{probabilidad:.1%}", border=True)
            st.metric("Confianza", nivel_confianza(probabilidad), border=True,
                      help="Alta: probabilidad ≥ 70 % o ≤ 30 %. Media: entre 30–40 % o 60–70 %. Incierta: 40–60 %.")
        st.progress(probabilidad)

    mostrar_comparacion(datos, pasajero, probabilidad)
    mostrar_explicacion(*contribuciones(modelo, columnas, pasajero))
    mostrar_simulacion(modelo, columnas, pasajero)


def mostrar_modo_ilustrado(modelo, columnas, datos):
    """Escena cartoon junto a los controles; se actualiza en vivo al cambiar los datos."""
    st.session_state.pop("predecir_ejemplo", None)
    mostrar_ejemplos()

    pasajero = pasajero_actual()
    prediccion, probabilidad = predecir(modelo, columnas, pasajero)
    tabla, es_lineal = contribuciones(modelo, columnas, pasajero)

    # Escena a la izquierda y controles a la derecha (se apilan en móviles)
    columna_escena, columna_controles = st.columns([1.15, 1], gap="large")
    with columna_escena:
        st.image(escena(pasajero, prediccion, probabilidad), width="stretch")
        with st.container(border=True):
            if prediccion == 1:
                st.markdown(f"#### 🎉 ¡{sujeto(pasajero)} consigue un lugar en un bote salvavidas!")
            else:
                st.markdown(f"#### 🌊 {sujeto(pasajero)} no logra subir a un bote salvavidas")
            st.markdown(f"Probabilidad estimada de sobrevivir: **{probabilidad:.0%}** "
                        f"· Confianza **{nivel_confianza(probabilidad).lower()}**")
            st.progress(probabilidad)
            if es_lineal:
                st.markdown(resumen_factores(tabla, pasajero))

    with columna_controles, st.container(border=True):
        st.caption("✏️ Cambie los datos y observe cómo cambia el personaje y su destino.")
        mostrar_campos()

    with st.expander("Ver análisis detallado", icon=":material/analytics:"):
        mostrar_comparacion(datos, pasajero, probabilidad)
        mostrar_explicacion(tabla, es_lineal)
        mostrar_simulacion(modelo, columnas, pasajero)


def cambiar_modo(modo):
    st.session_state["modo"] = modo


def mostrar_selector_modo():
    """Dos botones visibles; el de la vista ilustrada siempre se destaca para invitar a probarla."""
    activo = st.session_state["modo"]
    with st.container(horizontal=True):
        for modo, etiqueta_activa, etiqueta_invitacion in [
            (MODO_CLASICO, "📋 Vista clásica", "📋 Volver a la vista clásica"),
            (MODO_ILUSTRADO, "🎨 Vista ilustrada", "🎨 ✨ Probar vista ilustrada"),
        ]:
            es_activo = modo == activo
            st.button(
                etiqueta_activa if es_activo else etiqueta_invitacion,
                type="primary" if modo == MODO_ILUSTRADO else "secondary",
                icon=":material/check_circle:" if es_activo else None,
                on_click=cambiar_modo, args=(modo,), width="stretch", key=f"boton_{modo}",
            )
    if activo == MODO_CLASICO:
        st.caption("✨ ¿Algo más divertido? En la **vista ilustrada** un personaje cambia según los datos que elija.")


# ---------------------------------------------------------------- Otras pestañas
def mostrar_analisis(datos):
    st.markdown("Análisis de los **891 pasajeros** del dataset histórico.")
    with st.container(horizontal=True):
        st.metric("Pasajeros", f"{len(datos):,}", border=True)
        st.metric("Sobrevivientes", f"{int(datos['Survived'].sum()):,}", border=True)
        st.metric("Tasa de supervivencia", f"{datos['Survived'].mean():.1%}", border=True)

    columna_1, columna_2 = st.columns(2)
    with columna_1, st.container(border=True):
        st.markdown("**Por sexo**")
        st.bar_chart(tasa_supervivencia(datos, "Sex", SEXOS), x="Sex", y="Supervivencia (%)",
                     x_label="", height=250)
    with columna_2, st.container(border=True):
        st.markdown("**Por clase**")
        st.bar_chart(tasa_supervivencia(datos, "Pclass", CLASES), x="Pclass", y="Supervivencia (%)",
                     x_label="", height=250)

    with st.container(border=True):
        st.markdown("**Por clase y sexo**")
        combinada = datos.assign(Clase=datos["Pclass"].map(CLASES), Sexo=datos["Sex"].map(SEXOS))
        combinada = combinada.groupby(["Clase", "Sexo"])["Survived"].mean().mul(100).round(1)
        st.bar_chart(combinada.unstack("Sexo"), stack=False, x_label="", y_label="Supervivencia (%)",
                     color=["#8FA9C8", "#1F3A5F"], height=280)

    columna_3, columna_4 = st.columns(2)
    with columna_3, st.container(border=True):
        st.markdown("**Por rango de edad**")
        rangos = datos.assign(
            Edad=pd.cut(datos["Age"], bins=[0, 12, 18, 30, 50, 100], include_lowest=True,
                        labels=["0–12", "13–18", "19–30", "31–50", "51+"])
        )
        st.bar_chart(tasa_supervivencia(rangos, "Edad"), x="Edad", y="Supervivencia (%)",
                     x_label="", height=250)
    with columna_4, st.container(border=True):
        st.markdown("**Por puerto de embarque**")
        st.bar_chart(tasa_supervivencia(datos, "Embarked", PUERTOS), x="Embarked", y="Supervivencia (%)",
                     x_label="", height=250)

    with st.container(border=True):
        st.markdown("**¿Cómo influye cada variable?**")
        st.markdown(
            "- **Sexo:** se aplicó la regla *“mujeres y niños primero”*; el 74 % de las mujeres sobrevivió frente al 19 % de los hombres.\n"
            "- **Clase:** los camarotes de primera clase estaban en las cubiertas superiores, cerca de los botes salvavidas; la tercera clase, en las inferiores.\n"
            "- **Edad:** los niños tuvieron prioridad (58 % de supervivencia entre 0 y 12 años); las personas mayores tuvieron más dificultades para evacuar.\n"
            "- **Familia a bordo:** viajar con 1–3 familiares ayudó, pero las familias numerosas (casi todas de tercera clase) tuvieron tasas muy bajas.\n"
            "- **Tarifa y puerto:** reflejan principalmente la clase del pasajero; por sí solos aportan poca información al modelo."
        )


def mostrar_modelo(paquete, metricas):
    version = paquete["version"]
    try:
        fecha = datetime.strptime(version, "%Y%m%dT%H%M%SZ").strftime("%d/%m/%Y %H:%M UTC")
    except ValueError:
        fecha = version

    with st.container(horizontal=True):
        st.metric("Algoritmo", paquete["nombre_modelo"], border=True)
        st.metric("Entrenado", fecha, border=True)

    if not metricas:
        st.warning("No se encontró `modelos/metricas.json`. Ejecute `python scripts/entrenar.py`.")
        return

    st.markdown("**Desempeño en el conjunto de prueba**")
    with st.container(horizontal=True):
        for clave, valor in metricas["prueba"].items():
            nombre, descripcion = METRICAS_DESCRIPCION.get(clave, (clave, ""))
            st.metric(nombre, f"{valor:.2f}", help=descripcion, border=True)
    st.caption(f"Evaluado con {metricas['registros_prueba']} pasajeros no utilizados en el entrenamiento.")

    st.markdown("**Comparación de modelos (validación cruzada, 5 particiones)**")
    comparacion = pd.DataFrame(metricas["validacion_cruzada"])[
        ["modelo", "accuracy_media", "f1_media", "roc_auc_media"]
    ].rename(columns={"modelo": "Modelo", "accuracy_media": "Accuracy", "f1_media": "F1", "roc_auc_media": "ROC-AUC"})
    st.dataframe(comparacion, hide_index=True, width="stretch")
    st.markdown(
        "Ambos modelos obtuvieron un rendimiento prácticamente equivalente. Se eligió la "
        "**Regresión Logística** por ser más simple, rápida e interpretable: permite explicar "
        "cuánto aporta cada variable a cada predicción."
        if paquete["nombre_modelo"] == "Regresión Logística"
        else "Se eligió **Random Forest** por superar a la Regresión Logística en F1."
    )


# ---------------------------------------------------------------- Página
st.session_state.setdefault("modo", MODO_CLASICO)
# La vista ilustrada usa todo el ancho para mostrar la escena junto a los controles
st.set_page_config(page_title="Supervivencia en el Titanic", page_icon="🚢",
                   layout="wide" if st.session_state["modo"] == MODO_ILUSTRADO else "centered")

st.title("🚢 Supervivencia en el Titanic")
st.markdown("Estime si un pasajero habría sobrevivido al naufragio y descubra qué factores influyeron.")

if not RUTA_MODELO.exists():
    st.error("No se encontró el modelo entrenado. Ejecute primero: `python scripts/entrenar.py`")
    st.stop()

paquete = cargar_modelo()
modelo, columnas = paquete["modelo"], paquete["columnas"]
datos = cargar_datos()
for campo, valor in VALORES_INICIALES.items():
    st.session_state.setdefault(campo, valor)

st.caption(f"Modelo: {paquete['nombre_modelo']} · Versión {paquete['version']}")

tab_prediccion, tab_analisis, tab_modelo = st.tabs(
    ["🔮 Predicción", "📊 ¿Quién sobrevive?", "🧠 Sobre el modelo"]
)

with tab_prediccion:
    mostrar_selector_modo()
    if st.session_state["modo"] == MODO_CLASICO:
        mostrar_modo_clasico(modelo, columnas, datos)
    else:
        mostrar_modo_ilustrado(modelo, columnas, datos)

with tab_analisis:
    mostrar_analisis(datos)

with tab_modelo:
    mostrar_modelo(paquete, cargar_metricas())

st.divider()
st.caption("Datos: Titanic  · 891 pasajeros")
