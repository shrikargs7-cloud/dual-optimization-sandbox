"""
Dual-Optimization Sandbox (Descent vs. Ascent)
Interactive Educational Dashboard & Simulation Engine in Pure NumPy & Streamlit.

Visualizes the operational duality between Gradient Descent (minimizing a loss landscape)
and Gradient Ascent (maximizing an objective landscape) on the exact same coordinate system.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from engine import OptimizationEngine, OptimizationMode, TerminationStatus
from landscapes import LANDSCAPES, Landscape


# -----------------------------------------------------------------------------
# Streamlit Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Dual-Optimization Sandbox",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -----------------------------------------------------------------------------
# Session State Initialization
# -----------------------------------------------------------------------------
def init_session_state():
    if "theme" not in st.session_state:
        st.session_state.theme = "Light"
    if "selected_landscape_id" not in st.session_state:
        st.session_state.selected_landscape_id = "bowl"
    if "start_x" not in st.session_state:
        st.session_state.start_x = LANDSCAPES["bowl"].default_start[0]
    if "start_y" not in st.session_state:
        st.session_state.start_y = LANDSCAPES["bowl"].default_start[1]


init_session_state()


# -----------------------------------------------------------------------------
# Panel 1: Left Control Panel (Sidebar)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🎛️ Optimization Controls")

    # Theme Toggle (Default: Light)
    theme_choice = st.radio(
        "Display Theme",
        options=["Light", "Dark"],
        index=0 if st.session_state.theme == "Light" else 1,
        horizontal=True,
        help="Select user interface appearance mode.",
    )
    st.session_state.theme = theme_choice
    is_light = st.session_state.theme == "Light"

    st.markdown("---")

    # 1. Landscape selection
    landscape_options = {
        "bowl": "Symmetric Bowl (Paraboloid)",
        "rosenbrock": "Rosenbrock Valley (Banana)",
        "ackley": "Ackley's Multimodal Surface",
        "saddle": "Hyperbolic Saddle Point",
    }

    current_landscape_id = st.selectbox(
        "Mathematical Landscape",
        options=list(landscape_options.keys()),
        format_func=lambda k: landscape_options[k],
        index=list(landscape_options.keys()).index(st.session_state.selected_landscape_id),
        help="Select multi-dimensional surface topology.",
    )

    # Reset coordinates if landscape changed
    if current_landscape_id != st.session_state.selected_landscape_id:
        st.session_state.selected_landscape_id = current_landscape_id
        default_pt = LANDSCAPES[current_landscape_id].default_start
        st.session_state.start_x = default_pt[0]
        st.session_state.start_y = default_pt[1]
        st.rerun()

    active_landscape: Landscape = LANDSCAPES[current_landscape_id]

    st.markdown("---")
    st.markdown("#### 🎯 Initial Coordinates $\\theta_0 = (x_0, y_0)$")

    col_x, col_y = st.columns(2)
    with col_x:
        start_x = st.number_input(
            "Initial X",
            value=float(st.session_state.start_x),
            step=0.1,
            format="%.3f",
            key="input_start_x",
        )
    with col_y:
        start_y = st.number_input(
            "Initial Y",
            value=float(st.session_state.start_y),
            step=0.1,
            format="%.3f",
            key="input_start_y",
        )

    # Sync back to session state
    st.session_state.start_x = start_x
    st.session_state.start_y = start_y

    # Quick preset button
    if st.button("↺ Reset to Landscape Defaults", use_container_width=True):
        st.session_state.start_x = active_landscape.default_start[0]
        st.session_state.start_y = active_landscape.default_start[1]
        st.rerun()

    st.markdown("---")
    st.markdown("#### ⚙️ Hyperparameters")

    learning_rate = st.slider(
        "Learning Rate (α)",
        min_value=0.001,
        max_value=1.5,
        value=float(active_landscape.default_lr),
        step=0.001,
        format="%.4f",
        help="Step size for vector update along the gradient direction.",
    )

    max_iterations = st.slider(
        "Max Iterations",
        min_value=10,
        max_value=500,
        value=150,
        step=10,
        help="Maximum optimization loop execution limit.",
    )

    with st.expander("🛡️ Advanced Safety Bounds", expanded=False):
        tolerance = st.select_slider(
            "Convergence Tolerance ||∇f|| < ε",
            options=[1e-6, 1e-5, 1e-4, 1e-3, 1e-2],
            value=1e-5,
            format_func=lambda v: f"{v:.1e}",
            help="Halts iteration immediately when gradient length drops below threshold.",
        )
        use_clipping = st.checkbox("Enable Gradient Clipping", value=False)
        clip_threshold = 50.0 if use_clipping else None

    descent_legend_color = "#0284C7" if is_light else "#00F0FF"
    ascent_legend_color = "#E11D48" if is_light else "#FF007A"
    st.markdown("---")
    st.markdown(
        f"""
        <div style="font-size: 0.82rem; color: {'#64748B' if is_light else '#94A3B8'}; line-height: 1.5;">
            <b style="color: {descent_legend_color};">● Cyan/Blue Trail:</b> θ<sub>t+1</sub> = θ<sub>t</sub> - α∇f(θ<sub>t</sub>)<br>
            <b style="color: {ascent_legend_color};">● Magenta/Red Trail:</b> θ<sub>t+1</sub> = θ<sub>t</sub> + α∇f(θ<sub>t</sub>)
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# Dynamic CSS Injection (Light vs. Dark Theme)
# -----------------------------------------------------------------------------
if is_light:
    THEME_CSS = """
    <style>
    /* Clean Light Modern Theme */
    .stApp {
        background-color: #F8FAFC;
        color: #0F172A;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }
    .telemetry-card {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 14px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.05);
    }
    .descent-card {
        border-left: 6px solid #0284C7 !important;
    }
    .ascent-card {
        border-left: 6px solid #E11D48 !important;
    }
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    .badge-converged {
        background: rgba(16, 185, 129, 0.15);
        color: #047857;
        border: 1px solid #10B981;
    }
    .badge-max-iter {
        background: rgba(245, 158, 11, 0.15);
        color: #B45309;
        border: 1px solid #F59E0B;
    }
    .badge-diverged {
        background: rgba(239, 68, 68, 0.15);
        color: #B91C1C;
        border: 1px solid #EF4444;
    }
    .metric-label {
        color: #64748B;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 2px;
    }
    .metric-value {
        color: #0F172A;
        font-size: 1.15rem;
        font-weight: 700;
        font-family: "JetBrains Mono", "SF Mono", Menlo, Consolas, monospace;
    }
    .metric-value-cyan {
        color: #0284C7;
        font-weight: 700;
        font-family: "JetBrains Mono", monospace;
    }
    .metric-value-magenta {
        color: #E11D48;
        font-weight: 700;
        font-family: "JetBrains Mono", monospace;
    }
    .hero-title {
        background: linear-gradient(90deg, #0284C7 0%, #7C3AED 50%, #E11D48 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin-bottom: 0px;
    }
    .hero-sub {
        color: #475569;
        font-size: 0.95rem;
        margin-bottom: 12px;
    }
    </style>
    """
