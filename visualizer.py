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
plt.rcParams['axes.titleweight'] = 'bold'

def create_output_folder():
    if not os.path.exists('figures'):
        os.makedirs('figures')

def generate_visualizations(df):
    """
    Generates static figures with verifying console logs for each.
    """
    create_output_folder()
    print("\n" + "="*50)
    print("   PHASE 3: VISUALIZATION GENERATION   ")
    print("="*50)
    
    # Paper Figures
    _plot_funding_transition(df)
    _plot_kuznets_curve(df)
    _plot_energy_mix_evolution(df)
    _plot_top_aid_recipients(df)
    _plot_global_divergence(df)
    _plot_correlation_matrix(df)
    _plot_top_movers(df)
    _plot_income_disparity(df)
    
    # Predictive Figure
    _plot_forecast_transition(df)
    
    print("\n-> All figures saved to /figures directory.")

# --- PLOTTING FUNCTIONS WITH LOGGING ---

def _plot_funding_transition(df):
    print("\n[Fig 1] Funding Transition (Dual Axis)")
    if 'Financial_Flows' not in df.columns: return

    annual = df.groupby('Year').agg({'Financial_Flows': 'sum', 'Renewable_Capacity': 'mean'}).reset_index()
    
    # Log details
    max_aid_year = annual.loc[annual['Financial_Flows'].idxmax(), 'Year']
    max_aid_val = annual['Financial_Flows'].max() / 1e9
    print(f"   - Peak Financial Aid Year: {max_aid_year} (${max_aid_val:.2f} B)")
    print(f"   - Capacity 2000: {annual.iloc[0]['Renewable_Capacity']:.2f} W/cap")
    print(f"   - Capacity 2020: {annual.iloc[-1]['Renewable_Capacity']:.2f} W/cap")

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
    print("\n[Fig 2] Kuznets Curve (Scatter)")
    if 'GDP_Capita' not in df.columns: return
    
    print(f"   - Plotting {len(df)} data points.")
    print(f"   - X-Axis Range (GDP): ${df['GDP_Capita'].min():.0f} - ${df['GDP_Capita'].max():.0f}")

    plt.figure()
    sns.scatterplot(data=df, x='GDP_Capita', y='CO2_Total_kt', hue='Year', palette='viridis', alpha=0.7, size='Year', sizes=(20, 100))
    plt.xscale('log'); plt.yscale('log')
    plt.title('Fig 2: The Decoupling Test (GDP vs. CO2 Emissions)')
    plt.xlabel('GDP per Capita (Log Scale)'); plt.ylabel('CO2 Emissions (kt) (Log Scale)')
    plt.tight_layout(); plt.savefig('figures/fig2_kuznets_curve.png'); plt.close()

def _plot_energy_mix_evolution(df):
    print("\n[Fig 3] Energy Mix (Stacked Area)")
    if 'Elec_Fossil' not in df.columns: return

    annual_mix = df.groupby('Year')[['Elec_Fossil', 'Elec_Renewables']].sum().reset_index()
    
    # Log details
    ren_2000 = annual_mix.iloc[0]['Elec_Renewables']
    ren_2020 = annual_mix.iloc[-1]['Elec_Renewables']
    print(f"   - Global Renewable Generation 2000: {ren_2000:.0f} TWh")
    print(f"   - Global Renewable Generation 2020: {ren_2020:.0f} TWh")

    plt.figure()
    plt.stackplot(annual_mix['Year'], annual_mix['Elec_Fossil'], annual_mix['Elec_Renewables'], labels=['Fossil Fuels', 'Renewables'], colors=['#636e72', '#00b894'], alpha=0.8)
    plt.title('Fig 3: Global Electricity Generation Mix (TWh)'); plt.legend(loc='upper left')
    plt.ylabel('Terawatt-hours (TWh)')
    plt.tight_layout(); plt.savefig('figures/fig3_energy_mix_evolution.png'); plt.close()

def _plot_top_aid_recipients(df):
    print("\n[Fig 4] Top Aid Recipients")
    if 'Financial_Flows' not in df.columns: return
    
    total_aid = df.groupby('Country')['Financial_Flows'].sum().sort_values(ascending=False).head(10)
    print(f"   - #1 Recipient: {total_aid.index[0]} (${total_aid.values[0]/1e9:.2f} B)")

    plt.figure(figsize=(12, 6))
    sns.barplot(x=total_aid.values, y=total_aid.index, hue=total_aid.index, palette='Blues_r', legend=False)
    plt.title('Fig 4: Top 10 Recipients of Green Energy Aid (2000-2020)'); plt.xlabel('Total USD Received')
    plt.tight_layout(); plt.savefig('figures/fig4_top_aid_recipients.png'); plt.close()

def _plot_global_divergence(df):
    print("\n[Fig 5] Global Divergence (Indexed)")
    if 'GDP_Capita' not in df.columns: return
    
    annual = df.groupby('Year').agg({'GDP_Capita': 'mean', 'CO2_Total_kt': 'sum'}).reset_index()
    annual['GDP_Idx'] = (annual['GDP_Capita'] / annual['GDP_Capita'].iloc[0]) * 100
    annual['CO2_Idx'] = (annual['CO2_Total_kt'] / annual['CO2_Total_kt'].iloc[0]) * 100
    
    print(f"   - 2020 GDP Index: {annual.iloc[-1]['GDP_Idx']:.1f} (vs 100)")
    print(f"   - 2020 CO2 Index: {annual.iloc[-1]['CO2_Idx']:.1f} (vs 100)")

    plt.figure()
    plt.plot(annual['Year'], annual['GDP_Idx'], label='Global GDP per Capita', color='#2ecc71', linewidth=4)
    plt.plot(annual['Year'], annual['CO2_Idx'], label='Total CO2 Emissions', color='#e74c3c', linewidth=4, linestyle='--')
    plt.title('Fig 5: The Decoupling Challenge (Indexed 2000=100)'); plt.ylabel('Index Value')
    plt.legend(); plt.tight_layout(); plt.savefig('figures/fig5_global_divergence.png'); plt.close()

