# filename: visualizer.py
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# Set global style
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (12, 7)
plt.rcParams['savefig.dpi'] = 300

def create_output_folder():
    if not os.path.exists('figures'):
        os.makedirs('figures')

def generate_visualizations(df):
    """
    Generates and saves 5 key project plots to the 'figures/' directory.
    """
    create_output_folder()
    
    print("Generating visualizations...")
    _plot_equity_gap(df)
    _plot_aid_effectiveness(df)
    _plot_decoupling(df)
    _plot_correlation_heatmap(df)
    _plot_top_renewables(df)
    print("All 5 figures saved to /figures directory.")

def _plot_equity_gap(df):
    """Figure 1: The divergence between electricity and cooking access."""
    if 'Access_Electricity' not in df.columns: return

    plt.figure()
    global_trends = df.groupby('Year')[['Access_Electricity', 'Access_Cooking']].mean().reset_index()
    
    plt.plot(global_trends['Year'], global_trends['Access_Electricity'], 
             label='Electricity Access (%)', color='#2ecc71', linewidth=3)
    plt.plot(global_trends['Year'], global_trends['Access_Cooking'], 
             label='Clean Cooking Access (%)', color='#e74c3c', linewidth=3, linestyle='--')
    
    plt.fill_between(global_trends['Year'], 
                     global_trends['Access_Electricity'], 
                     global_trends['Access_Cooking'], 
                     color='gray', alpha=0.1, label='The Equity Gap')
    
    plt.title('Global Energy Equity: Infrastructure vs. Health (2000-2020)', fontsize=16)
    plt.ylabel('% of Population')
    plt.xlabel('Year')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('figures/fig1_equity_gap_trends.png')
    plt.close()

def _plot_aid_effectiveness(df):
    """Figure 2: Financial Flows vs Renewable Capacity."""
    if 'Financial_Flows' not in df.columns: return

    plt.figure()
    # Aggregate by country
    country_stats = df.groupby('Country').agg({
        'Financial_Flows': 'sum',
        'Renewable_Capacity': lambda x: x.iloc[-1] - x.iloc[0] if len(x) > 1 else 0,
        'GDP_Capita': 'mean'
    }).reset_index()
    
    subset = country_stats[country_stats['Financial_Flows'] > 0]
    
    if not subset.empty:
        sns.scatterplot(data=subset, x='Financial_Flows', y='Renewable_Capacity', 
                        size='GDP_Capita', sizes=(50, 400), hue='GDP_Capita', palette='viridis', alpha=0.7)
        
        plt.xscale('log')
        plt.title('Aid Effectiveness: Funding vs. Capacity Growth', fontsize=16)
        plt.xlabel('Total Financial Aid Received (USD, Log Scale)')
        plt.ylabel('Growth in Renewable Capacity (W/capita)')
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()
        plt.savefig('figures/fig2_aid_effectiveness_scatter.png')
        plt.close()

def _plot_decoupling(df):
    """Figure 3: GDP vs Energy Intensity."""
    if 'GDP_Capita' not in df.columns: return

    plt.figure()
    global_eco = df.groupby('Year')[['GDP_Capita', 'Energy_Intensity']].mean().reset_index()
    
    # Normalize to 2000 = 100
    global_eco['GDP_Index'] = (global_eco['GDP_Capita'] / global_eco['GDP_Capita'].iloc[0]) * 100
    global_eco['Intensity_Index'] = (global_eco['Energy_Intensity'] / global_eco['Energy_Intensity'].iloc[0]) * 100
    
    plt.plot(global_eco['Year'], global_eco['GDP_Index'], label='GDP Growth (Index)', color='#3498db', linewidth=3)
    plt.plot(global_eco['Year'], global_eco['Intensity_Index'], label='Energy Intensity (Index)', color='#f39c12', linewidth=3)
    
    plt.axhline(100, color='black', linewidth=1, linestyle='--')
    plt.title('The Efficiency Paradox: Growth vs. Intensity', fontsize=16)
    plt.ylabel('Index (Base Year 2000 = 100)')
    plt.legend()
    plt.tight_layout()
    plt.savefig('figures/fig3_efficiency_decoupling.png')
    plt.close()

def _plot_correlation_heatmap(df):
    """Figure 4: Correlation Matrix of Key Indicators."""
    plt.figure(figsize=(10, 8))
    
    cols_to_corr = ['Access_Electricity', 'Access_Cooking', 'Renewable_Capacity', 
                    'Financial_Flows', 'GDP_Capita', 'Energy_Intensity', 'CO2_Total_kt']
    
    # Filter only columns present
    cols = [c for c in cols_to_corr if c in df.columns]
    
    if len(cols) > 1:
        corr = df[cols].corr()
        mask = np.triu(np.ones_like(corr, dtype=bool))
        
        sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap='coolwarm', 
                    vmax=1, vmin=-1, square=True, linewidths=.5)
        
        plt.title('Correlation Matrix of Energy Indicators', fontsize=16)
        plt.tight_layout()
        plt.savefig('figures/fig4_correlation_heatmap.png')
        plt.close()

def _plot_top_renewables(df):
    """Figure 5: Top 20 Countries by Renewable Capacity (2020)."""
    if 'Renewable_Capacity' not in df.columns: return
    
    plt.figure(figsize=(12, 8))
    
    # Get 2020 data
    data_2020 = df[df['Year'] == 2020].sort_values(by='Renewable_Capacity', ascending=False).head(20)
    
    if not data_2020.empty:
        sns.barplot(x='Renewable_Capacity', y='Country', data=data_2020, palette='viridis')
        plt.title('Top 20 Countries by Renewable Capacity per Capita (2020)', fontsize=16)
        plt.xlabel('Watts per Capita')
        plt.ylabel('')
        plt.tight_layout()
        plt.savefig('figures/fig5_top_renewables_bar.png')
        plt.close()