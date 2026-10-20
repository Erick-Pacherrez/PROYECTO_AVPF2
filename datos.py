"""Carga, nombres en español y variables calculadas. Todos los scripts usan este archivo."""
from pathlib import Path
import numpy as np
import pandas as pd

RUTA = Path(__file__).resolve().parent / "projects.csv"

RENOMBRAR = {
    "project_id": "id_proyecto",
    "project_type": "tipo_proyecto",
    "floors": "pisos",
    "area_m2": "area_m2",
    "complexity": "complejidad_estructural",
    "contractor_capability": "capacidad_contratista",
    "resource_availability": "disponibilidad_recursos",
    "management_maturity": "madurez_gestion",
    "weather_exposure": "exposicion_clima",
    "supply_chain_exposure": "exposicion_suministro",
    "technology_maturity": "madurez_tecnologica",
    "planned_duration_days": "duracion_dias",
    "planned_cost": "costo_planificado_soles",
    "split": "particion",
}

TIPOS = {
    "Hospital": "Hospital", "Commercial": "Comercial", "Industrial": "Industrial",
    "Institutional": "Institucional", "Residential": "Residencial",
}

# --- Supuestos editables del grupo (justificarlos en el informe) ---
# Reserva de contingencia como % del costo, según el nivel de riesgo (valores de ejemplo)
CONTINGENCIA = {"Bajo": 0.05, "Medio": 0.10, "Alto": 0.15}
# Una obra es "crítica relativa" si su costo por m² supera en más de este % el promedio de su tipo
UMBRAL_DESVIACION = 0.20

COSTO = "costo_planificado_soles"
DURACION = "duracion_dias"
COSTO_M2 = "costo_por_m2_soles"

# Variables de entrada para los modelos
PREDICTORES = [
    "area_m2", "pisos", "complejidad_estructural", "capacidad_contratista",
    "disponibilidad_recursos", "madurez_gestion", "exposicion_clima",
    "exposicion_suministro", "madurez_tecnologica",
]

NUMERICAS = PREDICTORES + [DURACION, COSTO, COSTO_M2, "indice_riesgo"]


def cargar(limpio=True, calculadas=True):
    df = pd.read_csv(RUTA).rename(columns=RENOMBRAR)
    df["tipo_proyecto"] = df["tipo_proyecto"].map(TIPOS)
    if limpio:
        df = df.dropna().drop_duplicates()
    if calculadas:
        # KPI técnico: costo unitario por metro cuadrado
        df[COSTO_M2] = np.round(df[COSTO] / df["area_m2"], 2)
        # Índice de riesgo (propuesta del grupo, pesos iguales, escala 0 a 1):
        # promedio de exposiciones y de las deficiencias (1 - capacidad/madurez/disponibilidad)
        df["indice_riesgo"] = np.round((
            df["exposicion_clima"] + df["exposicion_suministro"]
            + (1 - df["capacidad_contratista"]) + (1 - df["disponibilidad_recursos"])
            + (1 - df["madurez_gestion"]) + (1 - df["madurez_tecnologica"])
        ) / 6, 3)
        # Nivel de riesgo por terciles de la cartera: bajo / medio / alto
        df["nivel_riesgo"] = pd.qcut(df["indice_riesgo"], 3, labels=["Bajo", "Medio", "Alto"]).astype(str)
        # Costo por día de obra (S/ por día planificado)
        df["costo_por_dia_soles"] = np.round(df[COSTO] / df[DURACION], 2)
        # Desviación del costo por m² respecto al promedio de su mismo tipo de proyecto
        prom_tipo = df.groupby("tipo_proyecto")[COSTO_M2].transform("mean")
        df["desviacion_vs_tipo"] = np.round(df[COSTO_M2] / prom_tipo - 1, 3)
        df["critica_relativa"] = df["desviacion_vs_tipo"] > UMBRAL_DESVIACION
        # Costo con reserva de contingencia según el nivel de riesgo
        df["contingencia_soles"] = np.round(df[COSTO] * df["nivel_riesgo"].map(CONTINGENCIA), 2)
        df["costo_con_contingencia"] = df[COSTO] + df["contingencia_soles"]
    return df


def x_logaritmico(d):
    """Predictores con el área en escala logarítmica (el costo crece de forma multiplicativa con el área)."""
    x = d[PREDICTORES].copy()
    x["area_m2"] = np.log(x["area_m2"])
    return x


# Componentes del índice de riesgo, expresados como "riesgo" (1 = peor) para poder compararlos
def factores_riesgo(d):
    return pd.DataFrame({
        "Exposición climática": d["exposicion_clima"],
        "Exposición de suministro": d["exposicion_suministro"],
        "Baja capacidad del contratista": 1 - d["capacidad_contratista"],
        "Baja disponibilidad de recursos": 1 - d["disponibilidad_recursos"],
        "Baja madurez de gestión": 1 - d["madurez_gestion"],
        "Baja madurez tecnológica": 1 - d["madurez_tecnologica"],
    })
