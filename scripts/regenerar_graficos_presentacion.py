from pathlib import Path
import os

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(BASE_DIR / ".matplotlib"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DATA_DIR = BASE_DIR / "datos" / "limpios"
FIGURAS_DIR = BASE_DIR / "resultados" / "figuras"
PRESENTACION_GRAFICOS_DIR = BASE_DIR / "presentacion_latex" / "graficos"

FIGURAS_DIR.mkdir(parents=True, exist_ok=True)
PRESENTACION_GRAFICOS_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_DIR / "produccion_cobre_mensual_limpio_ancho.csv", parse_dates=["fecha"])
df_largo = pd.read_csv(DATA_DIR / "produccion_cobre_mensual_limpio_largo.csv", parse_dates=["fecha"])


def guardar_figura(fig, nombre):
    for carpeta in [FIGURAS_DIR, PRESENTACION_GRAFICOS_DIR]:
        fig.savefig(carpeta / nombre, dpi=150)


fig, ax = plt.subplots(figsize=(8, 5))
ax.hist(df["total_chile"], bins=20, color="#1f77b4", edgecolor="white")
ax.set_title("Distribución mensual de la producción total de cobre en Chile")
ax.set_xlabel("Miles de toneladas métricas de cobre fino")
ax.set_ylabel("Frecuencia")
fig.tight_layout()
guardar_figura(fig, "hist_total_chile.png")
plt.close(fig)

fig, ax = plt.subplots(figsize=(8, 5))
ax.hist(df_largo["produccion_miles_tm_cobre_fino"], bins=35, color="#2ca02c", edgecolor="white")
ax.set_title("Distribución de producción mensual por empresa/faena")
ax.set_xlabel("Miles de toneladas métricas de cobre fino")
ax.set_ylabel("Frecuencia")
fig.tight_layout()
guardar_figura(fig, "hist_empresas_faenas.png")
plt.close(fig)

corr_codelco = df[["total_codelco", "total_chile"]].corr().iloc[0, 1]
fig, ax = plt.subplots(figsize=(7, 5))
ax.scatter(df["total_codelco"], df["total_chile"], alpha=0.75, color="#9467bd")
ax.set_title(f"Total Codelco vs Total Chile (corr={corr_codelco:.2f})")
ax.set_xlabel("Total Codelco")
ax.set_ylabel("Total Chile")
fig.tight_layout()
guardar_figura(fig, "scatter_codelco_total_chile.png")
plt.close(fig)

corr_escondida = df[["escondida", "total_chile"]].corr().iloc[0, 1]
fig, ax = plt.subplots(figsize=(7, 5))
ax.scatter(df["escondida"], df["total_chile"], alpha=0.75, color="#d62728")
ax.set_title(f"Escondida vs Total Chile (corr={corr_escondida:.2f})")
ax.set_xlabel("Escondida")
ax.set_ylabel("Total Chile")
fig.tight_layout()
guardar_figura(fig, "scatter_escondida_total_chile.png")
plt.close(fig)

print("Gráficos regenerados con tildes.")
