# Tracking the Divide: A Global Analysis of Progress and Energy Equity (2000–2020)

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Last Updated](https://img.shields.io/badge/last_updated-2025--12--07-orange)

---

## Overview
This project analyzes the **Global Data on Sustainable Energy (2000-2020)** to evaluate progress toward **Sustainable Development Goal 7 (Affordable and Clean Energy)**.  

The focus is on the **Energy Equity Gap**—the disparity between infrastructure (electricity access) and quality of life (clean cooking)—and the effectiveness of financial flows.

---

## Methodology Highlights
- Equity Gap Analysis: Compares access to electricity vs. access to clean fuels for cooking
- Aid Effectiveness: Correlates financial flows to developing countries with changes in renewable capacity
- Decoupling: Analyzes the relationship between GDP per capita and energy intensity
  
---

## Repository Contents

| File | Description |
|------|-------------|
| **`main.py`** | Main Python script for data processing, statistical analysis, and static visualization generation |
| **`data_loader.py`** |  Handles CSV loading, whitespace cleaning, null imputation, and feature engineering |
| **`eda.py`** | Performs statistical analysis, missing value assessment, and correlation checks. |
| **`visualizer.py`** | Generates static figures. |
| **`interactive_dashboard.py`** | Generates the HTML dashboard and outputs detailed chart statistics to the console. |
| **`figures/`** | Directory containing all generated outputs |

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
  
Place your dataset file global-data-on-sustainable-energy.csv in the `data/` directory.

Run the script:

```
python main.py
```

After running the script, check the console logs for granular data insights, including:
- Global renewable capacity distribution buckets.
- Specific "Equity Gap" trends for top impacted countries.
- Efficiency metrics for financial aid recipients (ROI analysis).
- Decoupling statistics (GDP vs CO2).

Figures 
1. **fig1_equity_gap_trends.png**: Electricity vs Clean Cooking access.
2. **fig2_aid_effectiveness_scatter.png**: Financial flows vs Capacity growth.
3. **fig3_efficiency_decoupling.png**: GDP vs Energy Intensity trends.
4. **fig4_correlation_heatmap.png**: Correlation matrix of all indicators.
5. **fig5_top_renewables_bar.png**: Top 20 nations by renewable capacity.
6. **interactive_dashboard.html**: Comprehensive dashboard with map, animations, and drill-downs.

</details> 

<details> 
<summary>3. Using the Dashboard</summary>

Simply double-click interactive_dashboard.html to open it in any modern web browser. No installation required. It contains embedded sample data for immediate interaction.

</details>
