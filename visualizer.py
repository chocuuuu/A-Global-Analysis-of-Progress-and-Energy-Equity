# filename: visualizer.py
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import os

# Set global style for publication-quality plots
sns.set_theme(style="whitegrid", context="talk")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['axes.titleweight'] = 'bold'

def create_output_folder():
    if not os.path.exists('figures'):
        os.makedirs('figures')

def generate_visualizations(df):
    """
    Generates static figures, including a PREDICTIVE forecast.
    """
    create_output_folder()
    print("Generating static visualizations...")
    
    # --- Original & Paper Figures ---
    _plot_funding_transition(df)
    _plot_kuznets_curve(df)
    _plot_energy_mix_evolution(df)
    _plot_top_aid_recipients(df)
    _plot_global_divergence(df)
    _plot_correlation_matrix(df)
    _plot_top_movers(df)
    _plot_income_disparity(df)
    
    # --- NEW PREDICTIVE CHART ---
    _plot_forecast_transition(df)  # <--- New Function Call
    
    print("Static figures saved to /figures directory.")

# ... [KEEP ALL PREVIOUS FUNCTIONS: _plot_funding_transition, _plot_kuznets_curve, etc.] ...
# (For brevity, I am not repeating the unchanged functions here, 
#  but you should keep them exactly as they were in the previous file.)

def _plot_funding_transition(df):
    """Fig 1: Dual Axis - Financial Flows vs Renewable Capacity (Global)."""
    if 'Financial_Flows' not in df.columns: return
    annual = df.groupby('Year').agg({'Financial_Flows': 'sum', 'Renewable_Capacity': 'mean'}).reset_index()
    fig, ax1 = plt.subplots()
    color1 = '#85bb65'
    ax1.set_xlabel('Year'); ax1.set_ylabel('Total Financial Flows (USD)', color=color1)
    ax1.bar(annual['Year'], annual['Financial_Flows'], color=color1, alpha=0.6, label='Financial Flows')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax2 = ax1.twinx(); color2 = '#2c3e50'
    ax2.set_ylabel('Avg Renewable Capacity (W/capita)', color=color2)
    ax2.plot(annual['Year'], annual['Renewable_Capacity'], color=color2, linewidth=4, marker='o', label='Renewable Capacity')
    ax2.tick_params(axis='y', labelcolor=color2)
    plt.title('Fig 1: Funding the Future - Aid vs. Capacity (2000-2020)')
    plt.tight_layout(); plt.savefig('figures/fig1_funding_transition.png'); plt.close()

def _plot_kuznets_curve(df):
    if 'GDP_Capita' not in df.columns: return
    plt.figure()
    sns.scatterplot(data=df, x='GDP_Capita', y='CO2_Total_kt', hue='Year', palette='viridis', alpha=0.7, size='Year', sizes=(20, 100))
    plt.xscale('log'); plt.yscale('log')
    plt.title('Fig 2: The Decoupling Test (GDP vs. CO2 Emissions)'); plt.tight_layout()
    plt.savefig('figures/fig2_kuznets_curve.png'); plt.close()

def _plot_energy_mix_evolution(df):
    if 'Elec_Fossil' not in df.columns: return
    annual_mix = df.groupby('Year')[['Elec_Fossil', 'Elec_Renewables']].sum().reset_index()
    plt.figure()
    plt.stackplot(annual_mix['Year'], annual_mix['Elec_Fossil'], annual_mix['Elec_Renewables'], labels=['Fossil Fuels', 'Renewables'], colors=['#636e72', '#00b894'], alpha=0.8)
    plt.title('Fig 3: Global Electricity Generation Mix (TWh)'); plt.legend(loc='upper left'); plt.tight_layout()
    plt.savefig('figures/fig3_energy_mix_evolution.png'); plt.close()

def _plot_top_aid_recipients(df):
    if 'Financial_Flows' not in df.columns: return
    total_aid = df.groupby('Country')['Financial_Flows'].sum().sort_values(ascending=False).head(10)
    plt.figure(figsize=(12, 6))
    sns.barplot(x=total_aid.values, y=total_aid.index, hue=total_aid.index, palette='Blues_r', legend=False)
    plt.title('Fig 4: Top 10 Recipients of Green Energy Aid (2000-2020)'); plt.tight_layout()
    plt.savefig('figures/fig4_top_aid_recipients.png'); plt.close()

def _plot_global_divergence(df):
    if 'GDP_Capita' not in df.columns: return
    annual = df.groupby('Year').agg({'GDP_Capita': 'mean', 'CO2_Total_kt': 'sum'}).reset_index()
    annual['GDP_Idx'] = (annual['GDP_Capita'] / annual['GDP_Capita'].iloc[0]) * 100
    annual['CO2_Idx'] = (annual['CO2_Total_kt'] / annual['CO2_Total_kt'].iloc[0]) * 100
    plt.figure()
    plt.plot(annual['Year'], annual['GDP_Idx'], label='Global GDP per Capita', color='#2ecc71', linewidth=4)
    plt.plot(annual['Year'], annual['CO2_Idx'], label='Total CO2 Emissions', color='#e74c3c', linewidth=4, linestyle='--')
    plt.title('Fig 5: The Decoupling Challenge (Indexed 2000=100)'); plt.legend(); plt.tight_layout()
    plt.savefig('figures/fig5_global_divergence.png'); plt.close()

