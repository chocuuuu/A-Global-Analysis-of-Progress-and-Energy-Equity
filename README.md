# Tracking the Divide: A Global Analysis of Progress and Energy Equity (2000–2020)

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Last Updated](https://img.shields.io/badge/last_updated-2025--12--07-orange)

---

## Overview
This project analyzes the **Global Data on Sustainable Energy (2000-2020)** to evaluate progress toward **Sustainable Development Goal 7 (Affordable and Clean Energy)**.  

The focus is on the **Energy Equity Gap**—the disparity between infrastructure (electricity access) and quality of life (clean cooking)—and the effectiveness of financial flows.

---

## Repository Contents

| File | Description |
|------|-------------|
| `analysis.py` | Main Python script for data processing, statistical analysis, and static visualization generation |
| `dashboard.html` | Standalone, interactive web dashboard visualizing key metrics (Equity, Aid Effectiveness, Efficiency) |
| `report.tex` | Final research report in LaTeX (ACM format structure) |
| `slides.md` | Presentation slides outlining the project narrative |

---

## Instructions

<details>
<summary>1. Prerequisites</summary>

You need **Python 3.8+** and the following libraries:

```bash
pip install pandas numpy matplotlib seaborn scikit-learn
```
</details> 

<details> 
<summary>2. Running the Analysis</summary>
  
Place your dataset file global-data-on-sustainable-energy.csv in this directory.
Note: If the file is missing, the script will generate a small synthetic dataset for demonstration purposes.

Run the script:

```
python analysis.py
```

The script will output:

Statistical summaries to the console

PNG images of the charts (saved in the current directory)

</details> 

<details> 
<summary>3. Using the Dashboard</summary>

Simply double-click dashboard.html to open it in any modern web browser. No installation required. It contains embedded sample data for immediate interaction.

</details>

## Methodology Highlights
- Equity Gap Analysis: Compares access to electricity vs. access to clean fuels for cooking
- Aid Effectiveness: Correlates financial flows to developing countries with changes in renewable capacity
- Decoupling: Analyzes the relationship between GDP per capita and energy intensity
