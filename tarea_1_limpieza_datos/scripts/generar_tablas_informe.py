from pathlib import Path
from datetime import datetime
import re
import unicodedata

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_LIMPIA = BASE_DIR / "datos" / "limpios"
DATA_ORIGINAL = BASE_DIR / "datos" / "originales" / "produccion_cobre_mina_empresa_mensual.xlsx"
TABLAS = BASE_DIR / "documento_latex" / "tablas"
TABLAS.mkdir(parents=True, exist_ok=True)


def latex_escape(value):
    text = str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def fmt_decimal(value, digits=2):
    if pd.isna(value):
        return ""
    return f"{value:.{digits}f}".replace(".", ",")


def clean_name(nombre):
    texto = str(nombre).strip().lower()
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    texto = re.sub(r"[^a-z0-9]+", "_", texto)
    texto = re.sub(r"_+", "_", texto).strip("_")
    return texto


def write_tabular(path, headers, rows, alignment=None):
    if alignment is None:
        alignment = "l" * len(headers)
    lines = [
        rf"\begin{{tabular}}{{{alignment}}}",
        r"\toprule",
        " & ".join(latex_escape(h) for h in headers) + r" \\",
        r"\midrule",
    ]
    for row in rows:
        lines.append(" & ".join(latex_escape(x) for x in row) + r" \\")
    lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    path.write_text("\n".join(lines))


def write_longtable(path, headers, rows, alignment=None):
    if alignment is None:
        alignment = "p{0.23\\textwidth}p{0.16\\textwidth}p{0.52\\textwidth}"
    header_line = " & ".join(latex_escape(h) for h in headers) + r" \\"
    lines = [
        rf"\begin{{longtable}}{{{alignment}}}",
        r"\toprule",
        header_line,
        r"\midrule",
        r"\endfirsthead",
        r"\toprule",
        header_line,
        r"\midrule",
        r"\endhead",
    ]
    for row in rows:
        lines.append(" & ".join(latex_escape(x) for x in row) + r" \\")
    lines.extend([r"\bottomrule", r"\end{longtable}", ""])
    path.write_text("\n".join(lines))


df = pd.read_csv(DATA_LIMPIA / "produccion_cobre_mensual_limpio_ancho.csv", parse_dates=["fecha"])
df_largo = pd.read_csv(DATA_LIMPIA / "produccion_cobre_mensual_limpio_largo.csv", parse_dates=["fecha"])
resumen_empresas = pd.read_csv(DATA_LIMPIA / "resumen_produccion_por_empresa.csv")
df_raw = pd.read_excel(DATA_ORIGINAL, sheet_name=0, header=6)

raw = df_raw.dropna(how="all").copy()
raw = raw.rename(columns={col: clean_name(col) for col in raw.columns})
raw = raw.rename(columns={raw.columns[0]: "fecha"})
monthly_mask = raw["fecha"].apply(lambda x: isinstance(x, (pd.Timestamp, datetime)))
monthly = raw.loc[monthly_mask].copy()
monthly["fecha"] = pd.to_datetime(monthly["fecha"], errors="coerce")
for col in monthly.columns:
    if col != "fecha":
        monthly[col] = pd.to_numeric(monthly[col], errors="coerce")
monthly_valid = monthly[monthly["total_chile"].fillna(0) > 0].copy()

flujo_rows = [
    ["Archivo original leído desde Excel", len(df_raw), df_raw.shape[1], "Incluye títulos, filas anuales y nota de fuente."],
    ["Filas no vacías después de lectura", len(raw), raw.shape[1], "Se eliminan filas totalmente vacías."],
    ["Filas mensuales identificadas", len(monthly), monthly.shape[1], "Se conservan registros cuyo campo fecha es mensual."],
    ["Meses con producción nacional informada", len(monthly_valid), monthly_valid.shape[1], "Se filtra total_chile mayor que cero."],
    ["Dataset limpio en formato largo", len(df_largo), df_largo.shape[1], "Una fila por fecha y empresa/faena con producción positiva."],
]
write_tabular(TABLAS / "flujo_limpieza.tex", ["Etapa", "Filas", "Columnas", "Criterio"], flujo_rows, "lrrp{0.43\\textwidth}")

general_rows = [
    ["Fuente", "COCHILCO"],
    ["Archivo original", "Producción de Cobre Mina por Empresa Mensual"],
    ["Unidad", "Miles de toneladas métricas de cobre fino"],
    ["Período limpio", f"{df['fecha'].min().date()} a {df['fecha'].max().date()}"],
    ["Observaciones formato ancho", len(df)],
    ["Columnas formato ancho", df.shape[1]],
    ["Registros formato largo", len(df_largo)],
    ["Empresas/faenas con producción positiva", df_largo["empresa_faena"].nunique()],
    ["Valores faltantes en dataset limpio ancho", int(df.isna().sum().sum())],
    ["Duplicados exactos en dataset limpio ancho", int(df.duplicated().sum())],
]
write_tabular(TABLAS / "resumen_general.tex", ["Aspecto", "Valor"], general_rows, "lp{0.62\\textwidth}")

