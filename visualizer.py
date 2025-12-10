# filename: visualizer.py
import matplotlib.pyplot as plt
import geopandas as gpd
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
    Generates 10 static figures aligned with the 'Financing the Future' PDF report.
    """
    create_output_folder()
    print("\n" + "="*60)
    print(f"   PHASE 3: VISUALIZATION GENERATION (Aligned to Report)   ")
    print("="*60)
    
    # Filter dataset
    df_clean = df[df['Year'] <= LAST_VALID_YEAR].copy()
    
    # Generating EDA visualizations
    _plot_eda_summary(df)

    # --- REPORT FIGURES (1-5) ---
    _plot_fig1_equity_gap(df_clean)
    _plot_fig2_aid_effectiveness(df_clean)
    _plot_fig3_efficiency_decoupling(df_clean)
    _plot_fig4_correlation_matrix(df_clean)
    _plot_fig5_strategic_leaders(df_clean)
    
    # --- SUPPLEMENTARY FIGURES (6-10) ---
    _plot_fig6_energy_mix(df_clean)
    _plot_fig7_top_aid_recipients(df_clean)
    _plot_fig8_income_disparity(df_clean)
    _plot_fig9_forecast(df_clean)
    _plot_fig10_choropleth_map(df_clean)
    
    print("\n-> All figures saved to /figures directory.")

# --- EDA VISUALIZATION FUNCTIONS ---

def _plot_eda_summary(df):
    print("\n[EDA] Summary Stats")
    
    # 1. Histogram Stats
    if 'Energy_Intensity' in df.columns:
        mean_val = df['Energy_Intensity'].mean()
        median_val = df['Energy_Intensity'].median()
        skew_val = df['Energy_Intensity'].skew()
        print(f"   - Intensity: Mean={mean_val:.2f}, Median={median_val:.2f}, Skew={skew_val:.2f}")
        
        plt.figure(figsize=(10, 6))
        sns.histplot(df['Energy_Intensity'], kde=True, color='purple', bins=30)
        plt.title('EDA: Distribution of Energy Intensity (Skew Check)', fontweight='bold')
        plt.xlabel('Energy Intensity (MJ/$ GDP)')
        plt.ylabel('Frequency')
        plt.tight_layout(); plt.savefig('figures/fig_eda_1_intensity_histogram.png'); plt.close()

    # 2. Boxplot Stats
    cols = ['Access_Electricity', 'Access_Cooking', 'Renewable_Capacity', 'Energy_Intensity']
    available = [c for c in cols if c in df.columns]
    if available:
        print("   - Outlier Detection (Max Values):")
        for c in available:
            print(f"     {c}: Max = {df[c].max():.2f}")
            
        plt.figure(figsize=(14, 8))
        df_melt = df[available].melt(var_name='Indicator', value_name='Value')
        sns.boxplot(x='Indicator', y='Value', data=df_melt, palette='Set2')
        plt.yscale('log')
        plt.title('EDA: Outlier Detection', fontweight='bold')
        plt.tight_layout(); plt.savefig('figures/fig_eda_2_multi_boxplot.png'); plt.close()

    # 3. Missing Values
    plt.figure(figsize=(12, 6))
    missing = df.isnull().sum()
    missing = missing[missing > 0].sort_values(ascending=False)
    if not missing.empty:
        print(f"   - Missing Values Found: {missing.to_dict()}")
        sns.barplot(x=missing.values, y=missing.index, palette='Reds_r')
        plt.title('EDA: Missing Values Summary', fontweight='bold')
        plt.tight_layout(); plt.savefig('figures/fig_eda_3_missing_values.png'); plt.close()

# --- REPORT FIGURES (MATCHING PDF) ---

def _plot_fig1_equity_gap(df):
    print("\n[Fig 1] Equity Gap (Electricity vs Cooking)")
    if 'Access_Electricity' not in df.columns or 'Access_Cooking' not in df.columns: return

    annual = df.groupby('Year')[['Access_Electricity', 'Access_Cooking']].mean().reset_index()
    
    # Log the gap for the report
    gap_2000 = annual.iloc[0]['Access_Electricity'] - annual.iloc[0]['Access_Cooking']
    gap_end = annual.iloc[-1]['Access_Electricity'] - annual.iloc[-1]['Access_Cooking']
    print(f"   - Gap 2000: {gap_2000:.2f}% | Gap {LAST_VALID_YEAR}: {gap_end:.2f}%")
    
    # Detailed Data Log
    print("   - Annual Data Points (Year | Elec | Cooking):")
    for _, row in annual.iterrows():
        print(f"     {int(row['Year'])}: {row['Access_Electricity']:.2f}% | {row['Access_Cooking']:.2f}%")

    plt.figure()
    plt.plot(annual['Year'], annual['Access_Electricity'], label='Access to Electricity', color='#2ecc71', linewidth=3)
    plt.plot(annual['Year'], annual['Access_Cooking'], label='Access to Clean Cooking', color='#e67e22', linewidth=3)
    
    # Fill the gap
    plt.fill_between(annual['Year'], annual['Access_Electricity'], annual['Access_Cooking'], color='gray', alpha=0.1, label='The Equity Gap')
    
    plt.title('Fig 1: The "Hidden" Equity Gap (Infrastructure vs. Health)')
    plt.ylabel('Population Access (%)')
    plt.ylim(40, 100)
    plt.legend()
    plt.tight_layout(); plt.savefig('figures/fig1_equity_gap.png'); plt.close()

def _plot_fig2_aid_effectiveness(df):
    print("\n[Fig 2] Aid Effectiveness (Scatter)")
    if 'Financial_Flows' not in df.columns: return

    # Log for report
    corr = df['Financial_Flows'].corr(df['Renewable_Capacity'])
    print(f"   - Correlation (Aid vs Capacity): r = {corr:.4f}")
    
    # Check stats by group to verify visual clusters
    print("   - Average Stats by Income Group:")
    group_stats = df.groupby('Income_Group')[['Financial_Flows', 'Renewable_Capacity']].mean()
    print(group_stats.to_string())

    plt.figure()
    sns.scatterplot(data=df, x='Financial_Flows', y='Renewable_Capacity', hue='Income_Group', palette='viridis', size='GDP_Capita', sizes=(20, 200), alpha=0.7)
    
    # Add trendline (flat)
    sns.regplot(data=df, x='Financial_Flows', y='Renewable_Capacity', scatter=False, color='red', line_kws={'linestyle':'--'})
    
    plt.title(f'Fig 2: Aid Effectiveness (r={corr:.2f})')
    plt.xlabel('Financial Aid Received (USD)')
    plt.ylabel('Renewable Capacity (W/capita)')
    plt.xscale('log')
    plt.yscale('log')
    plt.tight_layout(); plt.savefig('figures/fig2_aid_effectiveness.png'); plt.close()

def _plot_fig3_efficiency_decoupling(df):
    print("\n[Fig 3] Efficiency Decoupling (GDP vs Energy Intensity)")
    if 'Energy_Intensity' not in df.columns: return

    annual = df.groupby('Year').agg({'GDP_Capita': 'mean', 'Energy_Intensity': 'mean'}).reset_index()
    
    # Normalize to 2000 = 100
    base_gdp = annual['GDP_Capita'].iloc[0]
    base_int = annual['Energy_Intensity'].iloc[0]
    
    annual['GDP_Idx'] = (annual['GDP_Capita'] / base_gdp) * 100
    annual['Intensity_Idx'] = (annual['Energy_Intensity'] / base_int) * 100
    
    print(f"   - Baseline (2000): GDP=${base_gdp:.2f}, Intensity={base_int:.2f} MJ/$")
    print(f"   - Final ({LAST_VALID_YEAR}): GDP=${annual['GDP_Capita'].iloc[-1]:.2f}, Intensity={annual['Energy_Intensity'].iloc[-1]:.2f} MJ/$")
    print(f"   - Indices ({LAST_VALID_YEAR}): GDP Index={annual['GDP_Idx'].iloc[-1]:.1f}, Intensity Index={annual['Intensity_Idx'].iloc[-1]:.1f}")

    plt.figure()
    plt.plot(annual['Year'], annual['GDP_Idx'], label='Global GDP per Capita', color='green', linewidth=4)
    plt.plot(annual['Year'], annual['Intensity_Idx'], label='Energy Intensity (MJ/$)', color='red', linewidth=4)
    
    plt.title('Fig 3: The Efficiency Paradox (Decoupling Growth from Energy Use)')
    plt.ylabel('Index (2000 = 100)')
    plt.legend()
    plt.tight_layout(); plt.savefig('figures/fig3_efficiency_decoupling.png'); plt.close()

def _plot_fig4_correlation_matrix(df):
    print("\n[Fig 4] Correlation Matrix")
    # Updated to include Energy Intensity and Cooking
    cols = ['GDP_Capita', 'Financial_Flows', 'Renewable_Share', 'Access_Cooking', 'Energy_Intensity', 'Renewable_Capacity']
    cols = [c for c in cols if c in df.columns]
    
    corr = df[cols].corr()
    print("   - Correlation Values:")
    print(corr.to_string())

    plt.figure(figsize=(10, 8))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap='RdBu', center=0)
    plt.title('Fig 4: Correlation Matrix of Drivers')
    plt.tight_layout(); plt.savefig('figures/fig4_correlation_matrix.png'); plt.close()

def _plot_fig5_strategic_leaders(df):
    print("\n[Fig 5] Top 20 Strategic Leaders (Capacity)")
    # Get latest year data per country
    latest = df.sort_values('Year').groupby('Country').tail(1)
    top20 = latest.nlargest(20, 'Renewable_Capacity')
    
    print(f"   - Top 20 Countries by Capacity in {LAST_VALID_YEAR}:")
    for rank, (idx, row) in enumerate(top20.iterrows(), 1):
        print(f"     {rank}. {row['Country']}: {row['Renewable_Capacity']:.2f} W/capita")

    plt.figure(figsize=(12, 8))
    sns.barplot(x=top20['Renewable_Capacity'], y=top20['Country'], palette='Blues_r')
    plt.title(f'Fig 5: Top 20 Nations by Renewable Capacity ({LAST_VALID_YEAR})')
    plt.xlabel('Watts per Capita')
    plt.tight_layout(); plt.savefig('figures/fig5_strategic_leaders.png'); plt.close()

# --- SUPPLEMENTARY FIGURES (6-10) ---

def _plot_fig6_energy_mix(df):
    print("\n[Fig 6] Global Energy Mix")
    if 'Elec_Fossil' not in df.columns: return
    annual = df.groupby('Year')[['Elec_Fossil', 'Elec_Renewables', 'Elec_Nuclear']].sum().reset_index()
    
    print("   - Global TWh Generation (Start vs End):")
    for yr_idx in [0, -1]:
        row = annual.iloc[yr_idx]
        print(f"     Year {int(row['Year'])}: Fossil={row['Elec_Fossil']:.0f} | Renewables={row['Elec_Renewables']:.0f} | Nuclear={row['Elec_Nuclear']:.0f}")

    plt.figure()
    plt.stackplot(annual['Year'], annual['Elec_Fossil'], annual['Elec_Nuclear'], annual['Elec_Renewables'], labels=['Fossil', 'Nuclear', 'Renewables'], colors=['gray', 'gold', 'green'], alpha=0.8)
    plt.title('Fig 6: Global Electricity Generation Mix')
    plt.legend(loc='upper left')
    plt.tight_layout(); plt.savefig('figures/fig6_energy_mix.png'); plt.close()

def _plot_fig7_top_aid_recipients(df):
    print("\n[Fig 7] Top Aid Recipients")
    total = df.groupby('Country')['Financial_Flows'].sum().sort_values(ascending=False).head(10)
    
    print("   - Top 10 Total Financial Aid Received (All Years Sum):")
    for country, val in total.items():
        print(f"     {country}: ${val:,.0f}")

    plt.figure()
    sns.barplot(x=total.values, y=total.index, palette='Greens_r')
    plt.title('Fig 7: Top 10 Recipients of Financial Aid')
    plt.tight_layout(); plt.savefig('figures/fig7_top_aid.png'); plt.close()

def _plot_fig8_income_disparity(df):
    print("\n[Fig 8] Income Disparity (Renewable Share)")
    
    print("   - Median Renewable Share by Income Group:")
    medians = df.groupby('Income_Group')['Renewable_Share'].median().sort_values(ascending=False)
    print(medians.to_string())

    plt.figure()
    sns.boxplot(x='Income_Group', y='Renewable_Share', data=df, palette='Set2')
    plt.title('Fig 8: Renewable Share by Income Group')
    plt.tight_layout(); plt.savefig('figures/fig8_income_disparity.png'); plt.close()

def _plot_fig9_forecast(df):
    print("\n[Fig 9] Forecast/Trajectories")
    pivoted = df.pivot_table(index='Country', columns='Year', values='Renewable_Share')
    if 2000 not in pivoted.columns: return
    
    pivoted['Growth'] = pivoted[LAST_VALID_YEAR] - pivoted[2000]
    top = pivoted.nlargest(5, 'Growth')
    
    print("   - Top 5 Movers (Share Growth 2000-2019):")
    for country, row in top.iterrows():
        print(f"     {country}: {row[2000]:.1f}% -> {row[LAST_VALID_YEAR]:.1f}% (Growth: +{row['Growth']:.1f}%)")

    plt.figure()
    for c in top.index:
        dat = df[df['Country'] == c]
        plt.plot(dat['Year'], dat['Renewable_Share'], label=c)
    plt.title('Fig 9: Trajectories of Top Movers')
    plt.legend()
    plt.tight_layout(); plt.savefig('figures/fig9_forecast.png'); plt.close()

def _plot_fig10_choropleth_map(df):
    print("\n[Fig 10] Choropleth Map Data Check")
    # Uses internet data for geometry
    try:
        world = gpd.read_file("https://raw.githubusercontent.com/python-visualization/folium/main/examples/data/world-countries.json")
        data_map = df[df['Year'] == LAST_VALID_YEAR].copy()
        
        # Check merge integrity
        print(f"   - Map Year: {LAST_VALID_YEAR}")
        print(f"   - Countries in Dataset: {len(data_map)}")
        print(f"   - Countries in GeoJSON: {len(world)}")
        
        world_data = world.merge(data_map, how="left", left_on="name", right_on="Country")
        fig, ax = plt.subplots(1, 1, figsize=(16, 10))
        world_data.plot(column='Renewable_Capacity', ax=ax, legend=True, cmap='Blues', missing_kwds={'color': 'lightgrey'})
        ax.set_axis_off()
        plt.title(f'Fig 10: Global Renewable Capacity Map ({LAST_VALID_YEAR})')
        plt.tight_layout(); plt.savefig('figures/fig10_map.png'); plt.close()
    except Exception as e:
        print(f"Skipping map generation due to: {e}")