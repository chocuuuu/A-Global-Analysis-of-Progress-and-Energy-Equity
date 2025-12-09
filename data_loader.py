# filename: data_loader.py
import pandas as pd
import numpy as np
import os

def load_and_clean_data(filepath='data/global-data-on-sustainable-energy.csv'):
    """
    Loads dataset, standardizes columns, and performs feature engineering 
    with verbose logging for the paper's methodology section.
    """
    print("\n" + "="*50)
    print("   PHASE 1: DATA INGESTION & PREPROCESSING   ")
    print("="*50)
    
    if os.path.exists(filepath):
        print(f"-> Loading dataset from: {filepath}")
        df = pd.read_csv(filepath)
        df.columns = df.columns.str.strip() 
    else:
        print(f"-> Error: {filepath} not found.")
        return pd.DataFrame()

    return _preprocess_data(df)

def _preprocess_data(df):
    """
    Renames columns and creates derived variables with logging.
    """
    initial_rows = len(df)
    
    # 1. Rename for clarity
    rename_map = {
        'Entity': 'Country',
        'Year': 'Year',
        'Access to electricity (% of population)': 'Access_Electricity',
        'Access to clean fuels for cooking': 'Access_Cooking',
        'Renewable-electricity-generating-capacity-per-capita': 'Renewable_Capacity',
        'Financial flows to developing countries (US $)': 'Financial_Flows',
        'Renewable energy share in the total final energy consumption (%)': 'Renewable_Share',
        'Electricity from fossil fuels (TWh)': 'Elec_Fossil',
        'Electricity from nuclear (TWh)': 'Elec_Nuclear',
        'Electricity from renewables (TWh)': 'Elec_Renewables',
        'Low-carbon electricity (% electricity)': 'Elec_Low_Carbon_Pct',
        'Primary energy consumption per capita (kWh/person)': 'Energy_Per_Capita',
        'Energy intensity level of primary energy (MJ/$2017 PPP GDP)': 'Energy_Intensity',
        'Value_co2_emissions_kt_by_country': 'CO2_Total_kt',
        'gdp_per_capita': 'GDP_Capita',
        'gdp_growth': 'GDP_Growth'
    }
    
    print("-> Renaming columns to standard format...")
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    # 2. Handle Missing Values
    if 'Financial_Flows' in df.columns:
        missing_aid = df['Financial_Flows'].isnull().sum()
        print(f"-> Imputing 0 for {missing_aid} missing 'Financial_Flows' records (assuming no aid received).")
        df['Financial_Flows'] = df['Financial_Flows'].fillna(0)
    
    # 3. Feature Engineering
    print("-> generating derived features:")
    
    # A. Green Transition Ratio
    if 'Elec_Renewables' in df.columns and 'Elec_Fossil' in df.columns:
        df['Green_Ratio'] = df['Elec_Renewables'] / (df['Elec_Fossil'] + 0.001)
        print("   - Created 'Green_Ratio' (Renewable TWh / Fossil TWh)")

    # B. Income Groups (Crucial for Equity Analysis)
    if 'GDP_Capita' in df.columns:
        # Check if we have enough data to cut
        if df['GDP_Capita'].notna().sum() > 0:
            df['Income_Group'] = pd.qcut(df['GDP_Capita'], 4, labels=['Low', 'Lower-Mid', 'Upper-Mid', 'High'])
            print("   - Created 'Income_Group' quartiles based on GDP per Capita")
    
    print(f"-> Preprocessing Complete. Final Dataset Shape: {df.shape}")
    return df