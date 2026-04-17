# 📊 Observatorio del Monitor Laboral – Advice
## Dashboard interactivo de la demanda laboral en Uruguay (2024–2025)

---

## 🚀 Instrucciones para correr

### 1. Requisitos previos
```bash
pip install streamlit pandas plotly
```

### 2. Ejecutar el dashboard
```bash
streamlit run app.py
```
El navegador se abre automáticamente en `http://localhost:8501`

### 3. Despliegue en la nube (Streamlit Community Cloud)
1. Subí todos los archivos a un repositorio de GitHub
2. Creá una cuenta en [share.streamlit.io](https://share.streamlit.io)
3. Conectá el repo y hacé deploy con un clic

**Estructura de archivos requerida:**
```
tu-repo/
├── app.py
├── dataset.csv
├── kpis_anuales.csv
├── calificacion.csv
├── dataset.json
└── requirements.txt   ← (ver abajo)
```

**requirements.txt:**
```
streamlit>=1.30.0
pandas>=2.0.0
plotly>=5.18.0
```

---

## 📁 Archivos del proyecto

| Archivo | Descripción |
|---|---|
| `app.py` | Dashboard Streamlit completo |
| `dataset.csv` | Dataset principal (116 registros, 11 columnas) |
| `kpis_anuales.csv` | KPIs macro por año 2019–2025 |
| `calificacion.csv` | Distribución por nivel de calificación |
| `dataset.json` | Dataset consolidado en formato JSON |
| `README.md` | Este archivo |

---

## 📊 Estructura del dataset.csv

| Columna | Tipo | Descripción |
|---|---|---|
| `fecha` | date | Fecha de referencia del dato (YYYY-01-01) |
| `anio` | int | Año del informe |
| `mes` | str | "Anual" |
| `sector` | str | Grupo de actividad económica |
| `cargo` | str | Nombre del puesto de trabajo |
| `seniority` | str | Nivel de seniority del cargo |
| `skill` | str | Skill o área principal del cargo |
| `ubicacion` | str | País (Uruguay) |
| `cantidad` | float | Vacantes totales del sector (null si no especificado por cargo) |
| `porcentaje` | float | Participación % en la demanda total |
| `fuente` | str | Informe de origen |

---

## 💡 KPIs del Dashboard

- **Total avisos por año** (2019–2025, serie histórica completa)
- **Variación % interanual** con indicadores de tendencia
- **Top sectores** por participación y crecimiento
- **Top 15 cargos** más demandados
- **Distribución por seniority** (stacked bars)
- **Top 20 skills** por demanda acumulada
- **Nivel de calificación** con variación interanual
- **Comparativa sectorial 2024 vs 2025**

---

## 🤖 Insights Automáticos incluidos

El dashboard genera 6 insights automáticos basados en los datos:
1. Crecimiento anual de la demanda
2. Recuperación del sector TI en 2025
3. Boom de especialistas en IA (+243%)
4. Impacto de automatización en Administración
5. Brecha de calificación alta vs baja
6. Boom del e-commerce (Picker en Top 40)

---

## 🔍 Filtros disponibles

- **Año**: 2024, 2025 (o ambos)
- **Sector**: 7 grupos de actividad
- **Seniority**: 7 niveles

---

## ⚠️ Notas metodológicas

1. Los datos provienen exclusivamente de los **Informes Anuales 2024 y 2025 del Monitor Laboral de Advice**.
2. Los porcentajes por cargo son **estimaciones proporcionales** dentro del total del sector (el informe publica rankings y porcentajes del sector, no de cada cargo individual).
3. El campo `cantidad` es null para la mayoría de cargos individuales (el informe solo publica el total del sector).
4. `seniority = "No especificado"` indica que el informe no desagrega explícitamente por ese nivel para ese cargo.
5. Los datos 2019–2023 son **históricos referenciales** sin desagregación por sector/cargo.

---

## 📞 Fuente

**Monitor Laboral – Advice**  
[www.advice.com.uy](https://www.advice.com.uy)  
Informes Anuales 2024 y 2025  
Editores: Federico Muttoni, Aiuba González, Diego Estellano, Mauricio Milano
