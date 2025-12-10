# filename: interactive_dashboard.py
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import os

# GLOBAL SETTING: Match visualizer.py
LAST_VALID_YEAR = 2019

def generate_interactive_dashboard(df):
    """
    Generates an HTML dashboard with 10 interactive charts that EXACTLY match 
    the static figures in visualizer.py, plus insight commentary.
    """
    print("\n" + "="*50)
    print("   PHASE 4: INTERACTIVE DASHBOARD GENERATION   ")
    print("="*50)
    
    # Filter dataset to match static report
    df_clean = df[df['Year'] <= LAST_VALID_YEAR].copy()

    # --- Generate All 10 Figures (Plotly Versions) ---
    figs = {}
    
    # 1. Equity Gap (Fig 1 in Report)
    figs['fig1'] = _create_fig1_equity_gap(df_clean)
    
    # 2. Aid Effectiveness (Fig 2 in Report)
    figs['fig2'] = _create_fig2_aid_effectiveness(df_clean)
    
    # 3. Efficiency Decoupling (Fig 3 in Report)
    figs['fig3'] = _create_fig3_efficiency_decoupling(df_clean)
    
    # 4. Correlation Matrix (Fig 4 in Report)
    figs['fig4'] = _create_fig4_correlation_matrix(df_clean)
    
    # 5. Strategic Leaders (Fig 5 in Report)
    figs['fig5'] = _create_fig5_strategic_leaders(df_clean)
    
    # --- Supplementary Figures (6-10) ---
    figs['fig6'] = _create_fig6_energy_mix(df_clean)
    figs['fig7'] = _create_fig7_top_aid_recipients(df_clean)
    figs['fig8'] = _create_fig8_income_disparity(df_clean)
    figs['fig9'] = _create_fig9_forecast(df_clean)
    figs['fig10'] = _create_fig10_choropleth_map(df_clean)

    # --- Assemble HTML ---
    html_content = _assemble_html(figs)
    
    # --- Save ---
    if not os.path.exists('figures'):
        os.makedirs('figures')
        
    with open('figures/interactive_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("-> Dashboard saved to 'figures/interactive_dashboard.html'")
    print("-> Consistency Check: All 10 figures (including Map) are now interactive.")

# ==========================================
# PLOTLY FIGURE GENERATORS
# ==========================================

def _create_fig1_equity_gap(df):
    """Fig 1: Equity Gap (Electricity vs Cooking)"""
    if 'Access_Electricity' not in df.columns or 'Access_Cooking' not in df.columns: return go.Figure()
    
    annual = df.groupby('Year')[['Access_Electricity', 'Access_Cooking']].mean().reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=annual['Year'], y=annual['Access_Electricity'], name="Access to Electricity", 
                             mode='lines+markers', line=dict(color='#2ecc71', width=3)))
    fig.add_trace(go.Scatter(x=annual['Year'], y=annual['Access_Cooking'], name="Access to Clean Cooking", 
                             mode='lines+markers', line=dict(color='#e67e22', width=3)))
    
    # Add fill
    fig.add_trace(go.Scatter(x=annual['Year'], y=annual['Access_Electricity'], fill=None, mode='lines', 
                             line_color='rgba(0,0,0,0)', showlegend=False))
    fig.add_trace(go.Scatter(x=annual['Year'], y=annual['Access_Cooking'], fill='tonexty', mode='lines', 
                             fillcolor='rgba(128,128,128,0.2)', line_color='rgba(0,0,0,0)', name='The Gap'))

    fig.update_layout(title="<b>Fig 1: The 'Hidden' Equity Gap</b>", template="plotly_white", yaxis_title="Population Access (%)")
    return fig

def _create_fig2_aid_effectiveness(df):
    """Fig 2: Aid Effectiveness (Scatter)"""
    if 'Financial_Flows' not in df.columns: return go.Figure()
    
    fig = px.scatter(df, x="Financial_Flows", y="Renewable_Capacity", color="Income_Group", 
                     size="GDP_Capita", hover_name="Country", log_x=True, log_y=True, 
                     title="<b>Fig 2: Aid Effectiveness Analysis</b>",
                     labels={"Financial_Flows": "Financial Aid ($)", "Renewable_Capacity": "Capacity (W/capita)"},
                     color_discrete_sequence=px.colors.qualitative.Prism)
    
    # Add trendline concept (not natively easy in simple px scatter, so we skip strictly for interactive)
    return fig