variables_interes = ["total_chile", "total_codelco", "escondida", "collahuasi", "los_pelambres", "el_teniente"]
desc = df[variables_interes].describe().T
desc_rows = []
for var, row in desc.iterrows():
    desc_rows.append([
        var,
        fmt_decimal(row["mean"]),
        fmt_decimal(row["std"]),
        fmt_decimal(row["min"]),
        fmt_decimal(row["50%"]),
        fmt_decimal(row["max"]),
    ])
write_tabular(TABLAS / "estadisticas_descriptivas.tex", ["Variable", "Media", "Desv. est.", "Mín.", "Mediana", "Máx."], desc_rows, "lrrrrr")

corr = df[variables_interes].corr()
corr_rows = []
for var in variables_interes:
    corr_rows.append([var] + [fmt_decimal(corr.loc[var, col]) for col in variables_interes])
write_tabular(TABLAS / "correlaciones.tex", ["Variable"] + variables_interes, corr_rows, "lrrrrrr")

numeric_cols = [col for col in df.columns if col != "fecha"]
cor_total = (
    df[numeric_cols]
    .corr()["total_chile"]
    .drop("total_chile")
    .sort_values(ascending=False)
)
cor_total_rows = []
for idx, value in cor_total.items():
    intensidad = "Alta" if abs(value) >= 0.70 else "Media" if abs(value) >= 0.40 else "Baja"
    sentido = "Positiva" if value > 0 else "Negativa" if value < 0 else "Nula"
    cor_total_rows.append([idx, fmt_decimal(value), sentido, intensidad])
write_longtable(
    TABLAS / "correlaciones_total_chile.tex",
    ["Variable", "Correlación con total_chile", "Sentido", "Intensidad"],
    cor_total_rows,
    "p{0.31\\textwidth}rrp{0.18\\textwidth}",
)

skew_kurt = pd.DataFrame({
    "asimetría": df[variables_interes].skew(),
    "curtosis": df[variables_interes].kurtosis(),
})
skew_rows = [[idx, fmt_decimal(row["asimetría"]), fmt_decimal(row["curtosis"])] for idx, row in skew_kurt.iterrows()]
write_tabular(TABLAS / "asimetria_curtosis.tex", ["Variable", "Asimetría", "Curtosis"], skew_rows, "lrr")

top_mean = (
    df_largo.groupby("empresa_faena")["produccion_miles_tm_cobre_fino"]
    .agg(["count", "mean", "sum", "min", "max"])
    .sort_values("mean", ascending=False)
    .head(10)
)
top_rows = []
for idx, row in top_mean.iterrows():
    top_rows.append([idx, int(row["count"]), fmt_decimal(row["mean"]), fmt_decimal(row["sum"]), fmt_decimal(row["min"]), fmt_decimal(row["max"])])
write_tabular(TABLAS / "top_faenas.tex", ["Empresa/faena", "Meses positivos", "Media positiva", "Total", "Mín.", "Máx."], top_rows, "lrrrrr")

q1 = df["total_chile"].quantile(0.25)
q3 = df["total_chile"].quantile(0.75)
iqr = q3 - q1
limite_inferior = q1 - 1.5 * iqr
limite_superior = q3 + 1.5 * iqr
outliers = df[(df["total_chile"] < limite_inferior) | (df["total_chile"] > limite_superior)][
    ["fecha", "total_chile", "total_codelco", "escondida"]
].copy()
outlier_rows = []
for _, row in outliers.iterrows():
    outlier_rows.append([row["fecha"].strftime("%Y-%m"), fmt_decimal(row["total_chile"]), fmt_decimal(row["total_codelco"]), fmt_decimal(row["escondida"])])
write_tabular(TABLAS / "outliers.tex", ["Mes", "Total Chile", "Total Codelco", "Escondida"], outlier_rows, "lrrr")

missing_raw = monthly.isna().sum().to_frame("faltantes")
missing_raw["pct"] = missing_raw["faltantes"] / len(monthly) * 100
missing_raw = missing_raw[missing_raw["faltantes"] > 0].sort_values("faltantes", ascending=False).head(12)
missing_rows = [[idx, int(row["faltantes"]), fmt_decimal(row["pct"])] for idx, row in missing_raw.iterrows()]
write_tabular(TABLAS / "faltantes_original_mensual.tex", ["Variable", "Faltantes", "\\%"], missing_rows, "lrr")

desc_map = {
    "fecha": "Mes de referencia de la observación.",
    "total_chile": "Producción total mensual de cobre de mina en Chile.",
    "total_codelco": "Producción mensual agregada de faenas Codelco incluidas en el archivo.",
    "otros": "Producción mensual agrupada en la categoría Otros.",
}
variable_rows = []
for col in df.columns:
    if col == "fecha":
        tipo = "Fecha"
        descripcion = desc_map[col]
    elif col.startswith("total_"):
        tipo = "Total agregado"
        descripcion = desc_map.get(col, f"Producción mensual agregada asociada a {col.replace('_', ' ')}.")
    else:
        tipo = "Empresa/faena"
        descripcion = desc_map.get(col, f"Producción mensual de cobre de mina reportada para {col.replace('_', ' ')}.")
    variable_rows.append([col, tipo, descripcion])
write_longtable(TABLAS / "diccionario_variables.tex", ["Variable limpia", "Tipo", "Descripción"], variable_rows)

print("Tablas LaTeX generadas.")
