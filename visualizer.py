# filename: visualizer.py
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import os

# Set global style
sns.set_theme(style="whitegrid", context="talk")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['savefig.dpi'] = 300

def create_output_folder():
    if not os.path.exists('figures'):
        os.makedirs('figures')

def generate_visualizations(df):
    """
    Generates static plots focusing on Economic Drivers and Green Transition.
    """
    create_output_folder()
    print("Generating static visualizations...")
    
    # Original Set
    _plot_funding_transition(df)
    _plot_kuznets_curve(df)
    _plot_energy_mix_evolution(df)
    _plot_top_aid_recipients(df)
    
    # Additional Figures for Paper
    _plot_global_divergence(df)
    _plot_correlation_matrix(df)
    _plot_top_movers(df)
    _plot_income_disparity(df)
    
    print("Static figures saved to /figures directory.")

def _plot_funding_transition(df):
    """Fig 1: Dual Axis - Financial Flows vs Renewable Capacity (Global)."""
    if 'Financial_Flows' not in df.columns: return

    # Aggregating globally by year
    annual = df.groupby('Year').agg({
        'Financial_Flows': 'sum',
        'Renewable_Capacity': 'mean'
    }).reset_index()

    fig, ax1 = plt.subplots()

    # Bar Chart for Money (Left Axis)
    color1 = '#85bb65' # Dollar Green
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Total Financial Flows (USD)', color=color1)
    ax1.bar(annual['Year'], annual['Financial_Flows'], color=color1, alpha=0.6, label='Financial Flows')
    ax1.tick_params(axis='y', labelcolor=color1)

    # Line Chart for Capacity (Right Axis)
    ax2 = ax1.twinx() 
    color2 = '#2c3e50' # Dark Blue
    ax2.set_ylabel('Avg Renewable Capacity (W/capita)', color=color2)
    ax2.plot(annual['Year'], annual['Renewable_Capacity'], color=color2, linewidth=4, marker='o', label='Renewable Capacity')
    ax2.tick_params(axis='y', labelcolor=color2)

    plt.title('Funding the Future: Does Money Drive Capacity? (2000-2020)', fontweight='bold')
    plt.tight_layout()
    plt.savefig('figures/fig1_funding_transition.png')
    plt.close()

def _plot_kuznets_curve(df):
    """Fig 2: GDP vs CO2 (Testing the Environmental Kuznets Curve)."""
    if 'GDP_Capita' not in df.columns: return

    plt.figure()
    # Log scale often helps visualize GDP/CO2 better
    sns.scatterplot(data=df, x='GDP_Capita', y='CO2_Total_kt', 
                    hue='Year', palette='viridis', alpha=0.7, size='Year', sizes=(20, 100))
    
    plt.xscale('log')
    plt.yscale('log')
    plt.title('The Decoupling Test: GDP vs. CO2 Emissions', fontweight='bold')
    plt.xlabel('GDP per Capita (Log Scale)')
    plt.ylabel('CO2 Emissions (kt) (Log Scale)')
    plt.tight_layout()
    plt.savefig('figures/fig2_kuznets_curve.png')
    plt.close()

def _plot_energy_mix_evolution(df):
    """Fig 3: Fossil vs Renewable TWh over time."""
    if 'Elec_Fossil' not in df.columns: return

    annual_mix = df.groupby('Year')[['Elec_Fossil', 'Elec_Renewables']].sum().reset_index()
    
    plt.figure()
    plt.stackplot(annual_mix['Year'], annual_mix['Elec_Fossil'], annual_mix['Elec_Renewables'],
                  labels=['Fossil Fuels', 'Renewables'], colors=['#636e72', '#00b894'], alpha=0.8)
    
    plt.title('Global Electricity Generation Mix (TWh)', fontweight='bold')
    plt.ylabel('Terawatt-hours (TWh)')
    plt.legend(loc='upper left')
    plt.tight_layout()
    plt.savefig('figures/fig3_energy_mix_evolution.png')
    plt.close()

