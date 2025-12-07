import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os

def generate_interactive_dashboard(df):
    """
    Creates a comprehensive interactive HTML dashboard with multiple Plotly charts.
    Prints detailed data insights to the console for analysis.
    """
    print("Generating interactive dashboard (Plotly)...")
    print("\n" + "="*60)
    print("DASHBOARD DATA INSIGHTS & GRANULAR STATISTICS")
    print("="*60)
    
    # 1. Create Individual Figures & Print Details
    fig_map = _create_map(df)
    fig_equity = _create_equity_plot(df)
    fig_aid = _create_aid_plot(df)
    fig_bubble = _create_bubble_chart(df)
    fig_comparison = _create_country_comparison(df)

    print("="*60 + "\n")

    # 2. Assemble into HTML
    html_content = _assemble_html(fig_map, fig_equity, fig_aid, fig_bubble, fig_comparison)
    
    # 3. Save
    if not os.path.exists('figures'):
        os.makedirs('figures')
        
    with open('figures/interactive_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("Interactive dashboard saved to 'figures/interactive_dashboard.html'")

def _create_map(df):
    """Global Map of Renewable Capacity (Latest Year)."""
    latest_year = df['Year'].max()
    df_latest = df[df['Year'] == latest_year].copy()
    total_count = len(df_latest)
    
    # Data Insights
    print(f"\n--- [1. Global Map] Renewable Capacity Distribution ({latest_year}) ---")
    print(f"Global Average Capacity: {df_latest['Renewable_Capacity'].mean():.2f} W/capita")
    
    # Bucket Analysis
    high = len(df_latest[df_latest['Renewable_Capacity'] > 500])
    med = len(df_latest[(df_latest['Renewable_Capacity'] <= 500) & (df_latest['Renewable_Capacity'] > 50)])
    low = len(df_latest[df_latest['Renewable_Capacity'] <= 50])
    
    print(f"Distribution Buckets:")
    print(f"  > 500 W/capita (High):   {high} countries ({high/total_count:.1%})")
    print(f"  50-500 W/capita (Med):   {med} countries ({med/total_count:.1%})")
    print(f"  < 50 W/capita (Low):     {low} countries ({low/total_count:.1%})")

    print("\nTop 5 Leaders (Watts/capita):")
    top_5 = df_latest.nlargest(5, 'Renewable_Capacity')[['Country', 'Renewable_Capacity']]
    print(top_5.to_string(index=False))

    fig = px.choropleth(df_latest, 
                        locations="Country", 
                        locationmode='country names',
                        color="Renewable_Capacity",
                        hover_name="Country",
                        color_continuous_scale="Viridis",
                        title=f"Global Renewable Capacity (W/capita) - {latest_year}",
                        projection="natural earth")
    fig.update_layout(margin=dict(l=0, r=0, t=50, b=0), paper_bgcolor='rgba(0,0,0,0)')
    return fig

def _create_equity_plot(df):
    """Interactive Equity Gap Line Chart."""
    global_trends = df.groupby('Year')[['Access_Electricity', 'Access_Cooking']].mean().reset_index()
    
    # Data Insights
    print(f"\n--- [2. Equity Chart] The 'Hidden Gap' Analysis ---")
    
    # Calculate CAGR (Compound Annual Growth Rate)
    years = 20
    start_elec = global_trends.iloc[0]['Access_Electricity']
    end_elec = global_trends.iloc[-1]['Access_Electricity']
    cagr_elec = ((end_elec / start_elec) ** (1/years) - 1) * 100

    start_cook = global_trends.iloc[0]['Access_Cooking']
    end_cook = global_trends.iloc[-1]['Access_Cooking']
    cagr_cook = ((end_cook / start_cook) ** (1/years) - 1) * 100
    
    print(f"Global Growth Rates (CAGR 2000-2020):")
    print(f"  Electricity Access: {cagr_elec:+.2f}% per year")
    print(f"  Clean Cooking:      {cagr_cook:+.2f}% per year")
    print(f"  -> Insight: Electricity is growing {cagr_elec/cagr_cook:.1f}x faster than clean cooking.")

    # Identify Worst Gaps in 2020 AND their trends
    df_2020 = df[df['Year'] == 2020].copy()
    
    if not df_2020.empty:
        df_2020['Equity_Gap'] = df_2020['Access_Electricity'] - df_2020['Access_Cooking']
        top_gaps = df_2020.nlargest(5, 'Equity_Gap')[['Country', 'Access_Electricity', 'Access_Cooking', 'Equity_Gap']]
        
        # Calculate change since 2000 for these specific countries
        print("\nTop 5 Countries with Largest Equity Gap (2020):")
        print("(Negative 'Trend' means the gap is closing, Positive means it is widening)")
        
        results = []
        for _, row in top_gaps.iterrows():
            country = row['Country']
            gap_2020 = row['Equity_Gap']
            
            # Find 2000 gap
            try:
                data_2000 = df[(df['Country'] == country) & (df['Year'] == 2000)]
                if not data_2000.empty:
                    gap_2000 = data_2000.iloc[0]['Access_Electricity'] - data_2000.iloc[0]['Access_Cooking']
                    change = gap_2020 - gap_2000
                    results.append({'Country': country, 'Gap_2020': gap_2020, 'Trend_since_2000': change})
                else:
                    results.append({'Country': country, 'Gap_2020': gap_2020, 'Trend_since_2000': float('nan')})
            except:
                continue
                
        results_df = pd.DataFrame(results)
        pd.options.display.float_format = '{:,.2f}'.format
        print(results_df.to_string(index=False))

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=global_trends['Year'], y=global_trends['Access_Electricity'],
                             mode='lines+markers', name='Electricity Access',
                             line=dict(color='#00C9A7', width=4)))
    fig.add_trace(go.Scatter(x=global_trends['Year'], y=global_trends['Access_Cooking'],
                             mode='lines+markers', name='Clean Cooking',
                             line=dict(color='#FF8066', width=4, dash='dash')))
    
    fig.update_layout(title="Global Equity Gap Trends (2000-2020)",
                      xaxis_title="Year", yaxis_title="% Population Access",
                      hovermode="x unified", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(240,240,240,0.5)')
    return fig

def _create_aid_plot(df):
    """Interactive Aid Effectiveness Scatter."""
    country_stats = df.groupby('Country').agg({
        'Financial_Flows': 'sum',
        'Renewable_Capacity': lambda x: x.iloc[-1] - x.iloc[0] if len(x) > 1 else 0,
        'GDP_Capita': 'mean',
        'Access_Electricity': 'mean' 
    }).reset_index()
    
    subset = country_stats[country_stats['Financial_Flows'] > 0].copy()
    
    # FIX: Drop NaNs in 'GDP_Capita' because it is used for the 'size' property
    subset = subset.dropna(subset=['GDP_Capita'])
    
    # Data Insights
    print(f"\n--- [3. Aid Scatter] ROI & Efficiency Analysis ---")
    print(f"Total Aid Analyzed: ${subset['Financial_Flows'].sum()/1e9:,.1f} Billion")
    
    # Count "Inefficient" cases
    # Received > $50M aid but has <= 0 W/capita growth
    inefficient = subset[(subset['Financial_Flows'] > 5e7) & (subset['Renewable_Capacity'] <= 0)]
    
    print(f"\n'Ghost Aid' Alert (High Aid, Zero/Negative Growth):")
    print(f"Found {len(inefficient)} countries that received >$50M but stalled or regressed.")
    if not inefficient.empty:
        inefficient_sorted = inefficient.sort_values('Financial_Flows', ascending=False).head(5)
        print(inefficient_sorted[['Country', 'Financial_Flows', 'Renewable_Capacity']].to_string(index=False))

    if subset.empty:
        fig = go.Figure()
        fig.update_layout(title="No Data Available for Aid Plot")
        return fig

    fig = px.scatter(subset, x='Financial_Flows', y='Renewable_Capacity',
                     size='GDP_Capita', color='GDP_Capita',
                     hover_name='Country', hover_data=['Access_Electricity'],
                     log_x=True, color_continuous_scale='Plasma',
                     title="Aid Effectiveness: Funding vs Capacity Growth",
                     labels={'Financial_Flows': 'Total Aid (USD)', 'Renewable_Capacity': 'Capacity Growth (W/cap)'})
    
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(240,240,240,0.5)')
    return fig

def _create_bubble_chart(df):
    """Animated Bubble Chart: GDP vs CO2."""
    df_clean = df.dropna(subset=['GDP_Capita', 'CO2_Total_kt', 'Year', 'Country', 'Access_Electricity']).copy()
    
    # Data Insights
    print(f"\n--- [4. Bubble Chart] Decoupling Analysis ---")
    
    # Calculate Carbon Intensity (CO2 per $ GDP)
    df_clean['Carbon_Intensity'] = df_clean['CO2_Total_kt'] / df_clean['GDP_Capita']
    
    latest_year = df_clean['Year'].max()
    earliest_year = df_clean['Year'].min()
    
    # Identify countries bucking the trend (Increasing Intensity)
    # Calculate change per country
    intensity_change = []
    for country in df_clean['Country'].unique():
        c_data = df_clean[df_clean['Country'] == country]
        if len(c_data) > 1:
            start = c_data.iloc[0]['Carbon_Intensity']
            end = c_data.iloc[-1]['Carbon_Intensity']
            change_pct = ((end - start) / start) * 100
            intensity_change.append({'Country': country, 'Intensity_Change_Pct': change_pct})
    
    intensity_df = pd.DataFrame(intensity_change)
    avg_change = intensity_df['Intensity_Change_Pct'].mean()
    
    print(f"Global Average Carbon Intensity Change ({earliest_year}-{latest_year}): {avg_change:+.2f}%")
    
    print("\nOutliers: Countries Becoming LESS Efficient (Increasing Intensity):")
    worsening = intensity_df.nlargest(5, 'Intensity_Change_Pct')
    print(worsening.to_string(index=False))

    if df_clean.empty:
         fig = go.Figure()
         fig.update_layout(title="No Data Available for Bubble Chart")
         return fig
    
    fig = px.scatter(df_clean, x="GDP_Capita", y="CO2_Total_kt",
                     animation_frame="Year", animation_group="Country",
                     size="Access_Electricity", color="Country", 
                     hover_name="Country",
                     log_x=True, size_max=45,
                     range_y=[0, df_clean['CO2_Total_kt'].max()*1.1],
                     title="Evolution: Economic Growth vs Emissions (Play Animation)",
                     template="plotly_white")
    
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(240,240,240,0.5)')
    return fig

def _create_country_comparison(df):
    """Line chart with Dropdown to compare specific countries."""
    
    # Calculate Top Movers globally, not just selected ones
    # Calculate total growth 2000-2020 for all countries
    df_growth = df.groupby('Country')['Access_Electricity'].agg(['first', 'last']).reset_index()
    df_growth['Growth'] = df_growth['last'] - df_growth['first']
    
    print(f"\n--- [5. Comparison Chart] Fastest Electrifying Nations (2000-2020) ---")
    top_movers = df_growth.nlargest(5, 'Growth')
    print(top_movers.to_string(index=False))

    # For the chart, we stick to a curated list for readability
    top_countries = ['China', 'India', 'United States', 'Brazil', 'Nigeria', 'Germany', 'Indonesia', 'Pakistan', 'Afghanistan', 'Cambodia']
    df_sub = df[df['Country'].isin(top_countries)].sort_values('Year')

    fig = px.line(df_sub, x='Year', y='Access_Electricity', color='Country',
                  title="Country Deep Dive: Electricity Access",
                  markers=True)
    
    # Create updatemenus for toggling metrics
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                buttons=list([
                    dict(
                        args=[{"y": [df_sub[df_sub['Country']==c]['Access_Electricity'] for c in top_countries]},
                              {"title": "Country Deep Dive: Electricity Access"}],
                        label="Electricity",
                        method="restyle"
                    ),
                    dict(
                        args=[{"y": [df_sub[df_sub['Country']==c]['Access_Cooking'] for c in top_countries]},
                              {"title": "Country Deep Dive: Cooking Access"}],
                        label="Cooking",
                        method="restyle"
                    ),
                    dict(
                        args=[{"y": [df_sub[df_sub['Country']==c]['Renewable_Capacity'] for c in top_countries]},
                              {"title": "Country Deep Dive: Renewable Capacity"}],
                        label="Renewables",
                        method="restyle"
                    )
                ]),
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.11,
                xanchor="left",
                y=1.1,
                yanchor="top"
            ),
        ]
    )
    
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(240,240,240,0.5)')
    return fig

