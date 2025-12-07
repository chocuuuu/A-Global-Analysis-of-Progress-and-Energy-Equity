import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set plot style
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)

def load_data(filepath):
    """Loads data or creates dummy data if file is missing."""
    if os.path.exists(filepath):
        print(f"Loading dataset from {filepath}...")
        return pd.read_csv(filepath)
    else:
        print("Dataset not found. Generating synthetic data for demonstration...")
        # Create a mock dataset mirroring the real structure
        years = np.arange(2000, 2021)
        countries = ['Country A', 'Country B', 'Country C', 'Country D']
        data = []
        for country in countries:
            for year in years:
                # Simulate trends: Electricity grows faster than cooking
                elec = min(100, 50 + (year-2000)*2.5 + np.random.normal(0, 2))
                cooking = min(100, 30 + (year-2000)*1.5 + np.random.normal(0, 2))
                gdp = 1000 + (year-2000)*200
                financial = max(0, 1000000 + np.random.normal(0, 500000))
                capacity = 50 + (year-2000)*5 if 'A' in country else 20
                
                data.append({
                    'Entity': country,
                    'Year': year,
                    'Access to electricity (% of population)': elec,
                    'Access to clean fuels for cooking (% of population)': cooking,
                    'Financial flows to developing countries (US $)': financial,
                    'Renewable-electricity-generating-capacity-per-capita': capacity,
                    'GDP per capita': gdp,
                    'Value_co2_emissions (metric tons per capita)': gdp/1000 * 0.5,
                    'Energy intensity level of primary energy (MJ/$2011 PPP GDP)': max(2, 8 - (year-2000)*0.2)
                })
        return pd.DataFrame(data)

def clean_and_feature_engineer(df):
    """Preprocesses data and adds new metrics."""
    # 1. Fill missing Financial Flows with 0 (assuming NaN means no aid received)
    if 'Financial flows to developing countries (US $)' in df.columns:
        df['Financial flows to developing countries (US $)'] = df['Financial flows to developing countries (US $)'].fillna(0)
    
    # 2. Create the "Equity Gap" (Infrastructure vs. Health)
    df['Cooking_Gap'] = df['Access to electricity (% of population)'] - df['Access to clean fuels for cooking (% of population)']
    
    # 3. Rename columns for easier access
    df = df.rename(columns={
        'Access to electricity (% of population)': 'Access_Electricity',
        'Access to clean fuels for cooking (% of population)': 'Access_Cooking',
        'Renewable-electricity-generating-capacity-per-capita': 'Renewable_Capacity',
        'Financial flows to developing countries (US $)': 'Financial_Flows',
        'GDP per capita': 'GDP_Capita',
        'Energy intensity level of primary energy (MJ/$2011 PPP GDP)': 'Energy_Intensity'
    })
    
    return df

def plot_equity_gap(df):
    """Visualizes the divergence between Electricity and Clean Cooking access."""
    plt.figure(figsize=(10, 6))
    
    # Group by year to get global averages
    global_trends = df.groupby('Year')[['Access_Electricity', 'Access_Cooking']].mean().reset_index()
    
    plt.plot(global_trends['Year'], global_trends['Access_Electricity'], 
             label='Electricity Access', color='#2ecc71', linewidth=3)
    plt.plot(global_trends['Year'], global_trends['Access_Cooking'], 
             label='Clean Cooking Access', color='#e74c3c', linewidth=3, linestyle='--')
    
    plt.fill_between(global_trends['Year'], 
                     global_trends['Access_Electricity'], 
                     global_trends['Access_Cooking'], 
                     color='gray', alpha=0.1, label='The Equity Gap')
    
    plt.title('The Hidden Divide: Electricity vs. Clean Cooking (Global Avg)', fontsize=14)
    plt.ylabel('Population Access (%)')
    plt.xlabel('Year')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig('equity_gap.png')
    plt.close()
    print("Generated 'equity_gap.png'")

def plot_aid_effectiveness(df):
    """Scatter plot of Financial Flows vs Capacity Growth."""
    plt.figure(figsize=(10, 6))
    
    # Aggregate by country
    country_stats = df.groupby('Entity').agg({
        'Financial_Flows': 'sum',
        'Renewable_Capacity': lambda x: x.iloc[-1] - x.iloc[0] if len(x) > 1 else 0,
        'GDP_Capita': 'mean'
    }).reset_index()
    
    # Filter for countries that actually received significant aid
    subset = country_stats[country_stats['Financial_Flows'] > 0]
    
    sns.scatterplot(data=subset, x='Financial_Flows', y='Renewable_Capacity', 
                    size='GDP_Capita', sizes=(20, 200), hue='GDP_Capita', palette='viridis', legend=False)
    
    plt.xscale('log')
    plt.title('Aid Effectiveness: Financial Flows vs. Renewable Capacity Growth', fontsize=14)
    plt.xlabel('Total Financial Flows Received (Log Scale US$)')
    plt.ylabel('Change in Renewable Capacity (W/capita)')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.savefig('aid_effectiveness.png')
    plt.close()
    print("Generated 'aid_effectiveness.png'")

def plot_efficiency_trend(df):
    """Visualizes the decoupling of GDP and Energy Intensity."""
    plt.figure(figsize=(10, 6))
    
    # Use 2000 as base year = 100 for normalization
    global_eco = df.groupby('Year')[['GDP_Capita', 'Energy_Intensity']].mean().reset_index()
    
    # Normalize
    global_eco['GDP_Index'] = (global_eco['GDP_Capita'] / global_eco['GDP_Capita'].iloc[0]) * 100
    global_eco['Intensity_Index'] = (global_eco['Energy_Intensity'] / global_eco['Energy_Intensity'].iloc[0]) * 100
    
    plt.plot(global_eco['Year'], global_eco['GDP_Index'], label='GDP Growth', color='#3498db', linewidth=3)
    plt.plot(global_eco['Year'], global_eco['Intensity_Index'], label='Energy Intensity', color='#f39c12', linewidth=3)
    
    plt.axhline(100, color='black', linewidth=1, linestyle='--')
    plt.title('Global Decoupling: Economic Growth vs. Energy Efficiency', fontsize=14)
    plt.ylabel('Index (2000 = 100)')
    plt.legend()
    plt.savefig('efficiency_decoupling.png')
    plt.close()
    print("Generated 'efficiency_decoupling.png'")

def main():
    # 1. Load
    filename = 'data/global-data-on-sustainable-energy.csv'
    df = load_data(filename)
    
    # 2. Process
    df = clean_and_feature_engineer(df)
    
    # 3. Analyze & Visualise
    print("\n--- Generating Visualizations ---")
    plot_equity_gap(df)
    plot_aid_effectiveness(df)
    plot_efficiency_trend(df)
    
    # 4. Summary Stats
    print("\n--- Key Insights ---")
    avg_gap = df.groupby('Year')['Cooking_Gap'].mean().iloc[-1]
    print(f"1. As of 2020, the average gap between Electricity and Cooking access is {avg_gap:.2f}%.")
    
    corr = df[['Financial_Flows', 'Renewable_Capacity']].corr().iloc[0,1]
    print(f"2. Correlation between Financial Aid and Renewable Capacity: {corr:.3f}")

if __name__ == "__main__":
    main()