def _plot_correlation_matrix(df):
    print("\n[Fig 6] Correlation Matrix")
    cols = ['GDP_Capita', 'Financial_Flows', 'Renewable_Share', 'CO2_Total_kt', 'Energy_Intensity', 'Access_Electricity']
    cols = [c for c in cols if c in df.columns]
    
    if len(cols) > 1:
        plt.figure(figsize=(10, 8))
        sns.heatmap(df[cols].corr(), annot=True, fmt=".2f", cmap='RdBu', center=0, square=True)
        plt.title('Fig 6: Correlation Matrix of Key Drivers'); plt.tight_layout()
        plt.savefig('figures/fig6_correlation_matrix.png'); plt.close()

def _plot_top_movers(df):
    print("\n[Fig 7] Top Green Movers")
    pivoted = df.pivot_table(index='Country', columns='Year', values='Renewable_Share')
    if 2000 in pivoted.columns and 2020 in pivoted.columns:
        pivoted['Growth'] = pivoted[2020] - pivoted[2000]
        # Drop NaNs to avoid "Afghanistan" error
        top10 = pivoted.dropna(subset=['Growth']).nlargest(10, 'Growth')
        
        print(f"   - Fastest Mover: {top10.index[0]} (+{top10['Growth'].iloc[0]:.1f}%)")

        plt.figure()
        sns.barplot(x=top10['Growth'], y=top10.index, hue=top10.index, palette='Greens_r', legend=False)
        plt.title('Fig 7: Top 10 Countries by Renewable Share Growth (2000-2020)'); plt.xlabel('Percentage Point Increase')
        plt.tight_layout(); plt.savefig('figures/fig7_top_movers.png'); plt.close()

def _plot_income_disparity(df):
    print("\n[Fig 8] Income Disparity Boxplot")
    if 'Income_Group' not in df.columns: 
        print("   - Skipping: 'Income_Group' column missing.")
        return
    
    counts = df['Income_Group'].value_counts()
    print(f"   - Group Sizes: {counts.to_dict()}")
    
    plt.figure()
    sns.boxplot(x='Income_Group', y='Renewable_Share', hue='Income_Group', data=df, palette='Set2', legend=False)
    plt.title('Fig 8: Renewable Energy Share by Income Level'); plt.xlabel('Income Quartile (GDP/capita)')
    plt.ylabel('Renewable Share (%)'); plt.tight_layout(); plt.savefig('figures/fig8_income_disparity.png'); plt.close()

def _plot_forecast_transition(df):
    print("\n[Fig 9] Predictive Forecast (2030)")
    if 'Renewable_Share' not in df.columns: return
    
    pivoted = df.pivot_table(index='Country', columns='Year', values='Renewable_Share')
    if 2000 not in pivoted.columns or 2020 not in pivoted.columns: return

    pivoted['Growth'] = pivoted[2020] - pivoted[2000]
    top_movers = pivoted.dropna(subset=['Growth']).nlargest(5, 'Growth').index.tolist()
    
    print(f"   - Forecasting for Top 5: {top_movers}")
    
    plt.figure(figsize=(14, 8))
    colors = sns.color_palette("bright", n_colors=5)
    
    for i, country in enumerate(top_movers):
        country_data = df[df['Country'] == country].sort_values('Year')
        X_hist = country_data['Year'].values
        y_hist = country_data['Renewable_Share'].values
        
        valid_idx = np.isfinite(y_hist)
        if np.sum(valid_idx) < 5: continue
        
        z = np.polyfit(X_hist[valid_idx], y_hist[valid_idx], 1)
        p = np.poly1d(z)
        
        X_future = np.arange(2020, 2031)
        y_future = np.clip(p(X_future), 0, 100)
        
        # Log prediction
        print(f"     * {country}: 2020={y_hist[-1]:.1f}% -> 2030={y_future[-1]:.1f}%")
        
        plt.plot(X_hist, y_hist, label=f"{country} (History)", color=colors[i], linewidth=2.5, alpha=0.6)
        plt.plot(X_future, y_future, linestyle='--', color=colors[i], linewidth=3)
        plt.scatter(2030, y_future[-1], color=colors[i], s=100, zorder=5)
        plt.text(2030.5, y_future[-1], f"{y_future[-1]:.0f}%", color=colors[i], fontweight='bold')

    plt.axvline(2030, color='gray', linestyle=':', alpha=0.5)
    plt.text(2028, 5, "SDG 2030 Target", color='gray')

    plt.title('Fig 9: Predictive Forecast - Trajectory to 2030 (Top 5 Movers)', fontweight='bold')
    plt.xlabel('Year'); plt.ylabel('Renewable Energy Share (%)')
    plt.legend(title='Country Trends', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout(); plt.savefig('figures/fig9_predictive_forecast.png'); plt.close()