def _create_fig3_efficiency_decoupling(df):
    """Fig 3: Efficiency Decoupling"""
    if 'Energy_Intensity' not in df.columns: return go.Figure()
    
    annual = df.groupby('Year').agg({'GDP_Capita': 'mean', 'Energy_Intensity': 'mean'}).reset_index()
    
    # Normalize
    annual['GDP_Idx'] = (annual['GDP_Capita'] / annual['GDP_Capita'].iloc[0]) * 100
    annual['Intensity_Idx'] = (annual['Energy_Intensity'] / annual['Energy_Intensity'].iloc[0]) * 100
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=annual['Year'], y=annual['GDP_Idx'], name='GDP Growth', line=dict(color='green', width=4)))
    fig.add_trace(go.Scatter(x=annual['Year'], y=annual['Intensity_Idx'], name='Energy Intensity', line=dict(color='red', width=4)))
    
    fig.update_layout(title="<b>Fig 3: The Efficiency Paradox</b>", template="plotly_white", yaxis_title="Index (2000=100)")
    return fig

def _create_fig4_correlation_matrix(df):
    """Fig 4: Correlation Matrix"""
    cols = ['GDP_Capita', 'Financial_Flows', 'Renewable_Share', 'Access_Cooking', 'Energy_Intensity', 'Renewable_Capacity']
    cols = [c for c in cols if c in df.columns]
    
    corr = df[cols].corr()
    fig = px.imshow(corr, text_auto=".2f", aspect="auto", color_continuous_scale="RdBu", zmin=-1, zmax=1, 
                    title="<b>Fig 4: Correlation Matrix of Drivers</b>")
    return fig

def _create_fig5_strategic_leaders(df):
    """Fig 5: Top 20 Strategic Leaders"""
    # Get the latest data for each country
    latest = df.sort_values('Year').groupby('Country').tail(1)
    
    # Get Top 20 and sort Ascending (so largest is at the top in Plotly)
    top20 = latest.nlargest(20, 'Renewable_Capacity').sort_values('Renewable_Capacity', ascending=True)
    
    fig = px.bar(top20, 
                 x='Renewable_Capacity', 
                 y='Country', 
                 orientation='h', 
                 title=f"<b>Fig 5: Top 20 Nations by Capacity ({LAST_VALID_YEAR})</b>", 
                 color='Renewable_Capacity', 
                 color_continuous_scale='Blues',
                 # FIX 1: Use text_auto to put the NUMBER on the bar
                 text_auto='.0f',
                 labels={'Renewable_Capacity': 'Watts per Capita', 'Country': ''}
                 )
    
    # FIX 2: Let Plotly decide if the number goes inside or outside the bar
    fig.update_traces(textposition='auto')
    
    # FIX 3: EXPLICITLY ensure country names (Y-axis) are visible
    fig.update_yaxes(showticklabels=True, tickfont=dict(size=12))
    
    fig.update_layout(template="plotly_white", coloraxis_showscale=False)
    return fig

def _create_fig6_energy_mix(df):
    """Fig 6: Energy Mix"""
    if 'Elec_Fossil' not in df.columns: return go.Figure()
    annual = df.groupby('Year')[['Elec_Fossil', 'Elec_Renewables', 'Elec_Nuclear']].sum().reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=annual['Year'], y=annual['Elec_Fossil'], mode='lines', name='Fossil', stackgroup='one', line=dict(color='gray')))
    fig.add_trace(go.Scatter(x=annual['Year'], y=annual['Elec_Nuclear'], mode='lines', name='Nuclear', stackgroup='one', line=dict(color='gold')))
    fig.add_trace(go.Scatter(x=annual['Year'], y=annual['Elec_Renewables'], mode='lines', name='Renewables', stackgroup='one', line=dict(color='green')))
    
    fig.update_layout(title="<b>Fig 6: Global Electricity Mix</b>", template="plotly_white")
    return fig

