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

# GLOBAL SETTING: Use 2019 as the cutoff due to missing 2020 data
LAST_VALID_YEAR = 2019

def create_output_folder():
    if not os.path.exists('figures'):
        os.makedirs('figures')

def generate_visualizations(df):
    """
    Generates 8 static figures with DETAILED DATA LOGGING for the report.
    """
    create_output_folder()
    print("\n" + "="*60)
    print(f"   PHASE 3: VISUALIZATION & DATA EXTRACTION (2000-{LAST_VALID_YEAR})   ")
    print("="*60)
    
    # Filter dataset
    df_clean = df[df['Year'] <= LAST_VALID_YEAR].copy()
    
    # Generating EDA visualizations
    _plot_eda_summary(df)

    # Generate Figures with Logs
    _plot_funding_transition(df_clean)
    _plot_kuznets_curve(df_clean)
    _plot_energy_mix_evolution(df_clean)
    _plot_top_aid_recipients(df_clean)
    _plot_global_divergence(df_clean)
    _plot_correlation_matrix(df_clean)
    _plot_top_movers(df_clean)
    _plot_income_disparity(df_clean)
    _plot_forecast_transition(df_clean)
    
    print("\n-> All figures saved to /figures directory.")

# --- EDA VISUALIZATION FUNCTIONS ---

def _plot_eda_summary(df):
    """
    Generates 3 preliminary visualizations required for EDA:
    1. Histogram (Distribution)
    2. Boxplot (Outliers - Multiple Columns)
    3. Missing Data Summary
    """
    
    # 1. Histogram: Energy Intensity Distribution
    if 'Energy_Intensity' in df.columns:
        plt.figure(figsize=(10, 6))
        sns.histplot(df['Energy_Intensity'], kde=True, color='purple', bins=30)
        plt.title('EDA: Distribution of Energy Intensity (Skew Check)', fontweight='bold')
        plt.xlabel('Energy Intensity (MJ/$ GDP)')
        plt.ylabel('Frequency')
        plt.axvline(df['Energy_Intensity'].mean(), color='red', linestyle='--', label='Mean')
        plt.legend()
        plt.tight_layout()
        plt.savefig('figures/fig_eda_1_intensity_histogram.png')
        plt.close()

    # 2. Boxplot: Comparative Outliers (Multiple Indicators)
    # Select key numerical columns for comparison
    cols_to_plot = ['Access_Electricity', 'Access_Cooking', 'Renewable_Capacity', 'Energy_Intensity']
    available_cols = [c for c in cols_to_plot if c in df.columns]
    
    if available_cols:
        plt.figure(figsize=(14, 8))
        
        # Melt the dataframe to long format for Seaborn boxplot
        df_melted = df[available_cols].melt(var_name='Indicator', value_name='Value')
        
        # Create boxplot
        sns.boxplot(x='Indicator', y='Value', data=df_melted, palette='Set2')
        
        plt.title('EDA: Outlier Detection Across Key Indicators', fontweight='bold')
        plt.xlabel('Indicator')
        plt.ylabel('Value (Log Scale)')
        plt.yscale('log') # Log scale is essential because units vary wildly (0-100% vs 0-3000 Watts)
        plt.tight_layout()
        plt.savefig('figures/fig_eda_2_multi_boxplot.png')
        plt.close()

    # 3. Bar Chart: Missing Values Summary
    plt.figure(figsize=(12, 6))
    missing = df.isnull().sum()
    missing = missing[missing > 0].sort_values(ascending=False)
    if not missing.empty:
        sns.barplot(x=missing.values, y=missing.index, palette='Reds_r')
        plt.title('EDA: Missing Values Count by Indicator', fontweight='bold')
        plt.xlabel('Number of Missing Records')
        plt.tight_layout()
        plt.savefig('figures/fig_eda_3_missing_values.png')
        plt.close()

# --- PLOTTING FUNCTIONS WITH DETAILED LOGS ---

