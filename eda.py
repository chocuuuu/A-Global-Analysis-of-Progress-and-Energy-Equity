# filename: eda.py
import pandas as pd
import numpy as np

def perform_eda(df):
    """
    Prints detailed statistical summaries to the terminal.
    """
    print("\n" + "="*50)
    print("   PHASE 2: EXPLORATORY DATA ANALYSIS (EDA)   ")
    print("="*50)

    # 1. Dataset Integrity
    print(f"\n[1] Data Integrity Check")
    print(f"    - Unique Countries: {df['Country'].nunique()}")
    print(f"    - Years Covered: {df['Year'].min()} to {df['Year'].max()}")
    print(f"    - Top Missing Cols:\n{df.isnull().sum().sort_values(ascending=False).head(3)}")

    # 2. RQ1: Decoupling
    print(f"\n[2] RQ1: Economic Decoupling Analysis")
    if 'GDP_Capita' in df.columns and 'CO2_Total_kt' in df.columns:
        corr_gdp_co2 = df[['GDP_Capita', 'CO2_Total_kt']].corr().iloc[0,1]
        print(f"    - Pearson Correlation (Wealth vs. Emissions): {corr_gdp_co2:.4f}")
        
        if 'Energy_Intensity' in df.columns:
            avg_2000 = df[df['Year'] == 2000]['Energy_Intensity'].mean()
            avg_2020 = df[df['Year'] == 2020]['Energy_Intensity'].mean()
            pct_change = ((avg_2020 - avg_2000) / avg_2000) * 100
            print(f"    - Energy Intensity Change (2000->2020): {pct_change:+.2f}%")
            if pct_change > 0:
                print("      (!) ALERT: Global efficiency WORSENED (More MJ needed per $).")
            else:
                print("      (OK) Insight: Global efficiency IMPROVED.")

    # 3. RQ2: Aid Effectiveness
    print(f"\n[3] RQ2: Aid ROI Analysis")
    if 'Financial_Flows' in df.columns and 'Renewable_Capacity' in df.columns:
        total_aid = df['Financial_Flows'].sum()
        print(f"    - Total Aid Recorded: ${total_aid/1e9:.2f} Billion")
        
        # Correlation on Receivers only
        receivers = df[df['Financial_Flows'] > 0]
        corr_aid = receivers['Financial_Flows'].corr(receivers['Renewable_Capacity'])
        print(f"    - Correlation (Aid > 0 vs Capacity): {corr_aid:.4f}")

    # 4. RQ3: Equity
    print(f"\n[4] RQ3: The Green Divide (Income Groups)")
    if 'Income_Group' in df.columns and 'Renewable_Share' in df.columns:
        print("    - Average Renewable Share (%) by Income Group:")
        print(df.groupby('Income_Group', observed=True)['Renewable_Share'].mean().to_string())

    print("\n" + "="*50)