def _plot_top_aid_recipients(df):
    """Fig 4: Top 10 Countries receiving Financial Flows."""
    if 'Financial_Flows' not in df.columns: return
    
    total_aid = df.groupby('Country')['Financial_Flows'].sum().sort_values(ascending=False).head(10)
    
    plt.figure(figsize=(12, 6))
    # FIX: Assigned 'y' to 'hue' and set legend=False to fix deprecation warning
    sns.barplot(x=total_aid.values, y=total_aid.index, hue=total_aid.index, palette='Blues_r', legend=False)
    plt.title('Top 10 Recipients of Green Energy Financial Aid (2000-2020)', fontweight='bold')
    plt.xlabel('Total USD Received')
    plt.tight_layout()
    plt.savefig('figures/fig4_top_aid_recipients.png')
    plt.close()

# --- Additional Figures for Paper ---

def _plot_global_divergence(df):
    """Fig 5: Global GDP vs Global CO2 (Normalized). Decoupling Check."""
    if 'GDP_Capita' not in df.columns: return
    
    annual = df.groupby('Year').agg({
        'GDP_Capita': 'mean', 
        'CO2_Total_kt': 'sum'
    }).reset_index()
    
    # Normalize to 2000 = 100
    annual['GDP_Idx'] = (annual['GDP_Capita'] / annual['GDP_Capita'].iloc[0]) * 100
    annual['CO2_Idx'] = (annual['CO2_Total_kt'] / annual['CO2_Total_kt'].iloc[0]) * 100
    
    plt.figure()
    plt.plot(annual['Year'], annual['GDP_Idx'], label='Global GDP per Capita', color='#2ecc71', linewidth=3)
    plt.plot(annual['Year'], annual['CO2_Idx'], label='Total CO2 Emissions', color='#e74c3c', linewidth=3, linestyle='--')
    
    plt.title('The Decoupling Challenge: Growth vs Emissions (Indexed)', fontweight='bold')
    plt.ylabel('Index (2000 = 100)')
    plt.legend()
    plt.tight_layout()
    plt.savefig('figures/fig5_global_divergence.png')
    plt.close()

def _plot_correlation_matrix(df):
    """Fig 6: Heatmap of Economic & Energy Indicators."""
    cols = ['GDP_Capita', 'Financial_Flows', 'Renewable_Share', 
            'CO2_Total_kt', 'Energy_Intensity', 'Access_Electricity']
    # Filter for columns that actually exist
    cols = [c for c in cols if c in df.columns]
    
    if len(cols) > 1:
        corr = df[cols].corr()
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr, annot=True, fmt=".2f", cmap='RdBu', center=0, square=True)
        plt.title('Correlation Matrix of Key Drivers', fontweight='bold')
        plt.tight_layout()
        plt.savefig('figures/fig6_correlation_matrix.png')
        plt.close()

def _plot_top_movers(df):
    """Fig 7: Top 10 Countries by INCREASE in Renewable Share."""
    # Calculate change: Value in 2020 - Value in 2000
    pivoted = df.pivot_table(index='Country', columns='Year', values='Renewable_Share')
    if 2000 in pivoted.columns and 2020 in pivoted.columns:
        pivoted['Growth'] = pivoted[2020] - pivoted[2000]
        top10 = pivoted.nlargest(10, 'Growth')
        
        plt.figure()
        # Fix warning: assign y to hue
        sns.barplot(x=top10['Growth'], y=top10.index, hue=top10.index, palette='Greens_r', legend=False)
        plt.title('Top 10 Countries by Renewable Share Growth (2000-2020)', fontweight='bold')
        plt.xlabel('Percentage Point Increase')
        plt.tight_layout()
        plt.savefig('figures/fig7_top_movers.png')
        plt.close()

def _plot_income_disparity(df):
    """Fig 8: Boxplot of Renewable Share by Income Group."""
    if 'Income_Group' not in df.columns: return
    
    plt.figure()
    # Fix warning: assign x to hue
    sns.boxplot(x='Income_Group', y='Renewable_Share', hue='Income_Group', data=df, palette='Set2', legend=False)
    plt.title('Renewable Energy Share by Income Level', fontweight='bold')
    plt.xlabel('Income Quartile (Based on GDP/capita)')
    plt.ylabel('Renewable Share (%)')
    plt.tight_layout()
    plt.savefig('figures/fig8_income_disparity.png')
    plt.close()