def _plot_funding_transition(df):
    print("\n[Fig 1] Funding Transition (Dual Axis)")
    if 'Financial_Flows' not in df.columns: return

    annual = df.groupby('Year').agg({'Financial_Flows': 'sum', 'Renewable_Capacity': 'mean'}).reset_index()
    
    # DATA EXTRACTION
    v2000 = annual.iloc[0]
    vEnd = annual.iloc[-1]
    peak = annual.loc[annual['Financial_Flows'].idxmax()]
    
    print(f"   - Aid Trend: 2000=${v2000['Financial_Flows']/1e9:.2f}B -> {LAST_VALID_YEAR}=${vEnd['Financial_Flows']/1e9:.2f}B")
    print(f"   - Peak Aid:  {int(peak['Year'])} (${peak['Financial_Flows']/1e9:.2f}B)")
    print(f"   - Capacity:  2000={v2000['Renewable_Capacity']:.2f} W/cap -> {LAST_VALID_YEAR}={vEnd['Renewable_Capacity']:.2f} W/cap")

    fig, ax1 = plt.subplots()
    color1 = '#85bb65'
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Total Financial Flows (USD)', color=color1)
    ax1.bar(annual['Year'], annual['Financial_Flows'], color=color1, alpha=0.6, label='Financial Flows')
    ax1.tick_params(axis='y', labelcolor=color1)
    
    ax2 = ax1.twinx()
    color2 = '#2c3e50'
    ax2.set_ylabel('Avg Renewable Capacity (W/capita)', color=color2)
    ax2.plot(annual['Year'], annual['Renewable_Capacity'], color=color2, linewidth=4, marker='o', label='Renewable Capacity')
    ax2.tick_params(axis='y', labelcolor=color2)
    
    plt.title(f'Fig 1: Funding the Future (2000-{LAST_VALID_YEAR})')
    plt.tight_layout(); plt.savefig('figures/fig1_funding_transition.png'); plt.close()

def _plot_kuznets_curve(df):
    print("\n[Fig 2] Kuznets Curve (Scatter)")
    if 'GDP_Capita' not in df.columns: return
    
    # DATA EXTRACTION
    rich_dirty = df[(df['GDP_Capita'] > 50000) & (df['CO2_Total_kt'] > 100000)]
    print(f"   - Data Points: {len(df)}")
    print(f"   - Correlation (Log-Log proxy): {np.log1p(df['GDP_Capita']).corr(np.log1p(df['CO2_Total_kt'])):.4f}")
    if not rich_dirty.empty:
        print(f"   - Example 'Rich & Dirty' outliers: {rich_dirty['Country'].unique()[:3]}")
    
    plt.figure()
    sns.scatterplot(data=df, x='GDP_Capita', y='CO2_Total_kt', hue='Year', palette='viridis', alpha=0.7, size='Year', sizes=(20, 100))
    plt.xscale('log'); plt.yscale('log')
    plt.title('Fig 2: The Decoupling Test (GDP vs. CO2)')
    plt.xlabel('GDP per Capita (Log)'); plt.ylabel('CO2 Emissions (kt) (Log)')
    plt.tight_layout(); plt.savefig('figures/fig2_kuznets_curve.png'); plt.close()

def _plot_energy_mix_evolution(df):
    print("\n[Fig 3] Energy Mix (Stacked Area)")
    if 'Elec_Fossil' not in df.columns: return

    annual_mix = df.groupby('Year')[['Elec_Fossil', 'Elec_Renewables', 'Elec_Nuclear']].sum().reset_index()
    
    # DATA EXTRACTION
    start = annual_mix.iloc[0]
    end = annual_mix.iloc[-1]
    
    f_growth = ((end['Elec_Fossil'] - start['Elec_Fossil']) / start['Elec_Fossil']) * 100
    r_growth = ((end['Elec_Renewables'] - start['Elec_Renewables']) / start['Elec_Renewables']) * 100
    
    print(f"   - Fossil Generation: {start['Elec_Fossil']:.0f} TWh -> {end['Elec_Fossil']:.0f} TWh ({f_growth:+.1f}%)")
    print(f"   - Renewables Gen:    {start['Elec_Renewables']:.0f} TWh -> {end['Elec_Renewables']:.0f} TWh ({r_growth:+.1f}%)")
    print("     (Insight: Are renewables growing faster than fossils?)")

    plt.figure()
    plt.stackplot(annual_mix['Year'], annual_mix['Elec_Fossil'], annual_mix['Elec_Nuclear'], annual_mix['Elec_Renewables'], 
                  labels=['Fossil Fuels', 'Nuclear', 'Renewables'], 
                  colors=['#636e72', '#f1c40f', '#00b894'], alpha=0.85)
    plt.title(f'Fig 3: Global Electricity Generation Mix (2000-{LAST_VALID_YEAR})')
    plt.ylabel('Terawatt-hours (TWh)')
    plt.legend(loc='upper left')
    plt.tight_layout(); plt.savefig('figures/fig3_energy_mix_evolution.png'); plt.close()

