import plotly.graph_objects as go
import plotly.io as pio

# Define the data for the Gantt chart
tasks = [
    # Phase 1: Foundation
    {"task": "Core Ling DB", "start": 1, "end": 12, "phase": "Phase 1: Found"},
    {"task": "Cultural Param", "start": 6, "end": 15, "phase": "Phase 1: Found"},
    {"task": "Prototype Trans", "start": 10, "end": 18, "phase": "Phase 1: Found"},
    {"task": "Advisory Ptnrs", "start": 1, "end": 18, "phase": "Phase 1: Found"},
    
    # Phase 2: Integration
    {"task": "Symbol Fusion", "start": 19, "end": 30, "phase": "Phase 2: Integ"},
    {"task": "SVCC Compress", "start": 24, "end": 33, "phase": "Phase 2: Integ"},
    {"task": "GPT Optimize", "start": 30, "end": 36, "phase": "Phase 2: Integ"},
    {"task": "Agent Generate", "start": 33, "end": 36, "phase": "Phase 2: Integ"},
    
    # Phase 3: Ethics & Validation
    {"task": "Ethics Valid", "start": 37, "end": 45, "phase": "Phase 3: Ethics"},
    {"task": "Bias Detection", "start": 42, "end": 48, "phase": "Phase 3: Ethics"},
    {"task": "Circuit Break", "start": 45, "end": 48, "phase": "Phase 3: Ethics"},
    {"task": "Ethics Test", "start": 46, "end": 48, "phase": "Phase 3: Ethics"},
    
    # Phase 4: Simulation Runtime
    {"task": "L1-L2-L3 Arch", "start": 49, "end": 57, "phase": "Phase 4: Sim"},
    {"task": "Cultural Integ", "start": 54, "end": 60, "phase": "Phase 4: Sim"},
    {"task": "Large Testing", "start": 58, "end": 60, "phase": "Phase 4: Sim"},
    {"task": "Perf Optimize", "start": 58, "end": 60, "phase": "Phase 4: Sim"},
    
    # Phase 5: Validation & Deployment
    {"task": "Cultural Valid", "start": 61, "end": 72, "phase": "Phase 5: Deploy"},
    {"task": "Perf Optimize", "start": 66, "end": 78, "phase": "Phase 5: Deploy"},
    {"task": "Security Test", "start": 72, "end": 81, "phase": "Phase 5: Deploy"},
    {"task": "Deploy Prep", "start": 78, "end": 84, "phase": "Phase 5: Deploy"}
]

# Define colors for each phase
phase_colors = {
    "Phase 1: Found": "#1FB8CD",
    "Phase 2: Integ": "#FFC185", 
    "Phase 3: Ethics": "#ECEBD5",
    "Phase 4: Sim": "#5D878F",
    "Phase 5: Deploy": "#D2BA4C"
}

# Create the figure
fig = go.Figure()

# Add bars for each task
for i, task in enumerate(tasks):
    duration = task["end"] - task["start"]
    fig.add_trace(go.Bar(
        x=[duration],
        y=[task["task"]],
        base=[task["start"]],
        orientation='h',
        name=task["phase"],
        marker_color=phase_colors[task["phase"]],
        hovertemplate=f"<b>{task['task']}</b><br>Months: {task['start']}-{task['end']}<br>Duration: {duration} mo<extra></extra>",
        showlegend=i == 0 or task["phase"] != tasks[i-1]["phase"],  # Show legend only for first occurrence of each phase
        cliponaxis=False
    ))

# Update layout
fig.update_layout(
    title="CASK Project Timeline (84 Months)",
    xaxis_title="Months",
    yaxis_title="Tasks",
    barmode='overlay',
    legend=dict(orientation='h', yanchor='bottom', y=1.05, xanchor='center', x=0.5)
)

# Update x-axis
fig.update_xaxes(
    range=[0, 84],
    dtick=12,  # Show ticks every 12 months (1 year)
    tickvals=[0, 12, 24, 36, 48, 60, 72, 84],
    ticktext=["0", "12", "24", "36", "48", "60", "72", "84"]
)

# Update y-axis to reverse order so Phase 1 appears at top
fig.update_yaxes(autorange="reversed")

# Save the chart
fig.write_image("cask_gantt_chart.png")