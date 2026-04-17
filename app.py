"""
=============================================================================
Observatorio del Monitor Laboral - Advice
Dashboard interactivo de la demanda laboral en Uruguay (2024-2025)

Fuente: Monitor Laboral de Advice (Informes Anuales 2024 y 2025)
=============================================================================

Cómo correr:
    pip install streamlit pandas plotly
    streamlit run app.py

Estructura de archivos necesarios en el mismo directorio:
    app.py
    dataset.csv
    kpis_anuales.csv
    calificacion.csv
=============================================================================
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# ─────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Observatorio del Monitor Laboral - Advice",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# PALETA DE COLORES (basada en identidad Advice)
# ─────────────────────────────────────────────
COLOR_PRIMARY   = "#C8102E"   # Rojo Advice
COLOR_DARK      = "#1A1A1A"
COLOR_LIGHT     = "#F5F5F5"
COLOR_ACCENT    = "#E8E8E8"
COLOR_GREY      = "#6B6B6B"

SECTOR_COLORS = {
    "Ventas / Gestión Comercial y Marketing": "#C8102E",
    "Tecnologías de la Información":          "#E63946",
    "Administración / Contabilidad y Finanzas": "#457B9D",
    "Industria / Construcción y Oficios":     "#F4A261",
    "Logística y Transporte":                 "#2A9D8F",
    "Turismo / Hotelería y Gastronomía":      "#E9C46A",
    "Otras Actividades":                      "#A8DADC",
}

# ─────────────────────────────────────────────
# ESTILOS CSS PERSONALIZADOS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Fondo principal */
    .stApp { background-color: #FAFAFA; }

    /* Header personalizado */
    .main-header {
        background: linear-gradient(135deg, #C8102E 0%, #8B0000 100%);
        padding: 2rem 2.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: white;
    }
    .main-header h1 { color: white; font-size: 2rem; font-weight: 700; margin: 0; }
    .main-header p  { color: rgba(255,255,255,0.85); font-size: 1rem; margin: 0.4rem 0 0 0; }

    /* KPI Cards */
    .kpi-card {
        background: white;
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
        border-left: 4px solid #C8102E;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        margin-bottom: 0.5rem;
    }
    .kpi-label  { font-size: 0.78rem; color: #6B6B6B; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
    .kpi-value  { font-size: 2rem; font-weight: 800; color: #1A1A1A; line-height: 1.1; }
    .kpi-delta  { font-size: 0.85rem; margin-top: 0.2rem; }
    .kpi-up     { color: #2ECC71; }
    .kpi-down   { color: #E74C3C; }

    /* Insight box */
    .insight-box {
        background: linear-gradient(135deg, #fff5f5 0%, #fff 100%);
        border: 1px solid #FFCDD2;
        border-left: 4px solid #C8102E;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin: 0.5rem 0;
        font-size: 0.92rem;
        color: #333;
    }
    .insight-icon { font-size: 1.1rem; margin-right: 0.4rem; }

    /* Section headers */
    .section-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1A1A1A;
        border-bottom: 2px solid #C8102E;
        padding-bottom: 0.3rem;
        margin: 1.2rem 0 0.8rem 0;
    }

    /* Sidebar */
    .css-1d391kg { background-color: #1A1A1A; }

    /* Footer */
    .footer {
        text-align: center;
        color: #999;
        font-size: 0.78rem;
        padding: 2rem 0 1rem 0;
        border-top: 1px solid #eee;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# CARGA DE DATOS
# ─────────────────────────────────────────────
@st.cache_data
def cargar_datos():
    """Carga y preprocesa todos los datasets."""
    base = os.path.dirname(os.path.abspath(__file__))

    df = pd.read_csv(os.path.join(base, "dataset.csv"))
    df["fecha"]  = pd.to_datetime(df["fecha"])
    df["anio"]   = df["anio"].astype(int)
    df["porcentaje"] = pd.to_numeric(df["porcentaje"], errors="coerce")
    df["cantidad"]   = pd.to_numeric(df["cantidad"],   errors="coerce")

    kpis = pd.read_csv(os.path.join(base, "kpis_anuales.csv"))
    kpis["anio"] = kpis["anio"].astype(int)
    kpis["total_avisos"]      = pd.to_numeric(kpis["total_avisos"],      errors="coerce")
    kpis["variacion_pct"]     = pd.to_numeric(kpis["variacion_pct"],     errors="coerce")
    kpis["top1_sector_pct"]   = pd.to_numeric(kpis["top1_sector_pct"],   errors="coerce")
    kpis["top2_sector_pct"]   = pd.to_numeric(kpis["top2_sector_pct"],   errors="coerce")
    kpis["top3_sector_pct"]   = pd.to_numeric(kpis["top3_sector_pct"],   errors="coerce")

    cal = pd.read_csv(os.path.join(base, "calificacion.csv"))
    cal["anio"] = cal["anio"].astype(int)

    return df, kpis, cal


df_raw, df_kpis, df_cal = cargar_datos()


# ─────────────────────────────────────────────
# SIDEBAR – FILTROS
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔍 Filtros")
    st.markdown("---")

    # Año
    anios_disponibles = sorted(df_raw["anio"].unique())
    anio_sel = st.multiselect(
        "Año",
        options=anios_disponibles,
        default=anios_disponibles,
        help="Seleccioná uno o más años."
    )

    # Sector
    sectores_disponibles = sorted(df_raw["sector"].unique())
    sector_sel = st.multiselect(
        "Sector",
        options=sectores_disponibles,
        default=sectores_disponibles,
        help="Filtrá por sector de actividad."
    )

    # Seniority
    seniority_disponible = sorted(df_raw["seniority"].unique())
    seniority_sel = st.multiselect(
        "Seniority",
        options=seniority_disponible,
        default=seniority_disponible,
    )

    st.markdown("---")
    st.markdown("### 📌 Fuente")
    st.caption("Monitor Laboral de **Advice**  \nInformes Anuales 2024 y 2025  \n[advice.com.uy](https://www.advice.com.uy)")

    st.markdown("---")
    st.caption("⚠️ Los porcentajes de cargos individuales son estimaciones proporcionales basadas en el volumen total declarado por sector. Datos donde el informe no especifica cantidad exacta por cargo aparecen como null en el dataset.")


# ─────────────────────────────────────────────
# APLICAR FILTROS
# ─────────────────────────────────────────────
if not anio_sel:
    anio_sel = anios_disponibles
if not sector_sel:
    sector_sel = sectores_disponibles
if not seniority_sel:
    seniority_sel = seniority_disponible

df = df_raw[
    df_raw["anio"].isin(anio_sel) &
    df_raw["sector"].isin(sector_sel) &
    df_raw["seniority"].isin(seniority_sel)
].copy()

df_kpis_fil = df_kpis[df_kpis["anio"].isin(anio_sel)]
df_cal_fil  = df_cal[df_cal["anio"].isin(anio_sel)]


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <h1>📊 Observatorio del Monitor Laboral – Advice</h1>
  <p>Análisis de la demanda laboral en Uruguay · Informes Anuales 2024 y 2025</p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# KPIs PRINCIPALES
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">📈 Indicadores Clave</div>', unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)

# Calcular KPIs de los años seleccionados
ultimo_anio  = df_kpis_fil["anio"].max() if not df_kpis_fil.empty else None
primer_anio  = df_kpis_fil["anio"].min() if not df_kpis_fil.empty else None

if ultimo_anio:
    row_ult = df_kpis_fil[df_kpis_fil["anio"] == ultimo_anio].iloc[0]
    total_avisos  = int(row_ult["total_avisos"])
    variacion     = row_ult["variacion_pct"]
    top1          = row_ult["top1_cargo"]
    anio_label    = str(ultimo_anio)
else:
    total_avisos, variacion, top1, anio_label = 0, None, "—", "—"

# Total cargos únicos en el filtro
total_cargos = df["cargo"].nunique()
total_sectores = df["sector"].nunique()

# Sector más demandado según el filtro
sector_top = (
    df.groupby("sector")["porcentaje"].sum().idxmax()
    if not df.empty else "—"
)

delta_color = "kpi-up" if variacion and variacion > 0 else "kpi-down"
delta_icon  = "▲" if variacion and variacion > 0 else "▼"

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Total Avisos ({anio_label})</div>
        <div class="kpi-value">{total_avisos:,}</div>
        <div class="kpi-delta {delta_color}">{delta_icon} {variacion:.1f}% vs año anterior</div>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Cargos Únicos Relevados</div>
        <div class="kpi-value">{total_cargos}</div>
        <div class="kpi-delta" style="color:#6B6B6B;">En los sectores seleccionados</div>
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Sectores Analizados</div>
        <div class="kpi-value">{total_sectores}</div>
        <div class="kpi-delta" style="color:#6B6B6B;">Grupos de actividad</div>
    </div>""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Sector Líder</div>
        <div class="kpi-value" style="font-size:1.1rem;">{sector_top.split('/')[0].strip()}</div>
        <div class="kpi-delta" style="color:#6B6B6B;">Mayor demanda acumulada</div>
    </div>""", unsafe_allow_html=True)

