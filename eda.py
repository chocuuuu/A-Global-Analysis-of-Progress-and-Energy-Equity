# filename: eda.py
import pandas as pd

def perform_eda(df):
    """
    Prints statistical summaries and key insights.
    """
    print("\n" + "="*40)
    print("   EXPLORATORY DATA ANALYSIS (EDA)   ")
    print("="*40)

    # 1. Basic Info
    print(f"\nTotal Records: {len(df)}")
    print(f"Countries Included: {df['Country'].nunique()}")
    print(f"Year Range: {df['Year'].min()} - {df['Year'].max()}")

    # 2. Missing Values Analysis
    print("\n--- Missing Values Count ---")
    print(df.isnull().sum()[df.isnull().sum() > 0])

    # 3. Correlation Analysis (Aid Effectiveness)
    if 'Financial_Flows' in df.columns and 'Renewable_Capacity' in df.columns:
        print("\n--- Correlation Analysis ---")
        # Filter for rows where both exist
        valid_data = df[['Financial_Flows', 'Renewable_Capacity']].dropna()
        if not valid_data.empty:
            corr = valid_data.corr().iloc[0,1]
            print(f"Correlation (Financial Aid vs Renewable Capacity): {corr:.4f}")
            if corr < 0.3:
                print("-> Insight: Weak correlation suggests aid efficiency issues.")
            else:
                print("-> Insight: Strong positive correlation suggests aid is effective.")

    # 4. Gap Analysis
    if 'Cooking_Gap' in df.columns:
        avg_gap_2020 = df[df['Year'] == 2020]['Cooking_Gap'].mean()
        print(f"\n--- Equity Gap Analysis (2020) ---")
        print(f"Average Gap (Electricity - Cooking Access): {avg_gap_2020:.2f}%")
        print("-> Insight: A positive gap means electrification is outpacing clean cooking access.")

    print("\n" + "="*40 + "\n")