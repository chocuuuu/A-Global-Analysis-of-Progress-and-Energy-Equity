# filename: data_loader.py
import pandas as pd
import numpy as np
import os

def load_and_clean_data(filepath='data/global-data-on-sustainable-energy.csv'):
    """
    Loads dataset, standardizes columns, and performs feature engineering 
    for the 'Financing the Future' analysis.
    """
    if os.path.exists(filepath):
        print(f"Loading dataset from {filepath}...")
        df = pd.read_csv(filepath)
        df.columns = df.columns.str.strip() 
    else:
        print(f"Error: {filepath} not found.")
        return pd.DataFrame()

    return _preprocess_data(df)

def _preprocess_data(df):
    """
    Renames columns and creates derived variables for analysis.
    """
    # 1. Rename for clarity
    rename_map = {
        'Entity': 'Country',
        'Year': 'Year',
        'Access to electricity (% of population)': 'Access_Electricity',
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
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    # 2. Handle Missing Values
    # Assume missing Financial Flows means $0 (Developed nations or no data)
    if 'Financial_Flows' in df.columns:
        df['Financial_Flows'] = df['Financial_Flows'].fillna(0)
    
    # 3. Feature Engineering for the Paper
    
    # A. Carbon Intensity: CO2 Emissions (kt) per Dollar of GDP
    # Note: To be precise we need Total GDP, so we approximate with correlation proxies 
    # or create a relative intensity index. Here we stick to raw cols for correlation.
    
    # B. Green Transition Ratio (Renewables vs Fossil)
    if 'Elec_Renewables' in df.columns and 'Elec_Fossil' in df.columns:
        # Add small epsilon to avoid division by zero
        df['Green_Ratio'] = df['Elec_Renewables'] / (df['Elec_Fossil'] + 0.001)

    # C. GDP Quartiles (for grouping countries by wealth)
    if 'GDP_Capita' in df.columns:
        df['Income_Group'] = pd.qcut(df['GDP_Capita'], 4, labels=['Low', 'Lower-Mid', 'Upper-Mid', 'High'])

    return df