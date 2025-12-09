# Financing the Future: Economic Drivers of the Green Transition (2000–2019)

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Last Updated](https://img.shields.io/badge/last_updated-2025--12--09-orange)

---

## Overview
This project analyzes the **Global Data on Sustainable Energy** to investigate the relationship between economic drivers—specifically **GDP growth** and **international financial aid**—and the transition to renewable energy.

Addressing **SDG 7 (Affordable and Clean Energy)** and **SDG 13 (Climate Action)**, the analysis answers three critical questions:
1.  **Decoupling:** Has economic growth separated from carbon emissions?
2.  **Aid Effectiveness:** Does international climate finance actually drive renewable capacity?
3.  **The Green Divide:** How does renewable adoption differ between rich and poor nations?

---

## Methodology Highlights
- **Relative Decoupling Analysis:** Comparing global GDP growth (+119.6%) vs. CO₂ emissions growth (+48.1%).
- **Aid ROI metrics:** Correlating cumulative financial flows with physical capacity added (Watts/capita).
- **Inequality Assessment:** Analyzing renewable energy shares across World Bank income quartiles.
- **Predictive Forecasting:** Linear regression models projecting the trajectory of top performing nations to 2030.

---

## Repository Contents

| File | Description |
|------|-------------|
| **`main.py`** | Main pipeline controller. Runs data loading, EDA, static visualization, and dashboard generation in sequence. |
| **`data_loader.py`** | Handles CSV ingestion, imputation of missing aid data, and feature engineering (Green Ratio, Income Groups). |
| **`eda.py`** | Performs statistical analysis for the paper, including correlations, intensity changes, and stratification by income. |
| **`visualizer.py`** | Generates the 9 static figures used in the final report, complete with granular data logging. |
| **`interactive_dashboard.py`** | Generates the HTML dashboard with interactive Plotly versions of all paper figures. |
| **`figures/`** | Directory containing all generated PNG plots and the HTML dashboard. |

---

## Instructions

<details>
<summary>1. Prerequisites</summary>

You need **Python 3.8+** and the following libraries:

```bash
pip install pandas numpy matplotlib seaborn plotly
```
</details>

<details> 
<summary>2. Running the Analysis</summary>

Place your dataset file global-data-on-sustainable-energy.csv in the data/ directory.

Run the main script:

```bash
python main.py
```

The script will execute in 4 Phases and log detailed statistics to the terminal for use in your report:

- **Phase 1**: Data Ingestion & Preprocessing.
- **Phase 2**: EDA (Decoupling stats, Aid correlations, Equity tables).
- **Phase 3**: Visualization Generation.
- **Phase 4**: Interactive Dashboard Assembly.

</details>

<details> <summary>3. Generated Outputs</summary>

After running the script, the figures/ directory will contain:

Static Figures (for PDF Report):

1. **fig1_funding_transition.png**: Dual-axis chart comparing Financial Aid vs. Capacity.
2. **fig2_kuznets_curve.png**: Scatter plot testing the Environmental Kuznets Curve.
3. **fig3_energy_mix_evolution.png**: Stacked area chart of global generation (Fossil vs. Renewable).
4. **fig4_top_aid_recipients.png**: Top 10 countries receiving climate finance.
5. **fig5_global_divergence.png**: Indexed trends of GDP vs. CO2 (The Decoupling Check).
6. **fig6_correlation_matrix.png**: Heatmap of key economic and energy drivers.
7. **fig7_top_movers.png**: Top 10 nations by renewable share growth.
8. **fig8_income_disparity.png**: Boxplot showing the "Green Divide" by income group.
9. **fig9_predictive_forecast.png**: 2030 Trajectory forecast for top performers.

Interactive Dashboard:

- **interactive_dashboard.html**: A standalone HTML file containing interactive versions of all 9 figures above. Double-click to open in any browser.

</details>