import plotly.graph_objects as go
import numpy as np
import json

# Load the data
data = {
  "quantum_vectors": [
    {
      "id": "qv_1",
      "magnitude": 1.2,
      "phase": 0.5,
      "coherence_time": 1.0,
      "position": [0, 0, 0],
      "entangled_with": ["qv_2"]
    },
    {
      "id": "qv_2", 
      "magnitude": 2.0,
      "phase": 1.57,
      "coherence_time": 0.8,
      "position": [2, 1, 1],
      "entangled_with": ["qv_1"]
    },
    {
      "id": "qv_3",
      "magnitude": 1.5,
      "phase": 3.14,
      "coherence_time": 0.6,
      "position": [1, 2, -1],
      "entangled_with": []
    }
  ],
  "trajectory_waypoints": [
    {"time": 0.0, "magnitude": 1.20, "phase": 0.50, "coherence": 1.0},
    {"time": 0.1, "magnitude": 1.23, "phase": 0.67, "coherence": 0.99},
    {"time": 0.2, "magnitude": 1.26, "phase": 0.85, "coherence": 0.98},
    {"time": 0.5, "magnitude": 1.35, "phase": 1.57, "coherence": 0.95},
    {"time": 0.8, "magnitude": 1.44, "phase": 2.30, "coherence": 0.92},
    {"time": 1.0, "magnitude": 1.50, "phase": 3.14, "coherence": 0.90}
  ],
  "superposition_states": [
    {"state_id": "coherent", "probability": 0.7, "stability": 0.9},
    {"state_id": "decoherent", "probability": 0.3, "stability": 0.4}
  ],
  "control_parameters": {
    "flight_altitude": 10000,
    "velocity": 250,
    "trajectory_type": "spiral_ascent",
    "phase_lock": True,
    "entanglement_strength": 0.85
  }
}

fig = go.Figure()

# Brand colors for different elements
colors = ['#1FB8CD', '#DB4545', '#2E8B57', '#5D878F', '#D2BA4C']

# 1. Add quantum vectors as cones (arrows)
for i, qv in enumerate(data["quantum_vectors"]):
    x, y, z = qv["position"]
    
    # Convert phase to direction components
    u = qv["magnitude"] * np.cos(qv["phase"]) * 0.5
    v = qv["magnitude"] * np.sin(qv["phase"]) * 0.5  
    w = qv["magnitude"] * 0.3
    
    # Color based on coherence time (opacity for decay)
    opacity = qv["coherence_time"]
    
    fig.add_trace(go.Cone(
        x=[x], y=[y], z=[z],
        u=[u], v=[v], w=[w],
        colorscale=[[0, colors[i]], [1, colors[i]]],
        showscale=False,
        sizemode="absolute",
        sizeref=0.3,
        opacity=opacity,
        name=f"QV{i+1}",
        hovertemplate=f"Mag: {qv['magnitude']:.2f}<br>Phase: {qv['phase']:.2f}<br>Coherence: {qv['coherence_time']:.2f}<extra></extra>"
    ))

# 2. Add entanglement connections
for qv in data["quantum_vectors"]:
    if qv["entangled_with"]:
        x1, y1, z1 = qv["position"]
        for entangled_id in qv["entangled_with"]:
            # Find the entangled vector
            for other_qv in data["quantum_vectors"]:
                if other_qv["id"] == entangled_id:
                    x2, y2, z2 = other_qv["position"]
                    
                    # Create curved connection using parametric curve
                    t = np.linspace(0, 1, 20)
                    mid_x = (x1 + x2) / 2
                    mid_y = (y1 + y2) / 2 + 0.5  # Curve upward
                    mid_z = (z1 + z2) / 2
                    
                    # Bezier-like curve
                    curve_x = (1-t)**2 * x1 + 2*(1-t)*t * mid_x + t**2 * x2
                    curve_y = (1-t)**2 * y1 + 2*(1-t)*t * mid_y + t**2 * y2
                    curve_z = (1-t)**2 * z1 + 2*(1-t)*t * mid_z + t**2 * z2
                    
                    fig.add_trace(go.Scatter3d(
                        x=curve_x, y=curve_y, z=curve_z,
                        mode='lines',
                        line=dict(color='#5D878F', width=4, dash='dash'),
                        name='Entanglement',
                        opacity=0.7,
                        showlegend=False,
                        hovertemplate="Entanglement Bond<extra></extra>"
                    ))

