# filename: interactive_dashboard.py
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

def generate_interactive_dashboard(df):
    print("Generating interactive dashboard...")
    
    # Generate Plotly Figures
    fig1 = _map_renewables(df)
    fig2 = _scatter_decoupling(df)
    fig3 = _dual_axis_funding(df)
    fig4 = _bar_top_movers(df)

    # Save to HTML
    _save_html(fig1, fig2, fig3, fig4)
    print("Dashboard saved to figures/interactive_dashboard.html")

def _map_renewables(df):
    df_2020 = df[df['Year'] == 2020]
    return px.choropleth(df_2020, locations="Country", locationmode='country names',
                         color="Renewable_Share", title="Global Renewable Share (2020)",
                         color_continuous_scale="Viridis")

def _scatter_decoupling(df):
    # Filter for valid data to avoid 'NaN' size error
    clean = df.dropna(subset=['GDP_Capita', 'CO2_Total_kt', 'Access_Electricity'])
    clean = clean[clean['Access_Electricity'] > 0] # Avoid size=0
    
    return px.scatter(clean, x="GDP_Capita", y="CO2_Total_kt",
                      animation_frame="Year", animation_group="Country",
                      size="Access_Electricity", color="Country",
                      hover_name="Country", log_x=True, log_y=True,
                      title="Decoupling Analysis: GDP vs CO2 (Size=Elec Access)")

def _dual_axis_funding(df):
    annual = df.groupby('Year').agg({'Financial_Flows': 'sum', 'Renewable_Capacity': 'mean'}).reset_index()
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=annual['Year'], y=annual['Financial_Flows'], name="Financial Aid ($)"), secondary_y=False)
    fig.add_trace(go.Scatter(x=annual['Year'], y=annual['Renewable_Capacity'], name="Renewable Capacity", 
                             mode='lines+markers', line=dict(width=3)), secondary_y=True)
    fig.update_layout(title="Drivers: Aid vs Capacity Trends")
    return fig

def _bar_top_movers(df):
    pivoted = df.pivot_table(index='Country', columns='Year', values='Renewable_Share')
    if 2000 in pivoted.columns and 2020 in pivoted.columns:
        pivoted['Growth'] = pivoted[2020] - pivoted[2000]
        top10 = pivoted.nlargest(10, 'Growth').reset_index()
        return px.bar(top10, x='Growth', y='Country', orientation='h', 
                      title="Top 10 Green Movers (2000-2020)", color='Growth')
    else:
        return go.Figure()

def _save_html(fig1, fig2, fig3, fig4):
    html = f"""
    <html>
    <head><title>Energy Transition Dashboard</title></head>
    <body style="font-family:sans-serif; background:#f0f2f5; padding:20px;">
        <h1 style="text-align:center;">Financing the Future: Interactive Results</h1>
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:20px;">
            <div style="background:white; padding:15px; border-radius:8px;">{fig1.to_html(full_html=False, include_plotlyjs='cdn')}</div>
            <div style="background:white; padding:15px; border-radius:8px;">{fig2.to_html(full_html=False, include_plotlyjs=False)}</div>
            <div style="background:white; padding:15px; border-radius:8px;">{fig3.to_html(full_html=False, include_plotlyjs=False)}</div>
            <div style="background:white; padding:15px; border-radius:8px;">{fig4.to_html(full_html=False, include_plotlyjs=False)}</div>
        </div>
    </body>
    </html>
    """
    if not os.path.exists('figures'): os.makedirs('figures')
    with open('figures/interactive_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html)