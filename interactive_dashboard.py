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
    print("\n" + "="*50)
    print("DASHBOARD DATA INSIGHTS & SUMMARY STATISTICS")
    print("="*50)
    
    # 1. Create Individual Figures & Print Details
    fig_map = _create_map(df)
    fig_equity = _create_equity_plot(df)
    fig_aid = _create_aid_plot(df)
    fig_bubble = _create_bubble_chart(df)
    fig_comparison = _create_country_comparison(df)

    print("="*50 + "\n")

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
    
    # Data Insights
    print(f"\n--- [1. Global Map] Renewable Capacity ({latest_year}) ---")
    top_5 = df_latest.nlargest(5, 'Renewable_Capacity')[['Country', 'Renewable_Capacity']]
    print("Top 5 Countries (Watts/capita):")
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
    print(f"\n--- [2. Equity Chart] Global Access Trends ---")
    start_row = global_trends.iloc[0]
    end_row = global_trends.iloc[-1]
    print(f"Year {int(start_row['Year'])}: Elec={start_row['Access_Electricity']:.1f}%, Cooking={start_row['Access_Cooking']:.1f}%")
    print(f"Year {int(end_row['Year'])}: Elec={end_row['Access_Electricity']:.1f}%, Cooking={end_row['Access_Cooking']:.1f}%")
    gap_2020 = end_row['Access_Electricity'] - end_row['Access_Cooking']
    print(f"Final Equity Gap (2020): {gap_2020:.2f}% points")

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
    print(f"\n--- [3. Aid Scatter] Financial Flows vs. Capacity Growth ---")
    print(f"Number of Aid Recipients analyzed: {len(subset)}")
    if len(subset) > 1:
        corr = subset['Financial_Flows'].corr(subset['Renewable_Capacity'])
        print(f"Correlation Coefficient: {corr:.4f}")
    
    top_recipient = subset.nlargest(1, 'Financial_Flows').iloc[0]
    print(f"Top Recipient: {top_recipient['Country']}")
    print(f"  - Total Aid: ${top_recipient['Financial_Flows']:,.0f}")
    print(f"  - Capacity Growth: {top_recipient['Renewable_Capacity']:.2f} W/capita")

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
    print(f"\n--- [4. Bubble Chart] GDP vs CO2 Animation ---")
    print(f"Data points included: {len(df_clean)}")
    print(f"Unique Countries: {df_clean['Country'].nunique()}")
    min_co2 = df_clean['CO2_Total_kt'].min()
    max_co2 = df_clean['CO2_Total_kt'].max()
    print(f"CO2 Range: {min_co2:.2f} to {max_co2:,.2f} kt")

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
    top_countries = ['China', 'India', 'United States', 'Brazil', 'Nigeria', 'Germany', 'Indonesia', 'Pakistan']
    df_sub = df[df['Country'].isin(top_countries)].sort_values('Year')
    
    # Data Insights
    print(f"\n--- [5. Comparison Chart] Selected Country Stats (2020) ---")
    stats_2020 = df_sub[df_sub['Year'] == 2020][['Country', 'Access_Electricity', 'Access_Cooking', 'Renewable_Capacity']]
    print(stats_2020.to_string(index=False))

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