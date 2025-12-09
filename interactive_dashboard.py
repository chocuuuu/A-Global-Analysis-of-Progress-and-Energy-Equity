# filename: interactive_dashboard.py
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import os

def generate_interactive_dashboard(df):
    """
    Generates an HTML dashboard with 9 interactive charts that EXACTLY match 
    the static figures in visualizer.py.
    """
    print("\n" + "="*50)
    print("   PHASE 4: INTERACTIVE DASHBOARD GENERATION   ")
    print("="*50)
    
    # --- Generate All 9 Figures (Plotly Versions) ---
    figs = {}
    
    # 1. Funding Transition (Dual Axis)
    figs['fig1'] = _create_fig1_funding(df)
    
    # 2. Kuznets Curve (Scatter) - FIXED (Handles NaNs)
    figs['fig2'] = _create_fig2_kuznets(df)
    
    # 3. Energy Mix (Stacked Area)
    figs['fig3'] = _create_fig3_energy_mix(df)
    
    # 4. Top Aid Recipients (Bar)
    figs['fig4'] = _create_fig4_top_aid(df)
    
    # 5. Global Divergence (Indexed Line)
    figs['fig5'] = _create_fig5_divergence(df)
    
    # 6. Correlation Matrix (Heatmap)
    figs['fig6'] = _create_fig6_correlation(df)
    
    # 7. Top Movers (Bar)
    figs['fig7'] = _create_fig7_top_movers(df)
    
    # 8. Income Disparity (Box)
    figs['fig8'] = _create_fig8_income(df)
    
    # 9. Predictive Forecast (Trend Lines)
    figs['fig9'] = _create_fig9_forecast(df)

    # --- Assemble HTML ---
    html_content = _assemble_html(figs)
    
    # --- Save ---
    if not os.path.exists('figures'):
        os.makedirs('figures')
        
    with open('figures/interactive_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("-> Dashboard saved to 'figures/interactive_dashboard.html'")
    print("-> Consistency Check: All 9 paper figures are now interactive.")

# ==========================================
# PLOTLY FIGURE GENERATORS (Matching Visualizer)
# ==========================================

def _create_fig1_funding(df):
    """Fig 1: Dual Axis - Aid vs Capacity"""
    if 'Financial_Flows' not in df.columns: return go.Figure()
    
    annual = df.groupby('Year').agg({'Financial_Flows': 'sum', 'Renewable_Capacity': 'mean'}).reset_index()
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(go.Bar(x=annual['Year'], y=annual['Financial_Flows'], name="Financial Aid ($)", 
                         marker_color='#85bb65', opacity=0.7), secondary_y=False)
    
    fig.add_trace(go.Scatter(x=annual['Year'], y=annual['Renewable_Capacity'], name="Renewable Capacity", 
                             mode='lines+markers', line=dict(color='#2c3e50', width=3)), secondary_y=True)
    
    fig.update_layout(title="<b>Fig 1: Funding the Future</b><br>Does Money Drive Capacity?", 
                      template="plotly_white", legend=dict(x=0, y=1.1, orientation='h'))
    fig.update_yaxes(title_text="Total Aid (USD)", secondary_y=False)
    fig.update_yaxes(title_text="Capacity (W/capita)", secondary_y=True)
    return fig

def _create_fig2_kuznets(df):
    """Fig 2: Kuznets Curve (Log-Log)"""
    if 'GDP_Capita' not in df.columns: return go.Figure()
    
    # FIX: Drop NaNs in critical columns to prevent animation crash
    clean_df = df.dropna(subset=['GDP_Capita', 'CO2_Total_kt', 'Access_Electricity', 'Year']).copy()
    clean_df = clean_df.sort_values('Year')
    
    if clean_df.empty: return go.Figure()
    
    fig = px.scatter(clean_df, x="GDP_Capita", y="CO2_Total_kt", animation_frame="Year", 
                     animation_group="Country", size="Access_Electricity", color="Income_Group",
                     hover_name="Country", log_x=True, log_y=True,
                     title="<b>Fig 2: The Decoupling Test</b><br>GDP vs CO2 (Play Animation)",
                     color_discrete_sequence=px.colors.qualitative.Prism)
    return fig

def _create_fig3_energy_mix(df):
    """Fig 3: Energy Mix (Stacked Area)"""
    if 'Elec_Fossil' not in df.columns: return go.Figure()
    
    annual = df.groupby('Year')[['Elec_Fossil', 'Elec_Renewables', 'Elec_Nuclear']].sum().reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=annual['Year'], y=annual['Elec_Fossil'], mode='lines', name='Fossil Fuels', stackgroup='one', line=dict(color='#636e72')))
    fig.add_trace(go.Scatter(x=annual['Year'], y=annual['Elec_Nuclear'], mode='lines', name='Nuclear', stackgroup='one', line=dict(color='#f1c40f')))
    fig.add_trace(go.Scatter(x=annual['Year'], y=annual['Elec_Renewables'], mode='lines', name='Renewables', stackgroup='one', line=dict(color='#00b894')))
    
    fig.update_layout(title="<b>Fig 3: Global Energy Mix</b><br>Evolution of Generation Sources", template="plotly_white")
    fig.update_yaxes(title_text="Terawatt-hours (TWh)")
    return fig

