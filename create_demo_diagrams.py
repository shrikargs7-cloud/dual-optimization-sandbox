"""
Creates high-aesthetic, visual graphics for the report:
1. diagram3_dashboard_demo.png: A crisp diagram of the 3-panel UI layout (Controls, Contour Canvas with Click-to-Pick, Telemetry Cards).
2. diagram4_workflow_steps.png: Step-by-step user demonstration workflow (Choose terrain -> Set coordinates -> Tune alpha -> Scrub playback -> Observe outcome).
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches

out_dir = os.path.join(os.path.dirname(__file__), "report_assets")
os.makedirs(out_dir, exist_ok=True)

# ---------------------------------------------------------------------------
# Diagram 3: Visual Dashboard UI Breakdown
# ---------------------------------------------------------------------------
def make_dashboard_mockup():
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=180, facecolor='#0F172A')
    ax.set_facecolor('#0F172A')
    ax.axis('off')

    # Main application frame
    app_bg = patches.FancyBboxPatch(
        (0.02, 0.04), 0.96, 0.90,
        boxstyle="round,pad=0.01,rounding_size=0.03",
        facecolor='#1E293B', edgecolor='#334155', linewidth=1.5
    )
    ax.add_patch(app_bg)

    # Top Navigation bar
    navbar = patches.FancyBboxPatch(
        (0.02, 0.86), 0.96, 0.08,
        boxstyle="round,pad=0.005,rounding_size=0.02",
        facecolor='#0F172A', edgecolor='#334155', linewidth=1.0
    )
    ax.add_patch(navbar)
    ax.text(0.05, 0.90, "Dual-Optimization Sandbox (Descent vs. Ascent)", color='#F8FAFC', fontsize=12, fontweight='bold', va='center')
    ax.text(0.95, 0.90, "Light / Dark Mode  •  RV University CS2806", color='#94A3B8', fontsize=8.5, ha='right', va='center')

    # Panel 1: Left Controls (Sidebar)
    panel1 = patches.FancyBboxPatch(
        (0.04, 0.07), 0.23, 0.76,
        boxstyle="round,pad=0.01,rounding_size=0.02",
        facecolor='#0F172A', edgecolor='#38BDF8', linewidth=1.5
    )
    ax.add_patch(panel1)
    ax.text(0.155, 0.79, "PANEL 1: CONTROLS", color='#38BDF8', fontsize=9.5, fontweight='bold', ha='center')
    
    ctrl_items = [
        "1. Select Landscape\n   [Bowl / Rosenbrock / Ackley]",
        "2. Start Coordinates\n   X₀ = 3.00,  Y₀ = 2.50",
        "3. Learning Rate (α)\n   Slider: 0.001 to 1.500",
        "4. Max Iterations\n   Slider: 10 to 500 steps",
        "5. Safety Bounds\n   Tolerance: ||∇f|| < 1e-5"
    ]
    for i, item in enumerate(ctrl_items):
        y_pos = 0.69 - (i * 0.12)
        box = patches.FancyBboxPatch((0.05, y_pos - 0.04), 0.21, 0.09, boxstyle="round,pad=0.005,rounding_size=0.01", facecolor='#1E293B', edgecolor='#334155', lw=1)
        ax.add_patch(box)
        ax.text(0.06, y_pos, item, color='#E2E8F0', fontsize=7.2, va='center')

    # Panel 2: Center Interactive Canvas
    panel2 = patches.FancyBboxPatch(
        (0.29, 0.07), 0.44, 0.76,
        boxstyle="round,pad=0.01,rounding_size=0.02",
        facecolor='#0F172A', edgecolor='#0284C7', linewidth=1.5
    )
    ax.add_patch(panel2)
    ax.text(0.51, 0.79, "PANEL 2: INTERACTIVE 2D / 3D CANVAS", color='#38BDF8', fontsize=9.5, fontweight='bold', ha='center')

    # Mock 2D contour circles
    import numpy as np
    cx, cy = 0.51, 0.45
    for r in [0.22, 0.17, 0.12, 0.07, 0.03]:
        circ = patches.Circle((cx, cy), r, facecolor='none', edgecolor='#334155', linestyle='--', lw=1.0)
        ax.add_patch(circ)

    # Start Point
    ax.scatter([0.62], [0.55], color='#FACC15', s=160, marker='*', edgecolor='#000', zorder=10)
    ax.text(0.63, 0.57, "Start θ₀", color='#FACC15', fontsize=8, fontweight='bold')

    # Descent Path (Cyan into center)
    ax.annotate('', xy=(cx, cy), xytext=(0.62, 0.55),
                arrowprops=dict(arrowstyle="->,head_width=0.4,head_length=0.6", color='#00F0FF', lw=3.0))
    ax.text(0.44, 0.53, "Descent (Cyan)\nDown to Min", color='#00F0FF', fontsize=7.5, fontweight='bold')

    # Ascent Path (Magenta away from center)
    ax.annotate('', xy=(0.71, 0.65), xytext=(0.62, 0.55),
                arrowprops=dict(arrowstyle="->,head_width=0.4,head_length=0.6", color='#FF007A', lw=3.0))
    ax.text(0.66, 0.67, "Ascent (Magenta)\nUp to Summit", color='#FF007A', fontsize=7.5, fontweight='bold')

    # Click-to-pick callout
    click_bubble = patches.FancyBboxPatch((0.31, 0.11), 0.40, 0.09, boxstyle="round,pad=0.005,rounding_size=0.01", facecolor='#1E293B', edgecolor='#FACC15', lw=1.2)
    ax.add_patch(click_bubble)
    ax.text(0.51, 0.155, "CLICK-TO-PICK ANYWHERE ON MAP\nClicking captures new coordinates & re-runs instantly!", color='#F8FAFC', fontsize=7.5, fontweight='bold', ha='center', va='center')

    # Panel 3: Right Telemetry Cards
    panel3 = patches.FancyBboxPatch(
        (0.75, 0.07), 0.21, 0.76,
        boxstyle="round,pad=0.01,rounding_size=0.02",
        facecolor='#0F172A', edgecolor='#E11D48', linewidth=1.5
    )
    ax.add_patch(panel3)
    ax.text(0.855, 0.79, "PANEL 3: TELEMETRY", color='#F43F5E', fontsize=9.5, fontweight='bold', ha='center')

    # Descent Card
    desc_card = patches.FancyBboxPatch((0.76, 0.50), 0.19, 0.24, boxstyle="round,pad=0.005,rounding_size=0.01", facecolor='#1E293B', edgecolor='#00F0FF', lw=1.5)
    ax.add_patch(desc_card)
    ax.text(0.77, 0.70, "GRADIENT DESCENT", color='#00F0FF', fontsize=7.5, fontweight='bold')
    ax.text(0.93, 0.70, "CONVERGED", color='#10B981', fontsize=6.5, fontweight='bold', ha='right')
    ax.text(0.77, 0.64, "Final: (0.000, 0.000)", color='#E2E8F0', fontsize=6.8)
    ax.text(0.77, 0.58, "Cost f: 1.88e-11", color='#E2E8F0', fontsize=6.8)
    ax.text(0.77, 0.53, "Steps: 60 / 150", color='#94A3B8', fontsize=6.8)

    # Ascent Card
    asc_card = patches.FancyBboxPatch((0.76, 0.23), 0.19, 0.24, boxstyle="round,pad=0.005,rounding_size=0.01", facecolor='#1E293B', edgecolor='#FF007A', lw=1.5)
    ax.add_patch(asc_card)
    ax.text(0.77, 0.43, "GRADIENT ASCENT", color='#FF007A', fontsize=7.5, fontweight='bold')
    ax.text(0.93, 0.43, "DIVERGED", color='#EF4444', fontsize=6.5, fontweight='bold', ha='right')
    ax.text(0.77, 0.37, "Final: (1050, 875)", color='#E2E8F0', fontsize=6.8)
    ax.text(0.77, 0.31, "Cost f: 1.76e+10", color='#E2E8F0', fontsize=6.8)
    ax.text(0.77, 0.26, "Halted: Step 59 (Exploded)", color='#94A3B8', fontsize=6.8)

    # CSV Download Button
    csv_btn = patches.FancyBboxPatch((0.76, 0.10), 0.19, 0.08, boxstyle="round,pad=0.005,rounding_size=0.01", facecolor='#0284C7', edgecolor='#38BDF8', lw=1)
    ax.add_patch(csv_btn)
    ax.text(0.855, 0.14, "DOWNLOAD CSV DATA", color='#FFFFFF', fontsize=7.2, fontweight='bold', ha='center', va='center')

    plt.tight_layout()
    path = os.path.join(out_dir, "diagram3_dashboard_demo.png")
    plt.savefig(path)
    plt.close()
    print("Saved:", path)


# ---------------------------------------------------------------------------
# Diagram 4: Demonstration Step-by-Step Workflow
# ---------------------------------------------------------------------------
def make_workflow_diagram():
    fig, ax = plt.subplots(figsize=(10, 3.8), dpi=180, facecolor='#FFFFFF')
    ax.set_facecolor('#FFFFFF')
    ax.axis('off')

    steps = [
        ("STEP 1: SELECT TOPOLOGY", "Pick Paraboloid Bowl,\nRosenbrock, Ackley, or Saddle\nfrom the dropdown menu.", "#0284C7", "#E0F2FE"),
        ("STEP 2: DROP START POINT θ₀", "Click directly on the\n2D contour map or enter\ncoordinates manually.", "#7C3AED", "#EDE9FE"),
        ("STEP 3: TUNE STEP SIZE (α)", "Slide learning rate (0.001 - 1.5)\nto observe smooth steps\nor wild oscillations.", "#D97706", "#FEF3C7"),
        ("STEP 4: TIME SCRUBBING", "Drag the playback slider\nto inspect step-by-step\niteration progression.", "#059669", "#D1FAE5"),
        ("STEP 5: READ TELEMETRY", "Compare final cost values,\ngradient lengths, and\nexport raw NumPy CSV.", "#DC2626", "#FEE2E2"),
    ]

    for i, (title, desc, stroke_color, bg_color) in enumerate(steps):
        x = 0.02 + i * 0.198
        box = patches.FancyBboxPatch(
            (x, 0.15), 0.175, 0.70,
            boxstyle="round,pad=0.01,rounding_size=0.04",
            facecolor=bg_color, edgecolor=stroke_color, linewidth=2.0
        )
        ax.add_patch(box)
        # Header circle
        circ = patches.Circle((x + 0.0875, 0.73), 0.06, facecolor=stroke_color, edgecolor='#000', lw=0.5)
        ax.add_patch(circ)
        ax.text(x + 0.0875, 0.73, str(i + 1), color='#FFFFFF', fontsize=11, fontweight='bold', ha='center', va='center')

        ax.text(x + 0.0875, 0.54, title, color='#0F172A', fontsize=8.0, fontweight='bold', ha='center', va='center')
        ax.text(x + 0.0875, 0.32, desc, color='#475569', fontsize=7.2, ha='center', va='center', multialignment='center')

        # Arrow to next step
        if i < 4:
            ax.annotate('', xy=(x + 0.192, 0.50), xytext=(x + 0.177, 0.50),
                        arrowprops=dict(arrowstyle="->,head_width=0.3,head_length=0.4", color='#64748B', lw=2.0))

    ax.set_xlim(0, 1.0)
    ax.set_ylim(0, 1.0)
    ax.set_title("User Demonstration Protocol: How to Operate the Dual-Optimization Sandbox", fontsize=11.5, fontweight='bold', pad=10, color='#0F172A')

    plt.tight_layout()
    path = os.path.join(out_dir, "diagram4_workflow_steps.png")
    plt.savefig(path)
    plt.close()
    print("Saved:", path)


if __name__ == "__main__":
    make_dashboard_mockup()
    make_workflow_diagram()
