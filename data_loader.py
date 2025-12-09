# filename: data_loader.py
import pandas as pd
import numpy as np
import os

def load_and_clean_data(filepath='data/global-data-on-sustainable-energy.csv'):
    """
    Loads the dataset and performs feature engineering for the 'Financing the Future' analysis.
    """
    if os.path.exists(filepath):
        print(f"Loading real dataset from {filepath}...")
        df = pd.read_csv(filepath)
        df.columns = df.columns.str.strip() # Remove whitespace
    else:
        print("Dataset not found. Please ensure the file is in the 'data/' folder.")
        return pd.DataFrame() # Return empty if no data

    return _preprocess_data(df)

def _preprocess_data(df):
    """
    Performs feature engineering specific to Economic Drivers & Green Transition.
    """
    # 1. Fill missing Financial Flows (Assumed 0 for non-developing nations)
    if 'Financial flows to developing countries (US $)' in df.columns:
        df['Financial flows to developing countries (US $)'] = df['Financial flows to developing countries (US $)'].fillna(0)
    
    # 2. Rename columns for easier access
    rename_map = {
        'Entity': 'Country',
        'Access to electricity (% of population)': 'Access_Electricity',
        'Renewable-electricity-generating-capacity-per-capita': 'Renewable_Capacity',
        'Financial flows to developing countries (US $)': 'Financial_Flows',
        'Renewable energy share in the total final energy consumption (%)': 'Renewable_Share',
        'Electricity from fossil fuels (TWh)': 'Elec_Fossil',
        'Electricity from renewables (TWh)': 'Elec_Renewables',
        'Value_co2_emissions_kt_by_country': 'CO2_Total_kt',
        'gdp_per_capita': 'GDP_Capita',
        'gdp_growth': 'GDP_Growth',
        'Energy intensity level of primary energy (MJ/$2017 PPP GDP)': 'Energy_Intensity'
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    # 3. Feature Engineering: Economic & Environmental Metrics
    
    # Carbon Intensity (Emissions per Dollar of GDP) -> Measure of Decoupling
    if 'CO2_Total_kt' in df.columns and 'GDP_Capita' in df.columns:
        # Note: CO2 is in kt (kilotons), GDP is per capita. 
        # For a rough intensity proxy without population, we can look at correlation.
        # But if we want true intensity, we ideally need Total GDP. 
        # Here we will simply prepare the raw columns for correlation analysis.
        pass 

    # Renewable vs Fossil Ratio (The "Transition" Metric)
    if 'Elec_Renewables' in df.columns and 'Elec_Fossil' in df.columns:
        # Avoid division by zero
        df['Green_Transition_Ratio'] = df['Elec_Renewables'] / df['Elec_Fossil'].replace(0, 0.01)

    return df