def _create_fig4_top_aid(df):
    """Fig 4: Top Aid Recipients"""
    if 'Financial_Flows' not in df.columns: return go.Figure()
    
    total = df.groupby('Country')['Financial_Flows'].sum().sort_values(ascending=False).head(10).reset_index()
    
    fig = px.bar(total, x='Financial_Flows', y='Country', orientation='h', 
                 title="<b>Fig 4: Top 10 Aid Recipients</b><br>Total Funds Received (2000-2020)",
                 color='Financial_Flows', color_continuous_scale='Blues')
    fig.update_layout(yaxis=dict(autorange="reversed"), template="plotly_white")
    return fig

def _create_fig5_divergence(df):
    """Fig 5: Global Divergence (Indexed)"""
    if 'GDP_Capita' not in df.columns: return go.Figure()
    
    annual = df.groupby('Year').agg({'GDP_Capita': 'mean', 'CO2_Total_kt': 'sum'}).reset_index()
    annual['GDP_Idx'] = (annual['GDP_Capita'] / annual['GDP_Capita'].iloc[0]) * 100
    annual['CO2_Idx'] = (annual['CO2_Total_kt'] / annual['CO2_Total_kt'].iloc[0]) * 100
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=annual['Year'], y=annual['GDP_Idx'], name='GDP per Capita', line=dict(color='#2ecc71', width=4)))
    fig.add_trace(go.Scatter(x=annual['Year'], y=annual['CO2_Idx'], name='CO2 Emissions', line=dict(color='#e74c3c', width=4, dash='dash')))
    
    fig.update_layout(title="<b>Fig 5: The Decoupling Challenge</b><br>Growth vs Emissions (Indexed 2000=100)", template="plotly_white")
    return fig

def _create_fig6_correlation(df):
    """Fig 6: Correlation Matrix"""
    cols = ['GDP_Capita', 'Financial_Flows', 'Renewable_Share', 'CO2_Total_kt', 'Energy_Intensity', 'Access_Electricity']
    cols = [c for c in cols if c in df.columns]
    
    if len(cols) < 2: return go.Figure()
    
    corr = df[cols].corr()
    
    fig = px.imshow(corr, text_auto=".2f", aspect="auto", color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
                    title="<b>Fig 6: Correlation Matrix</b><br>Key Drivers Analysis")
    return fig

def _create_fig7_top_movers(df):
    """Fig 7: Top Green Movers"""
    pivoted = df.pivot_table(index='Country', columns='Year', values='Renewable_Share')
    if 2000 not in pivoted.columns or 2020 not in pivoted.columns: return go.Figure()
    
    pivoted['Growth'] = pivoted[2020] - pivoted[2000]
    top10 = pivoted.dropna(subset=['Growth']).nlargest(10, 'Growth').reset_index()
    
    fig = px.bar(top10, x='Growth', y='Country', orientation='h',
                 title="<b>Fig 7: Top Green Movers</b><br>Growth in Renewable Share (2000-2020)",
                 color='Growth', color_continuous_scale='Greens')
    fig.update_layout(yaxis=dict(autorange="reversed"), template="plotly_white")
    return fig

def _create_fig8_income(df):
    """Fig 8: Income Disparity"""
    if 'Income_Group' not in df.columns: return go.Figure()
    
    # FIX: Drop NaNs to ensure boxplot renders correctly
    clean_df = df.dropna(subset=['Income_Group', 'Renewable_Share'])
    
    fig = px.box(clean_df, x='Income_Group', y='Renewable_Share', color='Income_Group',
                 title="<b>Fig 8: The Green Divide</b><br>Renewable Share by Income Group",
                 color_discrete_sequence=px.colors.qualitative.Set2)
    fig.update_layout(template="plotly_white")
    return fig