def _plot_top_aid_recipients(df):
    print("\n[Fig 4] Top Aid Recipients")
    if 'Financial_Flows' not in df.columns: return
    
    total_aid = df.groupby('Country')['Financial_Flows'].sum().sort_values(ascending=False).head(10)
    
    # DATA EXTRACTION
    print("   - Top 5 Recipients (Cumulative 2000-2019):")
    for country, amount in total_aid.head(5).items():
        print(f"     * {country}: ${amount/1e9:.2f} Billion")

    plt.figure(figsize=(12, 6))
    sns.barplot(x=total_aid.values, y=total_aid.index, hue=total_aid.index, palette='Blues_r', legend=False)
    plt.title(f'Fig 4: Top 10 Recipients of Green Energy Aid (2000-{LAST_VALID_YEAR})')
    plt.xlabel('Total USD Received')
    plt.tight_layout(); plt.savefig('figures/fig4_top_aid_recipients.png'); plt.close()

def _plot_global_divergence(df):
    print("\n[Fig 5] Global Divergence (Indexed)")
    if 'GDP_Capita' not in df.columns: return
    
    annual = df.groupby('Year').agg({'GDP_Capita': 'mean', 'CO2_Total_kt': 'sum'}).reset_index()
    
    # Normalize to 2000 = 100
    base_gdp = annual['GDP_Capita'].iloc[0]
    base_co2 = annual['CO2_Total_kt'].iloc[0]
    
    annual['GDP_Idx'] = (annual['GDP_Capita'] / base_gdp) * 100
    annual['CO2_Idx'] = (annual['CO2_Total_kt'] / base_co2) * 100
    
    # DATA EXTRACTION
    final = annual.iloc[-1]
    print(f"   - 2000 Baseline: 100.0")
    print(f"   - {LAST_VALID_YEAR} GDP Index: {final['GDP_Idx']:.1f} (Growth: +{final['GDP_Idx']-100:.1f}%)")
    print(f"   - {LAST_VALID_YEAR} CO2 Index: {final['CO2_Idx']:.1f} (Growth: +{final['CO2_Idx']-100:.1f}%)")
    
    plt.figure()
    plt.plot(annual['Year'], annual['GDP_Idx'], label='Global GDP per Capita', color='#2ecc71', linewidth=4)
    plt.plot(annual['Year'], annual['CO2_Idx'], label='Total CO2 Emissions', color='#e74c3c', linewidth=4, linestyle='--')
    plt.title('Fig 5: The Decoupling Challenge (Indexed 2000=100)')
    plt.ylabel('Index Value')
    plt.legend()
    plt.tight_layout(); plt.savefig('figures/fig5_global_divergence.png'); plt.close()

def _plot_correlation_matrix(df):
    print("\n[Fig 6] Correlation Matrix")
    cols = ['GDP_Capita', 'Financial_Flows', 'Renewable_Share', 'CO2_Total_kt', 'Energy_Intensity', 'Access_Electricity']
    cols = [c for c in cols if c in df.columns]
    
    if len(cols) > 1:
        corr = df[cols].corr()
        # DATA EXTRACTION
        print("   - Key Correlations:")
        print(f"     * GDP vs Renewable Share: {corr.loc['GDP_Capita', 'Renewable_Share']:.3f}")
        print(f"     * Aid vs Access Elec:     {corr.loc['Financial_Flows', 'Access_Electricity']:.3f}")
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr, annot=True, fmt=".2f", cmap='RdBu', center=0, square=True)
        plt.title('Fig 6: Correlation Matrix of Key Drivers')
        plt.tight_layout(); plt.savefig('figures/fig6_correlation_matrix.png'); plt.close()

