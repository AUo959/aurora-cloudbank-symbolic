import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Create the data
data = [
    {"name": "GPT-4", "technical_maturity": 8, "cultural_awareness": 3, "complexity": "Medium", "category": "Current Systems"},
    {"name": "Multi-Agent Trans", "technical_maturity": 6, "cultural_awareness": 7, "complexity": "High", "category": "Emerging Tech"},
    {"name": "CAS Score", "technical_maturity": 5, "cultural_awareness": 8, "complexity": "Medium", "category": "Emerging Tech"},
    {"name": "Neuro-Symbolic", "technical_maturity": 6, "cultural_awareness": 4, "complexity": "High", "category": "Emerging Tech"},
    {"name": "Real-time Trans", "technical_maturity": 8, "cultural_awareness": 5, "complexity": "Medium", "category": "Current Systems"},
    {"name": "Agent Modeling", "technical_maturity": 7, "cultural_awareness": 2, "complexity": "Low", "category": "Emerging Tech"},
    {"name": "Vector Symbolic", "technical_maturity": 5, "cultural_awareness": 3, "complexity": "High", "category": "Emerging Tech"},
    {"name": "CASK System", "technical_maturity": 3, "cultural_awareness": 9, "complexity": "Very High", "category": "Proposed CASK"},
    {"name": "Ethical AI", "technical_maturity": 6, "cultural_awareness": 4, "complexity": "Medium", "category": "Current Systems"},
    {"name": "Cross-Cultural", "technical_maturity": 4, "cultural_awareness": 8, "complexity": "Medium", "category": "Emerging Tech"}
]

df = pd.DataFrame(data)

# Map complexity to bubble sizes
complexity_map = {"Low": 10, "Medium": 20, "High": 30, "Very High": 40}
df['size'] = df['complexity'].map(complexity_map)

# Define colors for categories using the specified palette
color_map = {
    "Current Systems": "#1FB8CD",
    "Emerging Tech": "#FFC185", 
    "Proposed CASK": "#ECEBD5"
}

# Create the bubble chart
fig = go.Figure()

for category in df['category'].unique():
    category_data = df[df['category'] == category]
    fig.add_trace(go.Scatter(
        x=category_data['technical_maturity'],
        y=category_data['cultural_awareness'], 
        mode='markers+text',
        marker=dict(
            size=category_data['size'],
            color=color_map[category],
            line=dict(width=2, color='white')
        ),
        text=category_data['name'],
        textposition='middle center',
        textfont=dict(size=10, color='black'),
        name=category,
        cliponaxis=False
    ))

# Update layout
fig.update_layout(
    title="Cultural AI Research Landscape",
    xaxis_title="Tech Maturity",
    yaxis_title="Cultural Aware",
    legend=dict(orientation='h', yanchor='bottom', y=1.05, xanchor='center', x=0.5),
    showlegend=True
)

# Update axes - removed cliponaxis parameter
fig.update_xaxes(range=[0, 10], dtick=2)
fig.update_yaxes(range=[0, 10], dtick=2)

# Save the chart
fig.write_image("cask_research_landscape.png")