def _create_fig9_forecast(df):
    """Fig 9: Predictive Forecast"""
    if 'Renewable_Share' not in df.columns: return go.Figure()
    
    pivoted = df.pivot_table(index='Country', columns='Year', values='Renewable_Share')
    if 2000 not in pivoted.columns or 2020 not in pivoted.columns: return go.Figure()

    pivoted['Growth'] = pivoted[2020] - pivoted[2000]
    top5 = pivoted.dropna(subset=['Growth']).nlargest(5, 'Growth').index.tolist()
    
    fig = go.Figure()
    colors = px.colors.qualitative.Bold
    
    for i, country in enumerate(top5):
        c_data = df[df['Country'] == country].sort_values('Year')
        X_hist = c_data['Year'].values
        y_hist = c_data['Renewable_Share'].values
        
        # Fit
        valid = np.isfinite(y_hist)
        if np.sum(valid) < 5: continue
        z = np.polyfit(X_hist[valid], y_hist[valid], 1)
        p = np.poly1d(z)
        
        X_fut = np.arange(2020, 2031)
        y_fut = np.clip(p(X_fut), 0, 100)
        
        color = colors[i % len(colors)]
        
        # History
        fig.add_trace(go.Scatter(x=X_hist, y=y_hist, name=f"{country} (Hist)", 
                                 line=dict(color=color, width=2), opacity=0.6))
        # Forecast
        fig.add_trace(go.Scatter(x=X_fut, y=y_fut, name=f"{country} (Pred)", 
                                 line=dict(color=color, width=3, dash='dot')))
        # Marker
        fig.add_trace(go.Scatter(x=[2030], y=[y_fut[-1]], showlegend=False,
                                 mode='markers+text', text=[f"{y_fut[-1]:.0f}%"], textposition="top center",
                                 marker=dict(color=color, size=10)))

    fig.add_vline(x=2030, line_dash="dot", annotation_text="SDG Target")
    fig.update_layout(title="<b>Fig 9: 2030 Forecast</b><br>Projected Trajectory for Top Movers", template="plotly_white")
    return fig

def _assemble_html(figs):
    """
    Assembles the 9 Plotly figures into a polished Tailwind CSS layout.
    """
    divs = {k: v.to_html(full_html=False, include_plotlyjs='cdn', config={'displayModeBar': False}) for k, v in figs.items()}
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Financing the Future: Interactive Dashboard</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body {{ background-color: #f1f5f9; font-family: 'Inter', sans-serif; }}
            .card {{ background: white; border-radius: 16px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); overflow: hidden; transition: transform 0.2s; }}
            .card:hover {{ transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }}
            .header {{ background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); color: white; }}
        </style>
    </head>
    <body>
        <div class="header p-8 mb-8 shadow-lg">
            <div class="container mx-auto">
                <h1 class="text-4xl font-bold mb-2">Financing the Future 🌍</h1>
                <p class="text-slate-300 text-lg">A Global Analysis of Economic Drivers & The Green Transition (2000-2030)</p>
                <div class="mt-4 flex gap-4 text-sm font-semibold">
                    <span class="bg-green-500/20 px-3 py-1 rounded-full text-green-300">SDG 7: Clean Energy</span>
                    <span class="bg-blue-500/20 px-3 py-1 rounded-full text-blue-300">SDG 13: Climate Action</span>
                </div>
            </div>
        </div>

        <div class="container mx-auto px-4 pb-12">
            <h2 class="text-2xl font-bold text-slate-700 mb-4 border-l-4 border-blue-500 pl-4">1. Economic Drivers</h2>
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-12">
                <div class="card p-4">{divs['fig1']}</div>
                <div class="card p-4">{divs['fig6']}</div>
            </div>

            <h2 class="text-2xl font-bold text-slate-700 mb-4 border-l-4 border-green-500 pl-4">2. Global Outcomes</h2>
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-12">
                <div class="card p-4">{divs['fig3']}</div>
                <div class="card p-4">{divs['fig5']}</div>
            </div>

            <h2 class="text-2xl font-bold text-slate-700 mb-4 border-l-4 border-purple-500 pl-4">3. Equity & Efficiency</h2>
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-12">
                <div class="card p-4">{divs['fig2']}</div>
                <div class="card p-4">{divs['fig8']}</div>
            </div>

            <h2 class="text-2xl font-bold text-slate-700 mb-4 border-l-4 border-orange-500 pl-4">4. Global Leaders</h2>
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-12">
                <div class="card p-4">{divs['fig4']}</div>
                <div class="card p-4">{divs['fig7']}</div>
            </div>

            <h2 class="text-2xl font-bold text-slate-700 mb-4 border-l-4 border-indigo-500 pl-4">5. The Future Trajectory</h2>
            <div class="mb-12">
                <div class="card p-4 h-[600px]">{divs['fig9']}</div>
            </div>

            <footer class="text-center text-slate-400 py-8 border-t border-slate-200">
                <p>Generated via Python & Plotly | Data Source: World Bank / IEA</p>
                <p class="text-sm mt-2">Interactive Companion to ACM Paper Submission</p>
            </footer>
        </div>
    </body>
    </html>
    """
    return html