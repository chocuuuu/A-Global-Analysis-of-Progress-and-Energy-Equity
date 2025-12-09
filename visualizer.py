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
    
    _plot_funding_transition(df)
    _plot_kuznets_curve(df)
    _plot_energy_mix_evolution(df)
    _plot_top_aid_recipients(df)
    
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
    sns.barplot(x=total_aid.values, y=total_aid.index, palette='Blues_r')
    plt.title('Top 10 Recipients of Green Energy Financial Aid (2000-2020)', fontweight='bold')
    plt.xlabel('Total USD Received')
    plt.tight_layout()
    plt.savefig('figures/fig4_top_aid_recipients.png')
    plt.close()