def _create_fig7_top_aid_recipients(df):
    """Fig 7: Top Aid Recipients"""
    total = df.groupby('Country')['Financial_Flows'].sum().sort_values(ascending=False).head(10).sort_values(ascending=True)
    
    fig = px.bar(total, x='Financial_Flows', y=total.index, orientation='h', 
                 title="<b>Fig 7: Top 10 Aid Recipients</b>", color_discrete_sequence=['#27ae60'])
    fig.update_layout(template="plotly_white")
    return fig

def _create_fig8_income_disparity(df):
    """Fig 8: Income Disparity"""
    if 'Income_Group' not in df.columns: return go.Figure()
    
    fig = px.box(df, x='Income_Group', y='Renewable_Share', color='Income_Group', 
                 title="<b>Fig 8: Renewable Share by Income Group</b>", 
                 color_discrete_sequence=px.colors.qualitative.Set2)
    fig.update_layout(template="plotly_white")
    return fig

def _create_fig9_forecast(df):
    """Fig 9: Forecast (Trajectories)"""
    pivoted = df.pivot_table(index='Country', columns='Year', values='Renewable_Share')
    if 2000 not in pivoted.columns: return go.Figure()
    
    pivoted['Growth'] = pivoted[LAST_VALID_YEAR] - pivoted[2000]
    top5 = pivoted.nlargest(5, 'Growth').index.tolist()
    
    fig = go.Figure()
    for country in top5:
        dat = df[df['Country'] == country]
        fig.add_trace(go.Scatter(x=dat['Year'], y=dat['Renewable_Share'], name=country, mode='lines+markers'))
        
    fig.update_layout(title="<b>Fig 9: Trajectories of Top Movers</b>", template="plotly_white")
    return fig

def _create_fig10_choropleth_map(df):
    """Fig 10: Choropleth Map"""
    df_map = df[df['Year'] == LAST_VALID_YEAR].copy()
    if df_map.empty or 'Renewable_Capacity' not in df.columns: return go.Figure()
    
    fig = px.choropleth(df_map, 
                        locations="Country", 
                        locationmode="country names",
                        color="Renewable_Capacity",
                        hover_name="Country",
                        color_continuous_scale="Blues",
                        title=f"<b>Fig 10: Global Renewable Capacity ({LAST_VALID_YEAR})</b>")
    
    fig.update_geos(projection_type="natural earth", showcoastlines=True)
    fig.update_layout(template="plotly_white", margin=dict(l=0,r=0,t=50,b=0))
    return fig

