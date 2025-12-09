# filename: eda.py
import pandas as pd

def perform_eda(df):
    """
    Prints statistical summaries focused on Economic Drivers and Green Transition.
    """
    print("\n" + "="*50)
    print("   EXPLORATORY DATA ANALYSIS: FINANCING THE FUTURE   ")
    print("="*50)

    # 1. Overview
    print(f"\nTotal Records: {len(df)}")
    print(f"Countries: {df['Country'].nunique()}")
    print(f"Years: {df['Year'].min()} - {df['Year'].max()}")

    # 2. The Decoupling Question (GDP vs CO2)
    if 'GDP_Capita' in df.columns and 'CO2_Total_kt' in df.columns:
        print("\n--- [RQ1] The Decoupling Question ---")
        corr_eco = df[['GDP_Capita', 'CO2_Total_kt']].corr().iloc[0,1]
        print(f"Correlation (Wealth vs Emissions): {corr_eco:.4f}")
        if corr_eco > 0.5:
            print("-> Insight: Strong positive correlation. Economic growth is still tied to higher emissions.")
        else:
            print("-> Insight: Weak/Negative correlation. Signs of decoupling may be present.")

    # 3. The Aid Effectiveness Question
    if 'Financial_Flows' in df.columns and 'Renewable_Capacity' in df.columns:
        print("\n--- [RQ2] Aid Effectiveness Analysis ---")
        # Filter for countries that actually received aid
        receivers = df[df['Financial_Flows'] > 0]
        corr_aid = receivers[['Financial_Flows', 'Renewable_Capacity']].corr().iloc[0,1]
        
        print(f"Correlation (Financial Flows vs Renewable Capacity): {corr_aid:.4f}")
        print(f"Total Aid Recorded (2000-2020): ${df['Financial_Flows'].sum()/1e9:,.2f} Billion")

    # 4. The Transition Speed
    if 'Renewable_Share' in df.columns:
        print("\n--- [RQ3] Transition Speed ---")
        avg_2000 = df[df['Year'] == 2000]['Renewable_Share'].mean()
        avg_2020 = df[df['Year'] == 2020]['Renewable_Share'].mean()
        print(f"Global Avg Renewable Share (2000): {avg_2000:.2f}%")
        print(f"Global Avg Renewable Share (2020): {avg_2020:.2f}%")
        print(f"Net Change: {avg_2020 - avg_2000:+.2f}%")

    print("\n" + "="*50 + "\n")