with col5:
    record_icon = "🏆" if 2025 in anio_sel else "📊"
    record_txt  = "Récord histórico 2025" if 2025 in anio_sel else "Datos seleccionados"
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Cargo #1 ({anio_label})</div>
        <div class="kpi-value" style="font-size:1.1rem;">{top1}</div>
        <div class="kpi-delta" style="color:#6B6B6B;">{record_icon} {record_txt}</div>
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# INSIGHTS AUTOMÁTICOS
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">💡 Insights Automáticos</div>', unsafe_allow_html=True)

insights = []

# Insight 1: variación anual
if 2024 in anio_sel and 2025 in anio_sel:
    insights.append("📈 La demanda laboral <b>creció un 15,1% en 2025</b> vs 12,8% en 2024, alcanzando las <b>85.468 vacantes</b> — un récord histórico en la serie del Monitor Laboral.")

# Insight 2: TI revirtió caída
if "Tecnologías de la Información" in sector_sel and 2025 in anio_sel:
    insights.append("💻 El sector TI <b>revirtió dos años de caída</b>: creció un <b>39,5% en 2025</b> impulsado por IA (+174%) y Desarrollo de Software (+37%). Es el sector de mayor crecimiento del año.")

# Insight 3: IA
if 2025 in anio_sel:
    insights.append("🤖 La demanda de <b>Ingenieros de IA</b> creció un <b>243% en 2025</b> (16x el promedio), escalando 91 posiciones en el ranking. La IA generativa marca la agenda laboral 2026.")