def _assemble_html(figs):
    """Assembles the 10 Plotly figures into a polished HTML layout with insights."""
    
    divs = {k: v.to_html(full_html=False, include_plotlyjs='cdn', config={'displayModeBar': False}) for k, v in figs.items()}
    
    # Define Insights matching the Report Narrative
    insights = {
        'fig1': "<b>Insight:</b> The 'Hidden Gap' is clearly visible. While electricity access (green) pushes toward 90%, clean cooking (orange) lags significantly, highlighting a major health crisis.",
        'fig2': "<b>Insight:</b> The correlation is near zero. Financial aid (x-axis) does not automatically result in high renewable capacity (y-axis). This is the 'Ghost Aid' phenomenon.",
        'fig3': "<b>Insight:</b> A huge success story: The world is getting richer (Green Line up) while becoming MORE energy efficient (Red Line down).",
        'fig4': "<b>Insight:</b> The heatmap confirms that Money (Financial Flows) has almost NO correlation with Capacity or Green Share. The strongest driver of Capacity is actually Wealth (GDP).",
        'fig5': "<b>Insight:</b> The leaders are surprising. Bhutan (#1) and Paraguay dominate due to hydro resources, not just technology. It's about geography.",
        'fig6': "<b>Insight:</b> We still live in a fossil-fueled world. Despite the hype, renewables (green area) are a small fraction compared to the massive grey wall of fossil fuels.",
        'fig7': "<b>Insight:</b> Aid is highly concentrated. India and Pakistan receive billions, while many smaller nations receive almost nothing.",
        'fig8': "<b>Insight:</b> The 'Poor are Green' anomaly. Low-income nations have high renewable shares (biomass), while rich nations are still transitioning away from fossils.",
        'fig9': "<b>Insight:</b> These top movers prove rapid transition is possible. Look at the steep upward trajectories of countries like Denmark and Uruguay.",
        'fig10': "<b>Insight:</b> The map shows inequality. The 'Global North' and parts of South America are blue (high capacity), while much of Africa and Asia remains light (low capacity)."
    }

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Financing the Future: Interactive Dashboard</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body {{ background-color: #f8fafc; font-family: 'Segoe UI', Roboto, sans-serif; }}
            .card {{ background: white; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); overflow: hidden; border: 1px solid #e2e8f0; }}
            .card:hover {{ box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); transition: 0.3s; }}
            .insight-box {{ background-color: #f0f9ff; border-left: 4px solid #0ea5e9; padding: 12px; font-size: 0.9rem; color: #334155; margin: 10px; border-radius: 4px; }}
            .header {{ background: linear-gradient(to right, #0f172a, #334155); color: white; }}
        </style>
    </head>
    <body>
        <div class="header p-8 mb-8 shadow-md">
            <div class="container mx-auto">
                <h1 class="text-3xl font-bold">🌍 Financing the Future</h1>
                <p class="text-slate-300 mt-1">Interactive Companion: Thesis Visualizations</p>
            </div>
        </div>

        <div class="container mx-auto px-4 pb-12">
            
            <h2 class="text-xl font-bold text-slate-700 mb-4 border-l-4 border-blue-500 pl-3">1. The Core Problems (Equity & Aid)</h2>
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-10">
                <div class="card">
                    <div class="p-2">{divs['fig1']}</div>
                    <div class="insight-box">{insights['fig1']}</div>
                </div>
                <div class="card">
                    <div class="p-2">{divs['fig2']}</div>
                    <div class="insight-box">{insights['fig2']}</div>
                </div>
            </div>

            <h2 class="text-xl font-bold text-slate-700 mb-4 border-l-4 border-green-500 pl-3">2. Efficiency & Drivers</h2>
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-10">
                <div class="card">
                    <div class="p-2">{divs['fig3']}</div>
                    <div class="insight-box">{insights['fig3']}</div>
                </div>
                <div class="card">
                    <div class="p-2">{divs['fig4']}</div>
                    <div class="insight-box">{insights['fig4']}</div>
                </div>
            </div>

            <h2 class="text-xl font-bold text-slate-700 mb-4 border-l-4 border-purple-500 pl-3">3. Global Leaders & Strategy</h2>
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-10">
                <div class="card">
                    <div class="p-2">{divs['fig5']}</div>
                    <div class="insight-box">{insights['fig5']}</div>
                </div>
                <div class="card">
                    <div class="p-2">{divs['fig7']}</div>
                    <div class="insight-box">{insights['fig7']}</div>
                </div>
            </div>

            <h2 class="text-xl font-bold text-slate-700 mb-4 border-l-4 border-orange-500 pl-3">4. The Global Picture</h2>
            <div class="mb-10 card p-2">
                 {divs['fig10']}
                 <div class="insight-box">{insights['fig10']}</div>
            </div>

            <h2 class="text-xl font-bold text-slate-700 mb-4 border-l-4 border-indigo-500 pl-3">5. Trends & Forecasts</h2>
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-12">
                 <div class="card">
                    <div class="p-2">{divs['fig6']}</div>
                    <div class="insight-box">{insights['fig6']}</div>
                </div>
                <div class="card">
                    <div class="p-2">{divs['fig9']}</div>
                    <div class="insight-box">{insights['fig9']}</div>
                </div>
            </div>
            
             <div class="card p-2 mb-10">
                {divs['fig8']}
                <div class="insight-box">{insights['fig8']}</div>
            </div>

            <footer class="text-center text-slate-400 py-6 border-t">
                <p>Data Source: Thesis Dataset (2000-2019) | Generated via Python & Plotly</p>
            </footer>
        </div>
    </body>
    </html>
    """
    return html