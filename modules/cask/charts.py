"""Chart generation utilities for CASK."""

import plotly.express as px
import plotly.graph_objects as go


def create_architecture_flowchart(output_file: str = "cask_architecture_flowchart.png") -> None:
    """Generate the CASK architecture flowchart image."""
    fig = go.Figure()

    top_positions = [
        (1.5, 5, "Global Cross-Ling\nDB (PUTI)"),
        (2.8, 5, "Ethics & Value\nSystems Index"),
        (4.1, 5, "Cultural Cognition\nFramework"),
        (5.4, 5, "Historical Inst\nSystems"),
        (6.7, 5, "Lang-to-Symbolic\nFusion Layer"),
    ]

    middle_positions = [
        (2.2, 2.8, "Symbolic Vector\nChain Compressor\n(SVCC)"),
        (4.1, 2.8, "GPT Native\nEncoding Layer"),
        (6.0, 2.8, "Agent Simulation\nGen Module\n(L1 Staff Builder)"),
    ]

    bottom_positions = [
        (3.0, 0.8, "Recursive Ethics\nValidator\n(Picard_Delta_3)"),
        (5.2, 0.8, "Full ORION\nSimulation Runtime\n(L1-L2-L3)"),
    ]

    colors = {
        "knowledge": "#1FB8CD",
        "processing": "#FFC185",
        "validation": "#5D878F",
    }

    fig.add_shape(
        type="rect",
        x0=1,
        y0=4.3,
        x1=7.2,
        y1=5.7,
        fillcolor="rgba(31, 184, 205, 0.1)",
        line=dict(color="#13343B", width=3, dash="dash"),
        opacity=0.3,
    )

    def add_component(x: float, y: float, text: str, color: str, width: float = 1.2, height: float = 0.8) -> None:
        fig.add_shape(
            type="rect",
            x0=x - width / 2,
            y0=y - height / 2,
            x1=x + width / 2,
            y1=y + height / 2,
            fillcolor=color,
            line=dict(color="black", width=2),
            opacity=0.9,
        )
        fig.add_annotation(
            x=x,
            y=y,
            text=text,
            showarrow=False,
            font=dict(size=11, color="black", family="Arial"),
            align="center",
        )

    for x, y, text in top_positions:
        add_component(x, y, text, colors["knowledge"], width=1.1, height=0.8)
    for x, y, text in middle_positions:
        add_component(x, y, text, colors["processing"], width=1.3, height=1.0)
    for x, y, text in bottom_positions:
        add_component(x, y, text, colors["validation"], width=1.4, height=0.8)

    arrow_connections = [
        [(1.5, 4.6), (2.2, 3.3)],
        [(2.8, 4.6), (2.2, 3.3)],
        [(4.1, 4.6), (4.1, 3.3)],
        [(5.4, 4.6), (6.0, 3.3)],
        [(6.7, 4.6), (6.0, 3.3)],
        [(2.2, 2.3), (3.0, 1.3)],
        [(4.1, 2.3), (3.0, 1.3)],
        [(4.1, 2.3), (5.2, 1.3)],
        [(6.0, 2.3), (5.2, 1.3)],
    ]

    for start, end in arrow_connections:
        fig.add_annotation(
            x=end[0],
            y=end[1],
            ax=start[0],
            ay=start[1],
            arrowhead=2,
            arrowsize=1.2,
            arrowwidth=4,
            arrowcolor="#13343B",
            showarrow=True,
        )

    fig.add_annotation(
        x=4.1,
        y=6.3,
        text="CASK Knowledge Core",
        showarrow=False,
        font=dict(size=14, color="#13343B", family="Arial Bold"),
        align="center",
    )

    fig.add_annotation(
        x=0.2,
        y=5,
        text="Knowledge<br>Storage",
        showarrow=False,
        font=dict(size=10, color="#13343B", family="Arial Bold"),
        align="center",
    )
    fig.add_annotation(
        x=0.2,
        y=2.8,
        text="Processing<br>Layer",
        showarrow=False,
        font=dict(size=10, color="#13343B", family="Arial Bold"),
        align="center",
    )
    fig.add_annotation(
        x=0.2,
        y=0.8,
        text="Validation &<br>Runtime",
        showarrow=False,
        font=dict(size=10, color="#13343B", family="Arial Bold"),
        align="center",
    )

    fig.update_layout(
        title={"text": "CASK Technical Architecture", "x": 0.5, "xanchor": "center", "font": {"size": 18, "family": "Arial Black"}},
        showlegend=False,
        xaxis=dict(range=[0, 9], showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(range=[0, 6.8], showgrid=False, showticklabels=False, zeroline=False),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    fig.write_image(output_file, width=1200, height=800, scale=2)


def create_research_landscape_chart(output_file: str = "cask_research_landscape.png") -> None:
    """Generate the research landscape bubble chart."""
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
        {"name": "Cross-Cultural", "technical_maturity": 4, "cultural_awareness": 8, "complexity": "Medium", "category": "Emerging Tech"},
    ]
    df = pd.DataFrame(data)
    complexity_map = {"Low": 10, "Medium": 20, "High": 30, "Very High": 40}
    df["size"] = df["complexity"].map(complexity_map)
    color_map = {"Current Systems": "#1FB8CD", "Emerging Tech": "#FFC185", "Proposed CASK": "#ECEBD5"}
    fig = go.Figure()
    for category in df["category"].unique():
        cdata = df[df["category"] == category]
        fig.add_trace(
            go.Scatter(
                x=cdata["technical_maturity"],
                y=cdata["cultural_awareness"],
                mode="markers+text",
                marker=dict(size=cdata["size"], color=color_map[category], line=dict(width=2, color="white")),
                text=cdata["name"],
                textposition="middle center",
                textfont=dict(size=10, color="black"),
                name=category,
                cliponaxis=False,
            )
        )
    fig.update_layout(
        title="Cultural AI Research Landscape",
        xaxis_title="Tech Maturity",
        yaxis_title="Cultural Awareness",
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5),
        showlegend=True,
    )
    fig.update_xaxes(range=[0, 10], dtick=2)
    fig.update_yaxes(range=[0, 10], dtick=2)
    fig.write_image(output_file)