def _assemble_html(fig_map, fig_equity, fig_aid, fig_bubble, fig_comparison):
    """Combines Plotly figures into a Tailwind CSS layout."""
    
    # Convert figs to HTML div strings (without full html structure)
    config = {'responsive': True, 'displayModeBar': False}
    div_map = fig_map.to_html(full_html=False, include_plotlyjs='cdn', config=config)
    div_equity = fig_equity.to_html(full_html=False, include_plotlyjs=False, config=config)
    div_aid = fig_aid.to_html(full_html=False, include_plotlyjs=False, config=config)
    div_bubble = fig_bubble.to_html(full_html=False, include_plotlyjs=False, config=config)
    div_comp = fig_comparison.to_html(full_html=False, include_plotlyjs=False, config=config)

    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SDG 7 Energy Dashboard</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body {{ background-color: #f8fafc; }}
            .chart-card {{ background: white; border-radius: 12px; padding: 16px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); margin-bottom: 24px; }}
        </style>
    </head>
    <body class="text-slate-800">
        <nav class="bg-slate-900 text-white p-6 shadow-lg mb-8">
            <div class="container mx-auto">
                <h1 class="text-3xl font-bold">SDG 7 Global Tracker</h1>
                <p class="text-slate-400">Interactive Analysis of Sustainable Energy Data (2000-2020)</p>
            </div>
        </nav>

        <div class="container mx-auto px-4">
            <!-- Top Row: Map & Bubble -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div class="chart-card">
                    <h2 class="text-xl font-bold mb-2 text-slate-700">Global Capacity Map</h2>
                    {div_map}
                </div>
                <div class="chart-card">
                    <h2 class="text-xl font-bold mb-2 text-slate-700">Development Evolution (Play Animation)</h2>
                    {div_bubble}
                </div>
            </div>

            <!-- Middle Row: Equity & Aid -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div class="chart-card">
                    <h2 class="text-xl font-bold mb-2 text-slate-700">The Equity Gap</h2>
                    <p class="text-sm text-gray-500 mb-2">Compare the trajectory of electricity vs. clean cooking access.</p>
                    {div_equity}
                </div>
                <div class="chart-card">
                    <h2 class="text-xl font-bold mb-2 text-slate-700">Aid Effectiveness</h2>
                    <p class="text-sm text-gray-500 mb-2">Are financial flows correlating with capacity growth?</p>
                    {div_aid}
                </div>
            </div>

            <!-- Bottom Row: Comparison -->
            <div class="chart-card">
                <h2 class="text-xl font-bold mb-2 text-slate-700">Country Deep Dive</h2>
                <p class="text-sm text-gray-500 mb-2">Use the buttons to toggle between Electricity, Cooking, and Renewables for key nations.</p>
                {div_comp}
            </div>
            
            <footer class="text-center text-slate-500 py-8">
                <p>Generated via Python & Plotly | Data: World Bank / IEA</p>
            </footer>
        </div>
    </body>
    </html>
    """
    return html_template