def _plot_correlation_matrix(df):
    cols = ['GDP_Capita', 'Financial_Flows', 'Renewable_Share', 'CO2_Total_kt', 'Energy_Intensity', 'Access_Electricity']
    cols = [c for c in cols if c in df.columns]
    if len(cols) > 1:
        corr = df[cols].corr()
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr, annot=True, fmt=".2f", cmap='RdBu', center=0, square=True)
        plt.title('Fig 6: Correlation Matrix of Key Drivers'); plt.tight_layout()
        plt.savefig('figures/fig6_correlation_matrix.png'); plt.close()

def _plot_top_movers(df):
    pivoted = df.pivot_table(index='Country', columns='Year', values='Renewable_Share')
    if 2000 in pivoted.columns and 2020 in pivoted.columns:
        pivoted['Growth'] = pivoted[2020] - pivoted[2000]
        top10 = pivoted.nlargest(10, 'Growth')
        plt.figure()
        sns.barplot(x=top10['Growth'], y=top10.index, hue=top10.index, palette='Greens_r', legend=False)
        plt.title('Fig 7: Top 10 Countries by Renewable Share Growth (2000-2020)'); plt.tight_layout()
        plt.savefig('figures/fig7_top_movers.png'); plt.close()

def _plot_income_disparity(df):
    if 'Income_Group' not in df.columns: return
    plt.figure()
    sns.boxplot(x='Income_Group', y='Renewable_Share', hue='Income_Group', data=df, palette='Set2', legend=False)
    plt.title('Fig 8: Renewable Energy Share by Income Level'); plt.tight_layout()
    plt.savefig('figures/fig8_income_disparity.png'); plt.close()

# ==========================================
# 3. NEW PREDICTIVE FORECAST CHART
# ==========================================

def _plot_forecast_transition(df):
    """
    Fig 9: Future Forecast (2020-2030).
    Predicts renewable adoption for the Top 5 fastest-growing nations.
    """
    if 'Renewable_Share' not in df.columns: return
    
    # 1. Identify Top 5 Movers (by Growth)
    pivoted = df.pivot_table(index='Country', columns='Year', values='Renewable_Share')
    if 2000 not in pivoted.columns or 2020 not in pivoted.columns: return

    pivoted['Growth'] = pivoted[2020] - pivoted[2000]
    top_movers = pivoted.nlargest(5, 'Growth').index.tolist()
    
    plt.figure(figsize=(14, 8))
    colors = sns.color_palette("bright", n_colors=5)
    
    # 2. Iterate and Predict
    for i, country in enumerate(top_movers):
        # Get historical data
        country_data = df[df['Country'] == country].sort_values('Year')
        X_hist = country_data['Year'].values
        y_hist = country_data['Renewable_Share'].values
        
        # Fit Linear Trend (Degree 1 Polynomial)
        # We only fit on non-NaN data
        valid_idx = np.isfinite(y_hist)
        if np.sum(valid_idx) < 5: continue # Skip if not enough data points
        
        z = np.polyfit(X_hist[valid_idx], y_hist[valid_idx], 1)
        p = np.poly1d(z)
        
        # Create Forecast Years (2020 to 2030)
        X_future = np.arange(2020, 2031)
        y_future = p(X_future)
        
        # Clip values to 100% max (cannot exceed 100%)
        y_future = np.clip(y_future, 0, 100)
        
        # Plot History (Solid Line)
        plt.plot(X_hist, y_hist, label=f"{country} (History)", color=colors[i], linewidth=2.5, alpha=0.6)
        
        # Plot Forecast (Dashed Line)
        plt.plot(X_future, y_future, linestyle='--', color=colors[i], linewidth=3)
        
        # Add a marker at 2030
        plt.scatter(2030, y_future[-1], color=colors[i], s=100, zorder=5)
        plt.text(2030.5, y_future[-1], f"{y_future[-1]:.0f}%", color=colors[i], fontweight='bold')

    # Add Reference Line (SDG Target - Ideal)
    plt.axvline(2030, color='gray', linestyle=':', alpha=0.5)
    plt.text(2028, 5, "SDG 2030 Target", color='gray')

    plt.title('Fig 9: Predictive Forecast - Trajectory to 2030 (Top 5 Movers)', fontweight='bold')
    plt.xlabel('Year')
    plt.ylabel('Renewable Energy Share (%)')
    plt.legend(title='Country Trends', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig('figures/fig9_predictive_forecast.png')
    plt.close()