def _plot_top_movers(df):
    print("\n[Fig 7] Top Green Movers")
    pivoted = df.pivot_table(index='Country', columns='Year', values='Renewable_Share')
    
    if 2000 in pivoted.columns and LAST_VALID_YEAR in pivoted.columns:
        pivoted['Growth'] = pivoted[LAST_VALID_YEAR] - pivoted[2000]
        top10 = pivoted.dropna(subset=['Growth']).nlargest(10, 'Growth')
        
        # DATA EXTRACTION
        print("   - Top 5 Countries by Renewable Share Increase (points):")
        print(top10['Growth'].head(5).to_string())

        plt.figure()
        sns.barplot(x=top10['Growth'], y=top10.index, hue=top10.index, palette='Greens_r', legend=False)
        plt.title(f'Fig 7: Top 10 Countries by Renewable Share Growth (2000-{LAST_VALID_YEAR})')
        plt.xlabel('Percentage Point Increase')
        plt.tight_layout(); plt.savefig('figures/fig7_top_movers.png'); plt.close()

def _plot_income_disparity(df):
    print("\n[Fig 8] Income Disparity Boxplot")
    if 'Income_Group' not in df.columns: return
    
    # DATA EXTRACTION
    medians = df.groupby('Income_Group', observed=True)['Renewable_Share'].median()
    print("   - Median Renewable Share by Income Group:")
    print(medians.to_string())
    
    plt.figure()
    sns.boxplot(x='Income_Group', y='Renewable_Share', hue='Income_Group', data=df, palette='Set2', legend=False)
    plt.title('Fig 8: Renewable Energy Share by Income Level')
    plt.xlabel('Income Quartile (GDP/capita)')
    plt.ylabel('Renewable Share (%)')
    plt.tight_layout(); plt.savefig('figures/fig8_income_disparity.png'); plt.close()

def _plot_forecast_transition(df):
    print("\n[Fig 9] Predictive Forecast (2030)")
    if 'Renewable_Share' not in df.columns: return
    
    pivoted = df.pivot_table(index='Country', columns='Year', values='Renewable_Share')
    if 2000 not in pivoted.columns or LAST_VALID_YEAR not in pivoted.columns: return

    pivoted['Growth'] = pivoted[LAST_VALID_YEAR] - pivoted[2000]
    top_movers = pivoted.dropna(subset=['Growth']).nlargest(5, 'Growth').index.tolist()
    
    print(f"   - Forecasting for: {top_movers}")
    
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
        
        X_future = np.arange(LAST_VALID_YEAR, 2031)
        y_future = np.clip(p(X_future), 0, 100)
        
        # DATA LOGGING
        print(f"     * {country}: {LAST_VALID_YEAR}={y_hist[-1]:.1f}% -> 2030={y_future[-1]:.1f}% (Predicted)")
        
        plt.plot(X_hist, y_hist, label=f"{country} (History)", color=colors[i], linewidth=2.5, alpha=0.6)
        plt.plot(X_future, y_future, linestyle='--', color=colors[i], linewidth=3)
        plt.scatter(2030, y_future[-1], color=colors[i], s=100, zorder=5)
        plt.text(2030.5, y_future[-1], f"{y_future[-1]:.0f}%", color=colors[i], fontweight='bold')

    plt.axvline(2030, color='gray', linestyle=':', alpha=0.5)
    plt.title(f'Fig 9: Predictive Forecast - Trajectory to 2030 (History: 2000-{LAST_VALID_YEAR})', fontweight='bold')
    plt.xlabel('Year')
    plt.ylabel('Renewable Energy Share (%)')
    plt.legend(title='Country Trends', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout(); plt.savefig('figures/fig9_predictive_forecast.png'); plt.close()