# 3. Add trajectory path with waypoints
waypoints = data["trajectory_waypoints"]
times = [wp["time"] for wp in waypoints]
magnitudes = [wp["magnitude"] for wp in waypoints]
phases = [wp["phase"] for wp in waypoints]
coherences = [wp["coherence"] for wp in waypoints]

# Create trajectory path in 3D space based on time and phase
traj_x = [t * 2 for t in times]
traj_y = [np.sin(phase) * mag * 0.5 for phase, mag in zip(phases, magnitudes)]
traj_z = [np.cos(phase) * mag * 0.5 for phase, mag in zip(phases, magnitudes)]

# Trajectory line with coherence decay as opacity
fig.add_trace(go.Scatter3d(
    x=traj_x, y=traj_y, z=traj_z,
    mode='lines+markers',
    line=dict(color='#D2BA4C', width=6),
    marker=dict(
        size=[c * 8 for c in coherences],
        color=coherences,
        colorscale='Viridis',
        showscale=True,
        colorbar=dict(title="Coherence", len=0.3, y=0.7)
    ),
    name='Trajectory',
    opacity=0.8,
    hovertemplate="Time: %{text}<br>Coherence: %{marker.color:.2f}<extra></extra>",
    text=[f"{t:.1f}s" for t in times]
))

# 4. Add superposition states as ghosted overlays
for i, state in enumerate(data["superposition_states"]):
    # Create overlaid versions of quantum vectors for superposition
    for j, qv in enumerate(data["quantum_vectors"][:2]):  # Only show for first 2 vectors
        x, y, z = qv["position"]
        offset = 0.2 * (i - 0.5)  # Slight offset for visibility
        
        fig.add_trace(go.Scatter3d(
            x=[x + offset], y=[y + offset], z=[z + offset],
            mode='markers',
            marker=dict(
                size=qv["magnitude"] * 10 * state["probability"],
                color=colors[j],
                opacity=state["stability"] * 0.3,
                symbol='diamond' if state["state_id"] == "coherent" else 'square'
            ),
            name=f'Super {state["state_id"][:8]}',
            showlegend=i == 0,
            hovertemplate=f"State: {state['state_id']}<br>Prob: {state['probability']:.1f}<extra></extra>"
        ))

# 5. Add coordinate system reference
axis_length = 1.5
for axis, color, direction in zip(['X', 'Y', 'Z'], ['red', 'green', 'blue'], 
                                 [[axis_length,0,0], [0,axis_length,0], [0,0,axis_length]]):
    fig.add_trace(go.Scatter3d(
        x=[0, direction[0]], y=[0, direction[1]], z=[0, direction[2]],
        mode='lines',
        line=dict(color=color, width=3),
        name=f'{axis}-axis',
        showlegend=False,
        hoverinfo='skip'
    ))

# Update layout with scientific styling
fig.update_layout(
    title="Quantum Vector Field Visualization",
    scene=dict(
        xaxis_title="X Position",
        yaxis_title="Y Position", 
        zaxis_title="Z Position",
        bgcolor='rgba(0,0,0,0.1)',
        xaxis=dict(showbackground=True, backgroundcolor='rgba(0,0,0,0.1)'),
        yaxis=dict(showbackground=True, backgroundcolor='rgba(0,0,0,0.1)'),
        zaxis=dict(showbackground=True, backgroundcolor='rgba(0,0,0,0.1)'),
        aspectmode='cube'
    ),
    legend=dict(orientation='h', yanchor='bottom', y=1.05, xanchor='center', x=0.5)
)

# Save as both PNG and SVG
fig.write_image("quantum_vector_field.png")
fig.write_image("quantum_vector_field.svg", format="svg")

fig.show()