else:
    THEME_CSS = """
    <style>
    /* Dark Cyber Theme */
    .stApp {
        background-color: #0B0E14;
        color: #E2E8F0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    section[data-testid="stSidebar"] {
        background-color: #111622;
        border-right: 1px solid #1E293B;
    }
    .telemetry-card {
        background: #141A29;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 14px;
        border: 1px solid #1E293B;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
    }
    .descent-card {
        border-left: 5px solid #00F0FF !important;
    }
    .ascent-card {
        border-left: 5px solid #FF007A !important;
    }
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    .badge-converged {
        background: rgba(16, 185, 129, 0.2);
        color: #10B981;
        border: 1px solid #10B981;
    }
    .badge-max-iter {
        background: rgba(245, 158, 11, 0.2);
        color: #F59E0B;
        border: 1px solid #F59E0B;
    }
    .badge-diverged {
        background: rgba(239, 68, 68, 0.2);
        color: #EF4444;
        border: 1px solid #EF4444;
    }
    .metric-label {
        color: #94A3B8;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 2px;
    }
    .metric-value {
        color: #F8FAFC;
        font-size: 1.15rem;
        font-weight: 700;
        font-family: "JetBrains Mono", "SF Mono", Menlo, Consolas, monospace;
    }
    .metric-value-cyan {
        color: #00F0FF;
        font-weight: 700;
        font-family: "JetBrains Mono", monospace;
    }
    .metric-value-magenta {
        color: #FF007A;
        font-weight: 700;
        font-family: "JetBrains Mono", monospace;
    }
    .hero-title {
        background: linear-gradient(90deg, #00F0FF 0%, #A855F7 50%, #FF007A 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin-bottom: 0px;
    }
    .hero-sub {
        color: #94A3B8;
        font-size: 0.95rem;
        margin-bottom: 12px;
    }
    </style>
    """