# Insight 4: Admin estancada
if "Administración / Contabilidad y Finanzas" in sector_sel and 2025 in anio_sel:
    insights.append("📉 Administración, Contabilidad y Finanzas <b>cayó un 0,4% en 2025</b>. Los puestos de soporte administrativo bajan un 2,7%, vinculado a la automatización por IA generativa.")

# Insight 5: calificación
if 2025 in anio_sel:
    insights.append("🎓 En 2025, los empleos de <b>alta calificación crecieron un 29,2%</b> mientras los de baja calificación solo un 4,5% — una brecha de 25 puntos que refleja el impacto tecnológico.")

# Insight 6: e-commerce
if 2025 in anio_sel:
    insights.append("🛒 El auge del e-commerce llevó al cargo <b>'Picker (Armador de Pedidos)'</b> al Top 40 en 2025. Las compras online de uruguayos en el exterior crecieron un <b>108% en 2025</b>.")

cols_ins = st.columns(2)
for i, ins in enumerate(insights):
    with cols_ins[i % 2]:
        st.markdown(f'<div class="insight-box"><span class="insight-icon"></span>{ins}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# GRÁFICO 1: EVOLUCIÓN ANUAL DE LA DEMANDA
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">📉 Evolución de la Demanda Laboral (2019–2025)</div>', unsafe_allow_html=True)

fig_evol = go.Figure()

# Línea principal
fig_evol.add_trace(go.Scatter(
    x=df_kpis["anio"],
    y=df_kpis["total_avisos"],
    mode="lines+markers+text",
    line=dict(color=COLOR_PRIMARY, width=3),
    marker=dict(size=10, color=COLOR_PRIMARY, line=dict(color="white", width=2)),
    text=df_kpis["total_avisos"].apply(lambda x: f"{int(x):,}" if pd.notna(x) else ""),
    textposition="top center",
    textfont=dict(size=11, color=COLOR_DARK),
    name="Vacantes publicadas",
    hovertemplate="<b>%{x}</b><br>Vacantes: %{y:,.0f}<extra></extra>"
))

# Área sombreada debajo
fig_evol.add_trace(go.Scatter(
    x=df_kpis["anio"],
    y=df_kpis["total_avisos"],
    fill="tozeroy",
    fillcolor="rgba(200,16,46,0.08)",
    line=dict(color="rgba(0,0,0,0)"),
    showlegend=False,
    hoverinfo="skip"
))

# Anotación récord 2025
fig_evol.add_annotation(
    x=2025, y=85468,
    text="🏆 Récord histórico",
    showarrow=True,
    arrowhead=2,
    arrowcolor=COLOR_PRIMARY,
    ax=0, ay=-50,
    font=dict(color=COLOR_PRIMARY, size=12, family="Arial Black")
)

fig_evol.update_layout(
    height=380,
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(family="Arial", size=12),
    xaxis=dict(
        title="Año",
        showgrid=False,
        tickvals=list(df_kpis["anio"]),
        tickfont=dict(size=13, color=COLOR_DARK)
    ),
    yaxis=dict(
        title="Oportunidades de empleo",
        showgrid=True,
        gridcolor="#F0F0F0",
        tickformat=",",
    ),
    margin=dict(l=20, r=20, t=20, b=30),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
st.plotly_chart(fig_evol, use_container_width=True)


# ─────────────────────────────────────────────
# GRÁFICO 2 y 3: SECTORES Y CARGOS (lado a lado)
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">🏭 Distribución por Sector y Cargos Más Demandados</div>', unsafe_allow_html=True)

col_sec, col_car = st.columns([1, 1])

with col_sec:
    # Agrupar sectores por año y porcentaje
    df_sec = df.groupby(["anio", "sector"])["porcentaje"].sum().reset_index()
    df_sec_pivot = df_sec.pivot(index="sector", columns="anio", values="porcentaje").fillna(0)

    fig_sec = go.Figure()
    anios_plot = sorted(df_sec["anio"].unique())
    colores_anio = [COLOR_PRIMARY, "#457B9D"]

    for idx, ay in enumerate(anios_plot):
        col_ay = str(ay)
        vals = df_sec_pivot.get(ay, pd.Series(dtype=float))
        fig_sec.add_trace(go.Bar(
            name=str(ay),
            y=df_sec_pivot.index,
            x=df_sec_pivot.get(ay, 0),
            orientation="h",
            marker_color=colores_anio[idx % len(colores_anio)],
            opacity=0.85 + idx * 0.1,
            hovertemplate="<b>%{y}</b><br>%{x:.1f}%<extra>" + str(ay) + "</extra>"
        ))

    fig_sec.update_layout(
        title=dict(text="Participación por Sector (%)", font=dict(size=13)),
        height=400,
        paper_bgcolor="white",
        plot_bgcolor="white",
        barmode="group",
        xaxis=dict(title="% del total", showgrid=True, gridcolor="#F0F0F0"),
        yaxis=dict(showgrid=False, tickfont=dict(size=10)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=10, r=10, t=50, b=30)
    )
    st.plotly_chart(fig_sec, use_container_width=True)

with col_car:
    # Top 15 cargos por porcentaje total acumulado en el filtro
    df_cargos = df.groupby("cargo")["porcentaje"].sum().reset_index()
    df_cargos = df_cargos.sort_values("porcentaje", ascending=True).tail(15)

    # Color por sector
    cargo_sector = df.groupby("cargo")["sector"].first().reset_index()
    df_cargos = df_cargos.merge(cargo_sector, on="cargo", how="left")
    df_cargos["color"] = df_cargos["sector"].map(SECTOR_COLORS).fillna("#AAAAAA")

    fig_car = go.Figure(go.Bar(
        x=df_cargos["porcentaje"],
        y=df_cargos["cargo"],
        orientation="h",
        marker=dict(
            color=df_cargos["color"],
            line=dict(color="white", width=0.5)
        ),
        hovertemplate="<b>%{y}</b><br>Score demanda: %{x:.1f}<br><extra></extra>"
    ))

    fig_car.update_layout(
        title=dict(text="Top 15 Cargos Más Demandados", font=dict(size=13)),
        height=400,
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis=dict(title="Score de demanda acumulado", showgrid=True, gridcolor="#F0F0F0"),
        yaxis=dict(showgrid=False, tickfont=dict(size=10)),
        margin=dict(l=10, r=10, t=50, b=30)
    )
    st.plotly_chart(fig_car, use_container_width=True)


# ─────────────────────────────────────────────
# GRÁFICO 4: NIVEL DE CALIFICACIÓN
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">🎓 Distribución por Nivel de Calificación</div>', unsafe_allow_html=True)

col_cal1, col_cal2 = st.columns([1, 1])

with col_cal1:
    df_cal_f = df_cal_fil.copy()

    if not df_cal_f.empty:
        # Si hay dos años, barras agrupadas; si uno, torta
        if df_cal_f["anio"].nunique() > 1:
            fig_cal = px.bar(
                df_cal_f,
                x="calificacion",
                y="porcentaje",
                color="anio",
                barmode="group",
                color_discrete_map={2024: COLOR_PRIMARY, 2025: "#457B9D"},
                labels={"porcentaje": "% de vacantes", "calificacion": "Nivel", "anio": "Año"},
                title="Distribución por calificación (%)"
            )
            fig_cal.update_layout(
                height=350,
                paper_bgcolor="white",
                plot_bgcolor="white",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="#F0F0F0"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
                margin=dict(l=10, r=10, t=50, b=30)
            )
        else:
            ay = df_cal_f["anio"].iloc[0]
            fig_cal = px.pie(
                df_cal_f,
                names="calificacion",
                values="porcentaje",
                color_discrete_sequence=[COLOR_PRIMARY, "#457B9D", "#F4A261", "#2A9D8F"],
                title=f"Calificación {ay} (%)",
                hole=0.4
            )
            fig_cal.update_layout(
                height=350,
                paper_bgcolor="white",
                margin=dict(l=10, r=10, t=50, b=10)
            )
        st.plotly_chart(fig_cal, use_container_width=True)
    else:
        st.info("Sin datos de calificación para los filtros seleccionados.")

with col_cal2:
    # Variación de calificación vs año anterior
    if not df_cal_f.empty and "variacion_pct_vs_anio_anterior" in df_cal_f.columns:
        df_var = df_cal_f[df_cal_f["anio"] == df_cal_f["anio"].max()].copy()
        df_var = df_var.dropna(subset=["variacion_pct_vs_anio_anterior"])

        if not df_var.empty:
            df_var = df_var.sort_values("variacion_pct_vs_anio_anterior")
            colors_var = [COLOR_PRIMARY if v > 0 else "#6B6B6B" for v in df_var["variacion_pct_vs_anio_anterior"]]

            fig_var = go.Figure(go.Bar(
                x=df_var["variacion_pct_vs_anio_anterior"],
                y=df_var["calificacion"],
                orientation="h",
                marker_color=colors_var,
                hovertemplate="<b>%{y}</b><br>Variación: %{x:.1f}%<extra></extra>"
            ))
            fig_var.add_vline(x=0, line_dash="dash", line_color="#AAAAAA")
            fig_var.update_layout(
                title=dict(text=f"Variación vs año anterior (%) — {df_var['anio'].iloc[0]}", font=dict(size=13)),
                height=350,
                paper_bgcolor="white",
                plot_bgcolor="white",
                xaxis=dict(title="Variación %", showgrid=True, gridcolor="#F0F0F0"),
                yaxis=dict(showgrid=False),
                margin=dict(l=10, r=10, t=50, b=30)
            )
            st.plotly_chart(fig_var, use_container_width=True)
        else:
            st.info("Seleccioná el año 2025 para ver la variación vs año anterior.")
    else:
        st.info("Sin datos de variación de calificación disponibles.")


# ─────────────────────────────────────────────
# GRÁFICO 5: SENIORITY (stacked + tabla skills)
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">👔 Distribución por Seniority y Skills</div>', unsafe_allow_html=True)

col_sen, col_ski = st.columns([1, 1])

with col_sen:
    df_sen = df.groupby(["anio", "seniority"])["porcentaje"].sum().reset_index()

    if not df_sen.empty:
        SENIORITY_COLORS = {
            "No especificado":         "#AAAAAA",
            "Auxiliar / Junior":       "#E63946",
            "Analista / Semi Senior":  "#F4A261",
            "Técnico / Medio Oficial": "#E9C46A",
            "Senior / Profesional":    "#457B9D",
            "Ejecutivo / Senior":      "#1D3557",
            "Liderazgo / Manager":     "#2A9D8F",
        }
        fig_sen = px.bar(
            df_sen,
            x="anio",
            y="porcentaje",
            color="seniority",
            barmode="stack",
            color_discrete_map=SENIORITY_COLORS,
            labels={"porcentaje": "Score demanda", "seniority": "Seniority", "anio": "Año"},
            title="Composición por Seniority"
        )
        fig_sen.update_layout(
            height=380,
            paper_bgcolor="white",
            plot_bgcolor="white",
            xaxis=dict(showgrid=False, type="category"),
            yaxis=dict(showgrid=True, gridcolor="#F0F0F0"),
            legend=dict(orientation="v", x=1.01, y=0.5),
            margin=dict(l=10, r=10, t=50, b=30)
        )
        st.plotly_chart(fig_sen, use_container_width=True)
    else:
        st.info("Sin datos de seniority para los filtros seleccionados.")

with col_ski:
    # Top skills por suma de porcentaje
    df_ski = df.groupby("skill")["porcentaje"].sum().reset_index()
    df_ski = df_ski.sort_values("porcentaje", ascending=False).head(20)
    df_ski.columns = ["Skill / Área", "Score demanda"]
    df_ski["Score demanda"] = df_ski["Score demanda"].round(2)
    df_ski = df_ski.reset_index(drop=True)
    df_ski.index = df_ski.index + 1

    st.markdown("**🔧 Top 20 Skills / Áreas Más Demandadas**")
    st.dataframe(
        df_ski,
        use_container_width=True,
        height=360
    )


# ─────────────────────────────────────────────
# GRÁFICO 6: VARIACIÓN POR SECTOR (2024 vs 2025)
# ─────────────────────────────────────────────
if 2024 in anio_sel and 2025 in anio_sel:
    st.markdown('<div class="section-title">📊 Variación Interanual por Sector (2024 → 2025)</div>', unsafe_allow_html=True)

    # Datos reales del informe 2025
    variaciones_sector = pd.DataFrame({
        "Sector":      [
            "Tecnologías de la Información",
            "Turismo / Hotelería y Gastronomía",
            "Logística y Transporte",
            "Ventas / Gestión Comercial y Marketing",
            "Industria / Construcción y Oficios",
            "Administración / Contabilidad y Finanzas"
        ],
        "Variacion_2024": [
            -21.9, None, 23.6, 28.4, 16.0, 9.9
        ],
        "Variacion_2025": [
            39.5, 19.1, 14.4, 14.0, 7.6, -0.4
        ]
    })

    var_filt = variaciones_sector[
        variaciones_sector["Sector"].isin(sector_sel)
    ]

    fig_var2 = go.Figure()
    fig_var2.add_trace(go.Bar(
        name="2024",
        x=var_filt["Sector"],
        y=var_filt["Variacion_2024"],
        marker_color="#AAAAAA",
        hovertemplate="<b>%{x}</b><br>2024: %{y:.1f}%<extra></extra>"
    ))
    fig_var2.add_trace(go.Bar(
        name="2025",
        x=var_filt["Sector"],
        y=var_filt["Variacion_2025"],
        marker_color=COLOR_PRIMARY,
        hovertemplate="<b>%{x}</b><br>2025: %{y:.1f}%<extra></extra>"
    ))
    fig_var2.add_hline(
        y=0, line_dash="dash", line_color="#AAAAAA",
        annotation_text="0%", annotation_position="right"
    )
    fig_var2.add_hline(
        y=15.1, line_dash="dot", line_color=COLOR_PRIMARY,
        annotation_text="Promedio 2025: 15,1%", annotation_position="right",
        annotation_font_color=COLOR_PRIMARY
    )
    fig_var2.update_layout(
        height=380,
        barmode="group",
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis=dict(showgrid=False, tickangle=-20, tickfont=dict(size=10)),
        yaxis=dict(title="Variación %", showgrid=True, gridcolor="#F0F0F0"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(l=20, r=120, t=30, b=80)
    )
    st.plotly_chart(fig_var2, use_container_width=True)


# ─────────────────────────────────────────────
# TABLA DETALLADA
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">📋 Dataset Detallado</div>', unsafe_allow_html=True)

with st.expander("Ver / descargar datos completos", expanded=False):
    df_show = df[["anio", "sector", "cargo", "seniority", "skill", "porcentaje", "fuente"]].copy()
    df_show.columns = ["Año", "Sector", "Cargo", "Seniority", "Skill / Área", "% Demanda", "Fuente"]
    df_show = df_show.sort_values(["Año", "% Demanda"], ascending=[True, False]).reset_index(drop=True)

    st.dataframe(df_show, use_container_width=True, height=400)

    # Botón de descarga CSV
    csv_bytes = df_show.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Descargar dataset filtrado (CSV)",
        data=csv_bytes,
        file_name="monitor_laboral_filtrado.csv",
        mime="text/csv"
    )


# ─────────────────────────────────────────────
# NOTAS METODOLÓGICAS
# ─────────────────────────────────────────────
with st.expander("📌 Notas metodológicas y supuestos"):
    st.markdown("""
    **Fuente de datos:**
    - Monitor Laboral de **Advice** — Informes Anuales 2024 y 2025.
    - El Monitor Laboral se elabora desde 2008 con relevamiento sistemático de portales de empleo y medios digitales en Uruguay.

    **Supuestos del dataset:**
    1. Los **porcentajes de participación por sector** provienen directamente de los informes.
    2. Los **porcentajes estimados por cargo** se calcularon en proporción al volumen total declarado por sector, dado que el informe no publica participaciones exactas para cada cargo.
    3. El campo **`cantidad`** solo contiene valores donde el informe explicita el total absoluto del sector (no de cada cargo individualmente).
    4. El campo **`seniority`** se marcó como *"No especificado"* donde el informe no desagrega por ese nivel.
    5. Los datos de años 2019–2023 provienen de la tabla histórica del informe y no tienen desagregación por sector/cargo.

    **Normalización:**
    - Sectores unificados bajo nomenclatura estándar (ej: "IT" → "Tecnologías de la Información").
    - Cargos con múltiples denominaciones unificados (ej: "Desarrollador" / "Desarrollador de Software").
    - Seniority clasificado en 7 niveles consistentes entre ambos años.

    **Limitaciones:**
    - Los datos corresponden a **demanda publicada** (vacantes), no a empleo efectivo.
    - No incluye el mercado laboral informal.
    - Las variaciones de participación % entre sectores reflejan cambios en la composición de la demanda, no necesariamente caídas absolutas en todos los casos.
    """)


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("""
<div class="footer">
    📊 <b>Observatorio del Monitor Laboral</b> · Datos: Advice Uruguay (advice.com.uy)<br>
    Informes Anuales 2024 y 2025 · Dashboard generado con Streamlit + Plotly<br>
    ⚠️ Los datos son de uso referencial. Para información oficial, consultar los informes originales de Advice.
</div>
""", unsafe_allow_html=True)
