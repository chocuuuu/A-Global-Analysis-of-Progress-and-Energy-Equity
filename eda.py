# filename: eda.py
import pandas as pd
import numpy as np

def perform_eda(df):
    """
    Prints detailed statistical summaries to the terminal.
    Use these outputs for the 'Data Analysis' section of your paper.
    """
    print("\n" + "#"*60)
    print("   EXPLORATORY DATA ANALYSIS (EDA) & STATISTICS   ")
    print("#"*60)

    # 1. Data Structure
    print(f"\n[1] Dataset Overview")
    print(f"    - Total Records: {len(df)}")
    print(f"    - Unique Countries: {df['Country'].nunique()}")
    print(f"    - Years Covered: {df['Year'].min()} to {df['Year'].max()}")
    print(f"    - Missing Values (Top 5 Columns):\n{df.isnull().sum().sort_values(ascending=False).head(5)}")

    # 2. Research Question 1: Decoupling (GDP vs CO2)
    print(f"\n[2] RQ1: Economic Growth vs. Environmental Impact")
    if 'GDP_Capita' in df.columns and 'CO2_Total_kt' in df.columns:
        # Correlation
        corr_gdp_co2 = df[['GDP_Capita', 'CO2_Total_kt']].corr().iloc[0,1]
        print(f"    - Correlation (GDP per Capita vs. CO2 Total): {corr_gdp_co2:.4f}")
        
        # Intensity Change
        if 'Energy_Intensity' in df.columns:
            avg_int_2000 = df[df['Year'] == 2000]['Energy_Intensity'].mean()
            avg_2020 = df[df['Year'] == 2020]['Energy_Intensity'].mean()
            print(f"    - Global Avg Energy Intensity (2000): {avg_int_2000:.2f} MJ/$")
            print(f"    - Global Avg Energy Intensity (2020): {avg_2020:.2f} MJ/$")
            print(f"    - Improvement: {((avg_2020 - avg_int_2000)/avg_int_2000)*100:.1f}%")

    # 3. Research Question 2: Aid Effectiveness
    print(f"\n[3] RQ2: Financial Flows vs. Capacity")
    if 'Financial_Flows' in df.columns and 'Renewable_Capacity' in df.columns:
        total_aid = df['Financial_Flows'].sum()
        print(f"    - Total Financial Flows Recorded (2000-2020): ${total_aid/1e9:.2f} Billion")
        
        # Lagged Correlation check (Simplified)
        aid_receivers = df[df['Financial_Flows'] > 0]
        corr_aid_cap = aid_receivers['Financial_Flows'].corr(aid_receivers['Renewable_Capacity'])
        print(f"    - Correlation (Aid Received vs. Renewable Capacity): {corr_aid_cap:.4f}")
        print("      (Note: Low correlation implies aid may target access/grid rather than just generation capacity)")

    # 4. Outlier Detection / Top Performers
    print(f"\n[4] Top Performers (2020)")
    df_2020 = df[df['Year'] == 2020]
    
    print("    - Top 3 Countries by Renewable Share:")
    print(df_2020.nlargest(3, 'Renewable_Share')[['Country', 'Renewable_Share']].to_string(index=False))
    
    print("\n    - Top 3 Countries by Renewable Capacity Growth (Watts/capita):")
    # Simple growth proxy: Capacity in 2020
    print(df_2020.nlargest(3, 'Renewable_Capacity')[['Country', 'Renewable_Capacity']].to_string(index=False))

    print("\n" + "#"*60 + "\n")