st.markdown(THEME_CSS, unsafe_allow_html=True)


# Theme color palette variables for Plotly charts
if is_light:
    PAPER_BG = "#FFFFFF"
    PLOT_BG = "#F8FAFC"
    GRID_COLOR = "#E2E8F0"
    AXIS_COLOR = "#64748B"
    TEXT_COLOR = "#0F172A"
    LEGEND_BG = "rgba(255, 255, 255, 0.92)"
    LEGEND_BORDER = "#CBD5E1"
    DESC_COLOR = "#0284C7"    # Vivid Cyan/Cerulean
    ASC_COLOR = "#E11D48"     # Vivid Magenta/Crimson
    START_COLOR = "#D97706"   # Deep Amber Star
    CONTOUR_SCALE = "Viridis"
else:
    PAPER_BG = "#0B0E14"
    PLOT_BG = "#111622"
    GRID_COLOR = "#1E293B"
    AXIS_COLOR = "#94A3B8"
    TEXT_COLOR = "#E2E8F0"
    LEGEND_BG = "rgba(17, 22, 34, 0.85)"
    LEGEND_BORDER = "#1E293B"
    DESC_COLOR = "#00F0FF"    # Electric Cyan
    ASC_COLOR = "#FF007A"     # Intense Magenta
    START_COLOR = "#FFE600"   # Bright Yellow Star
    CONTOUR_SCALE = "Viridis"


# -----------------------------------------------------------------------------
# Execute Optimization Backend via Pure NumPy
# -----------------------------------------------------------------------------
engine = OptimizationEngine()
descent_result, ascent_result = engine.run_dual(
    landscape=active_landscape,
    initial_point=(st.session_state.start_x, st.session_state.start_y),
    learning_rate=learning_rate,
    max_iterations=max_iterations,
    tolerance=tolerance,
    clip_gradient=clip_threshold,
)

max_history_len = max(len(descent_result.history), len(ascent_result.history))


# -----------------------------------------------------------------------------
# Application Header
# -----------------------------------------------------------------------------
col_header, col_info = st.columns([2.5, 1.0])
with col_header:
    st.markdown('<div class="hero-title">Dual-Optimization Sandbox</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="hero-sub">Duality simulation of <b>Gradient Descent</b> (Cost Minimization) vs. '
        f'<b>Gradient Ascent</b> (Objective Maximization) on <code>{active_landscape.name}</code>.</div>',
        unsafe_allow_html=True,
    )

with col_info:
    st.latex(active_landscape.formula_latex)


# -----------------------------------------------------------------------------
# Main Visual & Telemetry Layout (Panel 2 & Panel 3)
# -----------------------------------------------------------------------------
col_canvas, col_telemetry = st.columns([1.6, 1.0], gap="large")


