# filename: interactive_dashboard.py
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

def generate_interactive_dashboard(df):
    print("Generating interactive dashboard...")
    
    # 1. Create Figures
    fig_map = _create_map(df)
    fig_funding = _create_funding_trend(df) # New
    fig_decouple = _create_decoupling_bubble(df) # New Focus
    fig_compare = _create_country_comparison(df)

    # 2. Assemble HTML
    html_content = _assemble_html(fig_map, fig_funding, fig_decouple, fig_compare)
    
    with open('figures/interactive_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("Dashboard saved to figures/interactive_dashboard.html")

def _create_map(df):
    """Global Map: Renewable Share."""
    df_2020 = df[df['Year'] == 2020]
    fig = px.choropleth(df_2020, locations="Country", locationmode='country names',
                        color="Renewable_Share",
                        title="Global Renewable Energy Share (2020)",
                        color_continuous_scale="Tealgrn")
    fig.update_layout(margin=dict(l=0, r=0, t=50, b=0))
    return fig

def _create_funding_trend(df):
    """Dual Axis: Money vs Capacity."""
    annual = df.groupby('Year').agg({'Financial_Flows': 'sum', 'Renewable_Capacity': 'mean'}).reset_index()
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Bars for Money
    fig.add_trace(go.Bar(x=annual['Year'], y=annual['Financial_Flows'], name="Financial Aid ($)", marker_color='#85bb65'),
                  secondary_y=False)
    
    # Line for Capacity
    fig.add_trace(go.Scatter(x=annual['Year'], y=annual['Renewable_Capacity'], name="Renewable Capacity", 
                             mode='lines+markers', line=dict(color='#2c3e50', width=3)),
                  secondary_y=True)
    
    fig.update_layout(title="Drivers: Financial Aid vs. Renewable Capacity Growth")
    fig.update_yaxes(title_text="Financial Flows (USD)", secondary_y=False)
    fig.update_yaxes(title_text="Capacity (W/capita)", secondary_y=True)
    return fig

def _create_decoupling_bubble(df):
    """Animated Bubble: GDP vs CO2."""
    # Filter out 0s for log scale
    df_clean = df[(df['GDP_Capita'] > 0) & (df['CO2_Total_kt'] > 0)].copy()
    
    fig = px.scatter(df_clean, x="GDP_Capita", y="CO2_Total_kt",
                     animation_frame="Year", animation_group="Country",
                     size="Access_Electricity", color="Country",
                     hover_name="Country", log_x=True, log_y=True,
                     title="Decoupling Path: GDP Growth vs. CO2 Emissions (Size = Elec Access)",
                     labels={'GDP_Capita': 'GDP per Capita (Log)', 'CO2_Total_kt': 'CO2 Emissions (Log)'})
    return fig

def _create_country_comparison(df):
    """Compare key nations on Green Metrics."""
    top_countries = ['China', 'India', 'United States', 'Germany', 'Brazil']
    df_sub = df[df['Country'].isin(top_countries)].sort_values('Year')
    
    fig = px.line(df_sub, x='Year', y='Renewable_Share', color='Country',
                  title="Comparison: Renewable Energy Share (%)")
    return fig

def _assemble_html(fig_map, fig_funding, fig_decouple, fig_compare):
    # Minimalist HTML assembly
    div_map = fig_map.to_html(full_html=False, include_plotlyjs='cdn')
    div_funding = fig_funding.to_html(full_html=False, include_plotlyjs=False)
    div_decouple = fig_decouple.to_html(full_html=False, include_plotlyjs=False)
    div_compare = fig_compare.to_html(full_html=False, include_plotlyjs=False)

    return f"""
    <html>
    <head><title>Financing the Future Dashboard</title></head>
    <body style="font-family: sans-serif; background: #f4f4f9; padding: 20px;">
        <h1 style="text-align:center;">Financing the Future: Green Transition Drivers</h1>
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 20px;">
            <div style="background:white; padding:15px; border-radius:10px;">{div_map}</div>
            <div style="background:white; padding:15px; border-radius:10px;">{div_funding}</div>
            <div style="background:white; padding:15px; border-radius:10px;">{div_decouple}</div>
            <div style="background:white; padding:15px; border-radius:10px;">{div_compare}</div>
        </div>
    </body>
    </html>
    """