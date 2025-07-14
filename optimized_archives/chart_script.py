import plotly.graph_objects as go
import plotly.io as pio

# Create figure
fig = go.Figure()

# Define positions for components with better alignment and spacing
# Top level - CASK Knowledge Core components (evenly spaced within core box)
top_positions = [
    (1.5, 5, "Global Cross-Ling\nDB (PUTI)"),
    (2.8, 5, "Ethics & Value\nSystems Index"),
    (4.1, 5, "Cultural Cognition\nFramework"),
    (5.4, 5, "Historical Inst\nSystems"),
    (6.7, 5, "Lang-to-Symbolic\nFusion Layer")
]

# Middle level - Processing layer (evenly spaced)
middle_positions = [
    (2.2, 2.8, "Symbolic Vector\nChain Compressor\n(SVCC)"),
    (4.1, 2.8, "GPT Native\nEncoding Layer"),
    (6.0, 2.8, "Agent Simulation\nGen Module\n(L1 Staff Builder)")
]

# Bottom level - Validation and runtime (evenly spaced)
bottom_positions = [
    (3.0, 0.8, "Recursive Ethics\nValidator\n(Picard_Delta_3)"),
    (5.2, 0.8, "Full ORION\nSimulation Runtime\n(L1-L2-L3)")
]

# Colors for different component types
colors = {
    'knowledge': '#1FB8CD',  # Strong cyan for knowledge storage
    'processing': '#FFC185',  # Light orange for processing
    'validation': '#5D878F'   # Darker cyan for validation/runtime
}

# Add the main CASK Knowledge Core container box
fig.add_shape(
    type="rect",
    x0=1, y0=4.3,
    x1=7.2, y1=5.7,
    fillcolor="rgba(31, 184, 205, 0.1)",  # Very light cyan background
    line=dict(color="#13343B", width=3, dash="dash"),
    opacity=0.3
)

# Add shapes and text for each component
def add_component(x, y, text, color, width=1.2, height=0.8):
    # Add rectangle shape
    fig.add_shape(
        type="rect",
        x0=x-width/2, y0=y-height/2,
        x1=x+width/2, y1=y+height/2,
        fillcolor=color,
        line=dict(color="black", width=2),
        opacity=0.9
    )
    
    # Add text with good contrast
    fig.add_annotation(
        x=x, y=y,
        text=text,
        showarrow=False,
        font=dict(size=11, color="black", family="Arial"),
        align="center"
    )

# Add all components with consistent sizing
# Top level components
for x, y, text in top_positions:
    add_component(x, y, text, colors['knowledge'], width=1.1, height=0.8)

# Middle level components  
for x, y, text in middle_positions:
    add_component(x, y, text, colors['processing'], width=1.3, height=1.0)

# Bottom level components
for x, y, text in bottom_positions:
    add_component(x, y, text, colors['validation'], width=1.4, height=0.8)

# Add clear arrows showing data flow
arrow_connections = [
    # From knowledge core to processing layer
    [(1.5, 4.6), (2.2, 3.3)],   # Global DB to SVCC
    [(2.8, 4.6), (2.2, 3.3)],   # Ethics to SVCC
    [(4.1, 4.6), (4.1, 3.3)],   # Cultural Cog to GPT (direct)
    [(5.4, 4.6), (6.0, 3.3)],   # Historical to Agent Sim
    [(6.7, 4.6), (6.0, 3.3)],   # Lang-Symbolic to Agent Sim
    
    # From processing to validation/runtime
    [(2.2, 2.3), (3.0, 1.3)],   # SVCC to Ethics Validator
    [(4.1, 2.3), (3.0, 1.3)],   # GPT to Ethics Validator
    [(4.1, 2.3), (5.2, 1.3)],   # GPT to ORION Runtime
    [(6.0, 2.3), (5.2, 1.3)]    # Agent Sim to ORION Runtime
]

# Add prominent arrows with better visibility
for start, end in arrow_connections:
    fig.add_annotation(
        x=end[0], y=end[1],
        ax=start[0], ay=start[1],
        arrowhead=2,
        arrowsize=1.2,
        arrowwidth=4,
        arrowcolor="#13343B",
        showarrow=True
    )

# Add main title
fig.add_annotation(
    x=4.1, y=6.3,
    text="CASK Knowledge Core",
    showarrow=False,
    font=dict(size=14, color="#13343B", family="Arial Bold"),
    align="center"
)

# Add layer labels with better positioning (further from boxes)
fig.add_annotation(
    x=0.2, y=5,
    text="Knowledge<br>Storage",
    showarrow=False,
    font=dict(size=10, color="#13343B", family="Arial Bold"),
    align="center"
)

fig.add_annotation(
    x=0.2, y=2.8,
    text="Processing<br>Layer",
    showarrow=False,
    font=dict(size=10, color="#13343B", family="Arial Bold"),
    align="center"
)

fig.add_annotation(
    x=0.2, y=0.8,
    text="Validation &<br>Runtime",
    showarrow=False,
    font=dict(size=10, color="#13343B", family="Arial Bold"),
    align="center"
)

# Add legend
legend_y_start = 4.0
legend_items = [
    ("Knowledge Storage", colors['knowledge']),
    ("Processing", colors['processing']),
    ("Validation/Runtime", colors['validation'])
]

fig.add_annotation(
    x=7.8, y=4.2,
    text="Component Types:",
    showarrow=False,
    font=dict(size=11, color="#13343B", family="Arial Bold"),
    align="left"
)

for i, (label, color) in enumerate(legend_items):
    y_pos = legend_y_start - (i * 0.4)
    
    # Add colored rectangle for legend
    fig.add_shape(
        type="rect",
        x0=7.8, y0=y_pos-0.1,
        x1=8.0, y1=y_pos+0.1,
        fillcolor=color,
        line=dict(color="black", width=1),
        opacity=0.9
    )
    
    # Add legend text
    fig.add_annotation(
        x=8.1, y=y_pos,
        text=label,
        showarrow=False,
        font=dict(size=10, color="#13343B"),
        align="left"
    )

# Update layout
fig.update_layout(
    title={
        'text': "CASK Technical Architecture",
        'x': 0.5,
        'xanchor': 'center',
        'font': {'size': 18, 'family': 'Arial Black'}
    },
    showlegend=False,
    xaxis=dict(
        range=[0, 9],
        showgrid=False,
        showticklabels=False,
        zeroline=False
    ),
    yaxis=dict(
        range=[0, 6.8],
        showgrid=False,
        showticklabels=False,
        zeroline=False
    ),
    plot_bgcolor='white',
    paper_bgcolor='white'
)

# Remove axes
fig.update_xaxes(visible=False)
fig.update_yaxes(visible=False)

# Save the chart
fig.write_image("cask_architecture_flowchart.png", width=1200, height=800, scale=2)
fig.show()