# -----------------------------------------------------------------------------
# Panel 2: Center Plot Canvas (Plotly Interactive 2D Contour & 3D Surface)
# -----------------------------------------------------------------------------
with col_canvas:
    # Trajectory playback scrubber
    playback_step = st.slider(
        "Trajectory Playback Step (Scrub to inspect iteration progression)",
        min_value=0,
        max_value=max_history_len - 1,
        value=max_history_len - 1,
        help="Interactive time slider to observe how Descent and Ascent navigate the surface step-by-step.",
    )

    tab_contour, tab_3d = st.tabs(["🗺️ 2D Dual Contour Map", "🏔️ 3D Elevation Surface"])

    # Compute Landscape Grid
    bounds = active_landscape.default_bounds
    # Dynamically expand bounds if trajectories move slightly outside
    all_x = np.concatenate([descent_result.x_coords, ascent_result.x_coords, [bounds[0], bounds[1]]])
    all_y = np.concatenate([descent_result.y_coords, ascent_result.y_coords, [bounds[2], bounds[3]]])
    # Filter inf/nan
    valid_mask = np.isfinite(all_x) & np.isfinite(all_y)
    if valid_mask.any():
        x_min = min(bounds[0], float(np.min(all_x[valid_mask]))) - 0.5
        x_max = max(bounds[1], float(np.max(all_x[valid_mask]))) + 0.5
        y_min = min(bounds[2], float(np.min(all_y[valid_mask]))) - 0.5
        y_max = max(bounds[3], float(np.max(all_y[valid_mask]))) + 0.5
    else:
        x_min, x_max, y_min, y_max = bounds

    # Bound safety clamp so grid generation remains responsive
    x_min, x_max = max(x_min, -20.0), min(x_max, 20.0)
    y_min, y_max = max(y_min, -20.0), min(y_max, 20.0)

    grid_res = 120
    x_grid = np.linspace(x_min, x_max, grid_res)
    y_grid = np.linspace(y_min, y_max, grid_res)
    X, Y = np.meshgrid(x_grid, y_grid)
    Z = active_landscape.evaluate(X, Y)

    # Truncate trajectories up to current playback step
    desc_sub_len = min(playback_step + 1, len(descent_result.history))
    asc_sub_len = min(playback_step + 1, len(ascent_result.history))

    desc_hist = descent_result.history[:desc_sub_len]
    asc_hist = ascent_result.history[:asc_sub_len]

    with tab_contour:
        fig_2d = go.Figure()

        # 1. Base Contour Fill
        fig_2d.add_trace(
            go.Contour(
                x=x_grid,
                y=y_grid,
                z=Z,
                colorscale=CONTOUR_SCALE,
                contours=dict(
                    coloring="fill",
                    showlabels=False,
                ),
                colorbar=dict(
                    title=dict(text="f(x, y)", font=dict(color=AXIS_COLOR)),
                    tickfont=dict(color=AXIS_COLOR),
                    thickness=12,
                    len=0.75,
                ),
                opacity=0.78,
                hoverinfo="x+y+z",
                name="Landscape Contours",
            )
        )

        # 2. Gradient Descent Path: Electric Cyan / Deep Cerulean
        if len(desc_hist) > 0:
            fig_2d.add_trace(
                go.Scatter(
                    x=desc_hist[:, 1],
                    y=desc_hist[:, 2],
                    mode="lines+markers",
                    line=dict(color=DESC_COLOR, width=3.5),
                    marker=dict(
                        color=DESC_COLOR,
                        size=6,
                        symbol="circle",
                        line=dict(color="#000000" if is_light else "#0B0E14", width=1),
                    ),
                    name="Gradient Descent (Minimizing)",
                    customdata=np.stack((desc_hist[:, 0], desc_hist[:, 3], desc_hist[:, 4]), axis=-1),
                    hovertemplate=(
                        "<b>Gradient Descent</b><br>"
                        "Step: %{customdata[0]:.0f}<br>"
                        "X: %{x:.4f}<br>"
                        "Y: %{y:.4f}<br>"
                        "f(x, y): %{customdata[1]:.4e}<br>"
                        "||∇f||: %{customdata[2]:.4e}<extra></extra>"
                    ),
                )
            )

            # Highlight Current / Landing Point
            fig_2d.add_trace(
                go.Scatter(
                    x=[desc_hist[-1, 1]],
                    y=[desc_hist[-1, 2]],
                    mode="markers",
                    marker=dict(
                        color=DESC_COLOR,
                        size=14,
                        symbol="cross",
                        line=dict(color="#FFFFFF", width=2),
                    ),
                    name="Descent Head",
                    showlegend=False,
                    hoverinfo="skip",
                )
            )

        # 3. Gradient Ascent Path: Intense Magenta / Crimson
        if len(asc_hist) > 0:
            fig_2d.add_trace(
                go.Scatter(
                    x=asc_hist[:, 1],
                    y=asc_hist[:, 2],
                    mode="lines+markers",
                    line=dict(color=ASC_COLOR, width=3.5, dash="solid"),
                    marker=dict(
                        color=ASC_COLOR,
                        size=6,
                        symbol="diamond",
                        line=dict(color="#000000" if is_light else "#0B0E14", width=1),
                    ),
                    name="Gradient Ascent (Maximizing)",
                    customdata=np.stack((asc_hist[:, 0], asc_hist[:, 3], asc_hist[:, 4]), axis=-1),
                    hovertemplate=(
                        "<b>Gradient Ascent</b><br>"
                        "Step: %{customdata[0]:.0f}<br>"
                        "X: %{x:.4f}<br>"
                        "Y: %{y:.4f}<br>"
                        "f(x, y): %{customdata[1]:.4e}<br>"
                        "||∇f||: %{customdata[2]:.4e}<extra></extra>"
                    ),
                )
            )

            # Highlight Current / Landing Point
            fig_2d.add_trace(
                go.Scatter(
                    x=[asc_hist[-1, 1]],
                    y=[asc_hist[-1, 2]],
                    mode="markers",
                    marker=dict(
                        color=ASC_COLOR,
                        size=14,
                        symbol="x",
                        line=dict(color="#FFFFFF", width=2),
                    ),
                    name="Ascent Head",
                    showlegend=False,
                    hoverinfo="skip",
                )
            )

        # 4. Starting Coordinate Marker (Star)
        fig_2d.add_trace(
            go.Scatter(
                x=[st.session_state.start_x],
                y=[st.session_state.start_y],
                mode="markers+text",
                marker=dict(
                    color=START_COLOR,
                    size=16,
                    symbol="star",
                    line=dict(color="#000000" if is_light else "#0B0E14", width=1.5),
                ),
                text=["Start θ₀"],
                textposition="top center",
                textfont=dict(color=START_COLOR, size=11, family="monospace"),
                name="Start Position θ₀",
                hoverinfo="text+x+y",
            )
        )

        fig_2d.update_layout(
            paper_bgcolor=PAPER_BG,
            plot_bgcolor=PLOT_BG,
            margin=dict(l=20, r=20, t=30, b=20),
            height=580,
            xaxis=dict(
                title=dict(text="X Coordinate", font=dict(color=AXIS_COLOR)),
                range=[x_min, x_max],
                gridcolor=GRID_COLOR,
                zerolinecolor=AXIS_COLOR,
                tickfont=dict(color=AXIS_COLOR),
            ),
            yaxis=dict(
                title=dict(text="Y Coordinate", font=dict(color=AXIS_COLOR)),
                range=[y_min, y_max],
                gridcolor=GRID_COLOR,
                zerolinecolor=AXIS_COLOR,
                tickfont=dict(color=AXIS_COLOR),
                scaleanchor="x",
                scaleratio=1,
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                font=dict(color=TEXT_COLOR, size=11),
                bgcolor=LEGEND_BG,
                bordercolor=LEGEND_BORDER,
                borderwidth=1,
            ),
        )

        # Interactive coordinate capture via Plotly chart click
        chart_event = st.plotly_chart(
            fig_2d,
            use_container_width=True,
            key="contour_map_view",
            on_select="rerun",
            selection_mode=["points"],
        )

        # If user clicks on the plot to choose a custom start point
        if chart_event and "selection" in chart_event and chart_event["selection"]:
            clicked_pts = chart_event["selection"].get("points", [])
            if clicked_pts:
                new_x = clicked_pts[0].get("x")
                new_y = clicked_pts[0].get("y")
                if new_x is not None and new_y is not None:
                    if (
                        abs(new_x - st.session_state.start_x) > 1e-4
                        or abs(new_y - st.session_state.start_y) > 1e-4
                    ):
                        st.session_state.start_x = round(new_x, 3)
                        st.session_state.start_y = round(new_y, 3)
                        st.rerun()

        st.caption("💡 **Interactive Tip:** Click anywhere on the contour plot to set a new starting point θ₀.")

    with tab_3d:
        # 3D Elevation Surface Visualization
        fig_3d = go.Figure()

        # Surface
        fig_3d.add_trace(
            go.Surface(
                x=x_grid,
                y=y_grid,
                z=Z,
                colorscale=CONTOUR_SCALE,
                opacity=0.8,
                showscale=False,
                name="Landscape",
            )
        )

        # 3D Descent Trail
        if len(desc_hist) > 0:
            fig_3d.add_trace(
                go.Scatter3d(
                    x=desc_hist[:, 1],
                    y=desc_hist[:, 2],
                    z=desc_hist[:, 3],
                    mode="lines+markers",
                    line=dict(color=DESC_COLOR, width=6),
                    marker=dict(color=DESC_COLOR, size=3),
                    name="Gradient Descent (Valley)",
                )
            )

        # 3D Ascent Trail
        if len(asc_hist) > 0:
            fig_3d.add_trace(
                go.Scatter3d(
                    x=asc_hist[:, 1],
                    y=asc_hist[:, 2],
                    z=asc_hist[:, 3],
                    mode="lines+markers",
                    line=dict(color=ASC_COLOR, width=6),
                    marker=dict(color=ASC_COLOR, size=3),
                    name="Gradient Ascent (Peak)",
                )
            )

        fig_3d.update_layout(
            paper_bgcolor=PAPER_BG,
            margin=dict(l=10, r=10, t=10, b=10),
            height=580,
            scene=dict(
                xaxis=dict(title="X", backgroundcolor=PLOT_BG, gridcolor=GRID_COLOR, color=AXIS_COLOR),
                yaxis=dict(title="Y", backgroundcolor=PLOT_BG, gridcolor=GRID_COLOR, color=AXIS_COLOR),
                zaxis=dict(title="f(x, y)", backgroundcolor=PLOT_BG, gridcolor=GRID_COLOR, color=AXIS_COLOR),
            ),
            legend=dict(font=dict(color=TEXT_COLOR)),
        )
        st.plotly_chart(fig_3d, use_container_width=True)


