# Mundial 2026 — Predicciones Probabilísticas

Plataforma de predicción para la Copa Mundial de la FIFA 2026. Pronostica los 104 partidos del torneo utilizando el modelo estadístico Dixon-Coles y simulación Monte Carlo.

## Metodología

El motor de predicción combina dos enfoques establecidos:

**Modelo Dixon-Coles (1997)** — Regresión de Poisson bivariada que estima parámetros de fuerza ofensiva y defensiva para cada selección nacional. El modelo aplica un factor de corrección para mejorar la precisión en resultados frecuentes del fútbol (0-0, 1-0, 0-1, 1-1). Los partidos se ponderan temporalmente, dando mayor importancia a los resultados recientes.

**Simulación Monte Carlo** — Se ejecutan 10,000 simulaciones completas del torneo, cada una simulando la fase de grupos, dieciseisavos, octavos, cuartos de final, semifinales, tercer puesto y final. Los empates en fase eliminatoria se resuelven mediante tandas de penales.

## Datos

- **Fuente:** [martj42/international_results](https://github.com/martj42/international_results) — aproximadamente 50,000 partidos internacionales desde 1872 hasta 2026
- **Formato:** 48 selecciones, 12 grupos de 4, clasifican 1° y 2° más 8 mejores terceros a dieciseisavos de final
- **Grupos:** Sorteo oficial FIFA

## Panel de Predicciones

El panel interactivo incluye:

- Predicciones de fase de grupos con probabilidades de marcador para los 72 partidos
- Visualización de la fase eliminatoria con probabilidades de avance por ronda
- Ranking de probabilidad de campeón para las 48 selecciones
- Tabla completa de probabilidades por ronda

**[Ver predicciones](https://xwilberx.github.io/worldcup-2026/)**

## Estructura del Proyecto

```
worldcup-2026/
├── docs/index.html                # Panel de predicciones (GitHub Pages)
├── dashboard/app.py               # Panel interactivo Streamlit
├── src/
│   ├── data/loader.py             # Carga y preprocesamiento de datos
│   ├── models/
│   │   ├── elo.py                 # Sistema de rating Elo
│   │   ├── dixon_coles.py         # Modelo Dixon-Coles Poisson
│   │   └── evaluate.py            # Métricas de backtesting
│   └── simulation/
│       ├── tournament.py          # Estructura del torneo y fase de grupos
│       └── monte_carlo.py         # Simulador Monte Carlo
├── scripts/
│   ├── download_data.py           # Descarga del dataset
│   └── train_model.py             # Pipeline completo de entrenamiento
├── data/
│   ├── raw/                       # Datos crudos (descarga separada)
│   └── processed/                 # Modelo entrenado y resultados
└── pyproject.toml                 # Dependencias (gestionado con uv)
```

## Inicio Rápido

**Requisitos:** Python 3.10+ y [uv](https://docs.astral.sh/uv/)

```bash
git clone https://github.com/XwilberX/worldcup-2026.git
cd worldcup-2026

uv sync
uv run python scripts/download_data.py
uv run python scripts/train_model.py
uv run streamlit run dashboard/app.py
```

## Principales Predicciones

Basado en 10,000 simulaciones Monte Carlo (10 de junio de 2026):

| # | Selección | Campeón |
|---|-----------|---------|
| 1 | Argentina | 21.4% |
| 2 | Brasil | 17.8% |
| 3 | España | 9.3% |
| 4 | Colombia | 8.9% |
| 5 | Francia | 6.3% |
| 6 | Inglaterra | 4.5% |
| 7 | Uruguay | 4.4% |
| 8 | Portugal | 3.9% |
| 9 | Ecuador | 3.3% |
| 10 | Países Bajos | 2.5% |

## Limitaciones

Las predicciones son probabilísticas. El modelo no contempla lesiones de jugadores, suspensiones, cambios de director técnico ni condiciones climáticas. El rendimiento histórico no garantiza resultados futuros. Todas las predicciones deben interpretarse como estimaciones estadísticas, no como certezas.