def create_project_gantt_chart(output_file: str = "cask_gantt_chart.png") -> None:
    """Generate the project timeline Gantt chart."""
    tasks = [
        {"task": "Core Ling DB", "start": 1, "end": 12, "phase": "Phase 1: Found"},
        {"task": "Cultural Param", "start": 6, "end": 15, "phase": "Phase 1: Found"},
        {"task": "Prototype Trans", "start": 10, "end": 18, "phase": "Phase 1: Found"},
        {"task": "Advisory Ptnrs", "start": 1, "end": 18, "phase": "Phase 1: Found"},
        {"task": "Symbol Fusion", "start": 19, "end": 30, "phase": "Phase 2: Integ"},
        {"task": "SVCC Compress", "start": 24, "end": 33, "phase": "Phase 2: Integ"},
        {"task": "GPT Optimize", "start": 30, "end": 36, "phase": "Phase 2: Integ"},
        {"task": "Agent Generate", "start": 33, "end": 36, "phase": "Phase 2: Integ"},
        {"task": "Ethics Valid", "start": 37, "end": 45, "phase": "Phase 3: Ethics"},
        {"task": "Bias Detection", "start": 42, "end": 48, "phase": "Phase 3: Ethics"},
        {"task": "Circuit Break", "start": 45, "end": 48, "phase": "Phase 3: Ethics"},
        {"task": "Ethics Test", "start": 46, "end": 48, "phase": "Phase 3: Ethics"},
        {"task": "L1-L2-L3 Arch", "start": 49, "end": 57, "phase": "Phase 4: Sim"},
        {"task": "Cultural Integ", "start": 54, "end": 60, "phase": "Phase 4: Sim"},
        {"task": "Large Testing", "start": 58, "end": 60, "phase": "Phase 4: Sim"},
        {"task": "Perf Optimize", "start": 58, "end": 60, "phase": "Phase 4: Sim"},
        {"task": "Cultural Valid", "start": 61, "end": 72, "phase": "Phase 5: Deploy"},
        {"task": "Perf Optimize", "start": 66, "end": 78, "phase": "Phase 5: Deploy"},
        {"task": "Security Test", "start": 72, "end": 81, "phase": "Phase 5: Deploy"},
        {"task": "Deploy Prep", "start": 78, "end": 84, "phase": "Phase 5: Deploy"},
    ]
    phase_colors = {
        "Phase 1: Found": "#1FB8CD",
        "Phase 2: Integ": "#FFC185",
        "Phase 3: Ethics": "#ECEBD5",
        "Phase 4: Sim": "#5D878F",
        "Phase 5: Deploy": "#D2BA4C",
    }
    fig = go.Figure()
    for i, task in enumerate(tasks):
        duration = task["end"] - task["start"]
        fig.add_trace(
            go.Bar(
                x=[duration],
                y=[task["task"]],
                base=[task["start"]],
                orientation="h",
                name=task["phase"],
                marker_color=phase_colors[task["phase"]],
                hovertemplate=f"<b>{task['task']}</b><br>Months: {task['start']}-{task['end']}<br>Duration: {duration} mo<extra></extra>",
                showlegend=i == 0 or task["phase"] != tasks[i - 1]["phase"],
                cliponaxis=False,
            )
        )
    fig.update_layout(
        title="CASK Project Timeline (84 Months)",
        xaxis_title="Months",
        yaxis_title="Tasks",
        barmode="overlay",
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5),
    )
    fig.update_xaxes(range=[0, 84], dtick=12, tickvals=[0, 12, 24, 36, 48, 60, 72, 84], ticktext=["0", "12", "24", "36", "48", "60", "72", "84"])
    fig.update_yaxes(autorange="reversed")
    fig.write_image(output_file)