# -----------------------------------------------------------------------------
# Panel 3: Right Telemetry Panel
# -----------------------------------------------------------------------------
with col_telemetry:
    st.markdown("### 📊 Dual Telemetry Grid")

    # Helper function for status badges
    def get_badge_html(status: TerminationStatus) -> str:
        if status == TerminationStatus.CONVERGED:
            return '<span class="badge badge-converged">Converged</span>'
        elif status == TerminationStatus.MAX_ITERATIONS:
            return '<span class="badge badge-max-iter">Iteration Limit</span>'
        else:
            return '<span class="badge badge-diverged">Diverged / Exploded</span>'

    # Current scrubber values
    desc_curr_row = desc_hist[-1] if len(desc_hist) > 0 else np.zeros(5)
    asc_curr_row = asc_hist[-1] if len(asc_hist) > 0 else np.zeros(5)

    # Telemetry Card: Gradient Descent
    desc_status_badge = get_badge_html(descent_result.status)
    st.markdown(
        f"""
        <div class="telemetry-card descent-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-weight: 700; color: {DESC_COLOR}; font-size: 1.05rem;">
                    ⚡ Gradient Descent
                </span>
                {desc_status_badge}
            </div>
            <div style="font-size: 0.78rem; color: {'#64748B' if is_light else '#94A3B8'}; margin-bottom: 10px;">
                Step index: <b>{desc_curr_row[0]:.0f} / {descent_result.iterations_completed}</b>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                <div>
                    <div class="metric-label">Coordinates (x, y)</div>
                    <div class="metric-value-cyan">({desc_curr_row[1]:.3f}, {desc_curr_row[2]:.3f})</div>
                </div>
                <div>
                    <div class="metric-label">Cost f(x, y)</div>
                    <div class="metric-value">{desc_curr_row[3]:.4e}</div>
                </div>
                <div>
                    <div class="metric-label">Gradient Norm ||∇f||</div>
                    <div class="metric-value">{desc_curr_row[4]:.4e}</div>
                </div>
                <div>
                    <div class="metric-label">Total Distance</div>
                    <div class="metric-value">{descent_result.total_path_distance:.3f}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Telemetry Card: Gradient Ascent
    asc_status_badge = get_badge_html(ascent_result.status)
    st.markdown(
        f"""
        <div class="telemetry-card ascent-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-weight: 700; color: {ASC_COLOR}; font-size: 1.05rem;">
                    🚀 Gradient Ascent
                </span>
                {asc_status_badge}
            </div>
            <div style="font-size: 0.78rem; color: {'#64748B' if is_light else '#94A3B8'}; margin-bottom: 10px;">
                Step index: <b>{asc_curr_row[0]:.0f} / {ascent_result.iterations_completed}</b>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                <div>
                    <div class="metric-label">Coordinates (x, y)</div>
                    <div class="metric-value-magenta">({asc_curr_row[1]:.3f}, {asc_curr_row[2]:.3f})</div>
                </div>
                <div>
                    <div class="metric-label">Objective f(x, y)</div>
                    <div class="metric-value">{asc_curr_row[3]:.4e}</div>
                </div>
                <div>
                    <div class="metric-label">Gradient Norm ||∇f||</div>
                    <div class="metric-value">{asc_curr_row[4]:.4e}</div>
                </div>
                <div>
                    <div class="metric-label">Total Distance</div>
                    <div class="metric-value">{ascent_result.total_path_distance:.3f}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Real-Time Telemetry Curve Charts
    st.markdown("#### 📈 Convergence Curves")
    chart_tabs = st.tabs(["f(x, y) Value", "Gradient Norm ||∇f||", "Rate of Movement"])

    with chart_tabs[0]:
        fig_loss = go.Figure()
        fig_loss.add_trace(
            go.Scatter(
                x=descent_result.history[:, 0],
                y=descent_result.history[:, 3],
                mode="lines",
                name="Descent f(x, y)",
                line=dict(color=DESC_COLOR, width=2.5),
            )
        )
        fig_loss.add_trace(
            go.Scatter(
                x=ascent_result.history[:, 0],
                y=ascent_result.history[:, 3],
                mode="lines",
                name="Ascent f(x, y)",
                line=dict(color=ASC_COLOR, width=2.5),
            )
        )
        fig_loss.update_layout(
            paper_bgcolor=PAPER_BG,
            plot_bgcolor=PLOT_BG,
            margin=dict(l=10, r=10, t=10, b=10),
            height=200,
            xaxis=dict(title=dict(text="Iteration", font=dict(color=AXIS_COLOR)), gridcolor=GRID_COLOR, tickfont=dict(color=AXIS_COLOR)),
            yaxis=dict(title=dict(text="f(x, y)", font=dict(color=AXIS_COLOR)), gridcolor=GRID_COLOR, tickfont=dict(color=AXIS_COLOR)),
            legend=dict(font=dict(color=TEXT_COLOR, size=10), bgcolor=LEGEND_BG),
        )
        st.plotly_chart(fig_loss, use_container_width=True)

    with chart_tabs[1]:
        fig_grad = go.Figure()
        fig_grad.add_trace(
            go.Scatter(
                x=descent_result.history[:, 0],
                y=descent_result.history[:, 4],
                mode="lines",
                name="Descent ||∇f||",
                line=dict(color=DESC_COLOR, width=2.5),
            )
        )
        fig_grad.add_trace(
            go.Scatter(
                x=ascent_result.history[:, 0],
                y=ascent_result.history[:, 4],
                mode="lines",
                name="Ascent ||∇f||",
                line=dict(color=ASC_COLOR, width=2.5),
            )
        )
        fig_grad.update_layout(
            paper_bgcolor=PAPER_BG,
            plot_bgcolor=PLOT_BG,
            margin=dict(l=10, r=10, t=10, b=10),
            height=200,
            yaxis_type="log",
            xaxis=dict(title=dict(text="Iteration", font=dict(color=AXIS_COLOR)), gridcolor=GRID_COLOR, tickfont=dict(color=AXIS_COLOR)),
            yaxis=dict(title=dict(text="log ||∇f||", font=dict(color=AXIS_COLOR)), gridcolor=GRID_COLOR, tickfont=dict(color=AXIS_COLOR)),
            legend=dict(font=dict(color=TEXT_COLOR, size=10), bgcolor=LEGEND_BG),
        )
        st.plotly_chart(fig_grad, use_container_width=True)

    with chart_tabs[2]:
        def get_step_deltas(hist: np.ndarray) -> np.ndarray:
            if len(hist) < 2:
                return np.zeros(len(hist))
            coords = hist[:, 1:3]
            diffs = np.linalg.norm(np.diff(coords, axis=0), axis=1)
            return np.concatenate([[0.0], diffs])

        desc_deltas = get_step_deltas(descent_result.history)
        asc_deltas = get_step_deltas(ascent_result.history)

        fig_vel = go.Figure()
        fig_vel.add_trace(
            go.Scatter(
                x=descent_result.history[:, 0],
                y=desc_deltas,
                mode="lines",
                name="Descent Step ||Δθ||",
                line=dict(color=DESC_COLOR, width=2),
            )
        )
        fig_vel.add_trace(
            go.Scatter(
                x=ascent_result.history[:, 0],
                y=asc_deltas,
                mode="lines",
                name="Ascent Step ||Δθ||",
                line=dict(color=ASC_COLOR, width=2),
            )
        )
        fig_vel.update_layout(
            paper_bgcolor=PAPER_BG,
            plot_bgcolor=PLOT_BG,
            margin=dict(l=10, r=10, t=10, b=10),
            height=200,
            xaxis=dict(title=dict(text="Iteration", font=dict(color=AXIS_COLOR)), gridcolor=GRID_COLOR, tickfont=dict(color=AXIS_COLOR)),
            yaxis=dict(title=dict(text="Step Distance ||Δθ||", font=dict(color=AXIS_COLOR)), gridcolor=GRID_COLOR, tickfont=dict(color=AXIS_COLOR)),
            legend=dict(font=dict(color=TEXT_COLOR, size=10), bgcolor=LEGEND_BG),
        )
        st.plotly_chart(fig_vel, use_container_width=True)


# -----------------------------------------------------------------------------
# Bottom Section: Structured NumPy Telemetry History Table
# -----------------------------------------------------------------------------
with st.expander("📋 Detailed NumPy Telemetry History Matrix [Iteration, X, Y, f(x, y), ||∇f||]", expanded=False):
    col_t1, col_t2 = st.columns(2)

    with col_t1:
        st.markdown(f"<b style='color:{DESC_COLOR};'>Descent History Trace Array</b>", unsafe_allow_html=True)
        df_desc = pd.DataFrame(
            descent_result.history,
            columns=["Iteration", "X_coord", "Y_coord", "Function_Value", "Gradient_Norm"],
        )
        st.dataframe(df_desc, use_container_width=True, height=240)
        st.download_button(
            "⬇️ Download Descent CSV",
            df_desc.to_csv(index=False),
            file_name="gradient_descent_trace.csv",
            mime="text/csv",
        )

    with col_t2:
        st.markdown(f"<b style='color:{ASC_COLOR};'>Ascent History Trace Array</b>", unsafe_allow_html=True)
        df_asc = pd.DataFrame(
            ascent_result.history,
            columns=["Iteration", "X_coord", "Y_coord", "Function_Value", "Gradient_Norm"],
        )
        st.dataframe(df_asc, use_container_width=True, height=240)
        st.download_button(
            "⬇️ Download Ascent CSV",
            df_asc.to_csv(index=False),
            file_name="gradient_ascent_trace.csv",
            mime="text/csv",
        )
