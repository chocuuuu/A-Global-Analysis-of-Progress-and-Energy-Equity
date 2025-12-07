# filename: data_loader.py
import pandas as pd
import numpy as np
import os

def load_and_clean_data(filepath='data/global-data-on-sustainable-energy.csv'):
    """
    Loads the dataset, handles missing file generation, and standardizes column names.
    """
    if os.path.exists(filepath):
        print(f"Loading real dataset from {filepath}...")
        df = pd.read_csv(filepath)
        df.columns = df.columns.str.strip() # Remove whitespace
    else:
        print("Dataset not found. Generating synthetic data for demonstration...")
        df = _generate_synthetic_data()

    return _preprocess_data(df)

def _preprocess_data(df):
    """
    Performs feature engineering and renaming.
    """
    # 1. Fill missing Financial Flows
    if 'Financial flows to developing countries (US $)' in df.columns:
        df['Financial flows to developing countries (US $)'] = df['Financial flows to developing countries (US $)'].fillna(0)
    
    # 2. Rename columns for internal consistency
    rename_map = {
        'Access to electricity (% of population)': 'Access_Electricity',
        'Access to clean fuels for cooking': 'Access_Cooking',
        'Renewable-electricity-generating-capacity-per-capita': 'Renewable_Capacity',
        'Financial flows to developing countries (US $)': 'Financial_Flows',
        'gdp_per_capita': 'GDP_Capita',
        'Energy intensity level of primary energy (MJ/$2017 PPP GDP)': 'Energy_Intensity',
        'Value_co2_emissions_kt_by_country': 'CO2_Total_kt',
        'Entity': 'Country'
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    # 3. Calculate the Equity Gap (Infrastructure vs Health)
    if 'Access_Electricity' in df.columns and 'Access_Cooking' in df.columns:
        df['Cooking_Gap'] = df['Access_Electricity'] - df['Access_Cooking']
        
    return df

def _generate_synthetic_data():
    """Generates dummy data matching the specific schema if CSV is missing."""
    years = np.arange(2000, 2021)
    countries = ['Country A', 'Country B', 'Country C', 'Country D']
    data = []
    for country in countries:
        for year in years:
            gdp = 1000 + (year-2000)*200
            data.append({
                'Entity': country,
                'Year': year,
                'Access to electricity (% of population)': min(100, 50 + (year-2000)*2.5 + np.random.normal(0, 2)),
                'Access to clean fuels for cooking': min(100, 30 + (year-2000)*1.5 + np.random.normal(0, 2)),
                'Financial flows to developing countries (US $)': max(0, 1e6 + np.random.normal(0, 5e5)),
                'Renewable-electricity-generating-capacity-per-capita': 50 + (year-2000)*5,
                'gdp_per_capita': gdp,
                'Value_co2_emissions_kt_by_country': gdp * 0.5,
                'Energy intensity level of primary energy (MJ/$2017 PPP GDP)': max(2, 8 - (year-2000)*0.2)
            })
    return pd.DataFrame(data)