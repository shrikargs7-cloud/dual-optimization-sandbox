"""
Generates clean pedagogical diagrams for the academic project report:
1. diagram1_duality.png: Visualizes the ball on the slope showing why the gradient points uphill, and how Descent vs. Ascent move.
2. diagram2_architecture.png: System flow diagram showing User Input -> Engine -> Safety Bounds -> Output Visuals.
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches

out_dir = os.path.join(os.path.dirname(__file__), "report_assets")
os.makedirs(out_dir, exist_ok=True)

# ---------------------------------------------------------------------------
# Diagram 1: Geometric Duality (Ball on a Hill)
# ---------------------------------------------------------------------------
def make_diagram1():
    fig, ax = plt.subplots(figsize=(8.5, 4.4), dpi=150, facecolor='#FFFFFF')
    ax.set_facecolor('#F8FAFC')

    x = np.linspace(-3.2, 3.2, 400)
    y = 0.5 * x**2

    ax.plot(x, y, color='#1E293B', linewidth=3, label='Landscape Surface f(θ)')
    
    # Current point
    x0 = 1.9
    y0 = 0.5 * x0**2
    ax.scatter([x0], [y0], color='#F59E0B', s=200, marker='o', edgecolor='#000', linewidth=1.5, zorder=5, label='Current Point θ_t')

    # Gradient Direction (Points Uphill)
    ax.annotate(
        '', xy=(2.7, 0.5 * 2.7**2), xytext=(x0, y0),
        arrowprops=dict(arrowstyle="->,head_width=0.4,head_length=0.6", color='#64748B', lw=2.5, ls='--')
    )
    ax.text(2.1, 2.7, '+ ∇f(θ_t)\nGradient points UPHILL\n(Direction of maximum increase)', color='#475569', fontsize=9.5, fontweight='bold')

    # Gradient Descent (Steps Downhill)
    ax.annotate(
        '', xy=(0.8, 0.5 * 0.8**2), xytext=(x0, y0),
        arrowprops=dict(arrowstyle="->,head_width=0.5,head_length=0.7", color='#0284C7', lw=3.5)
    )
    ax.text(0.3, 1.3, 'Gradient Descent: θ_(t+1) = θ_t - α ∇f(θ_t)\n[Steps OPPOSITE to gradient -> DOWNHILL to Valley]', color='#0284C7', fontsize=10, fontweight='bold')

    # Gradient Ascent (Steps Uphill)
    ax.annotate(
        '', xy=(2.9, 0.5 * 2.9**2), xytext=(x0, y0),
        arrowprops=dict(arrowstyle="->,head_width=0.5,head_length=0.7", color='#E11D48', lw=3.5)
    )
    ax.text(2.6, 4.3, 'Gradient Ascent: θ_(t+1) = θ_t + α ∇f(θ_t)\n[Steps ALONG gradient -> UPHILL to Peak]', color='#E11D48', fontsize=10, fontweight='bold')

    # Target valley
    ax.scatter([0], [0], color='#10B981', s=160, marker='*', edgecolor='#000', zorder=5, label='Valley Floor / Minimum (0, 0)')

    ax.set_title('Geometric Principle of Optimization Duality on a 1D Cross-Section', fontsize=12, fontweight='bold', pad=12, color='#0F172A')
    ax.set_xlabel('Parameter Coordinate θ', fontsize=10, color='#334155')
    ax.set_ylabel('Objective / Cost Value f(θ)', fontsize=10, color='#334155')
    ax.set_ylim(-0.3, 5.5)
    ax.grid(True, linestyle=':', alpha=0.7, color='#CBD5E1')
    ax.legend(loc='upper left', frameon=True, facecolor='#FFFFFF', edgecolor='#CBD5E1', fontsize=8.5)

    plt.tight_layout()
    path = os.path.join(out_dir, "diagram1_duality.png")
    plt.savefig(path)
    plt.close()
    print("Saved:", path)


# ---------------------------------------------------------------------------
# Diagram 2: System Architecture Flowchart
# ---------------------------------------------------------------------------
def make_diagram2():
    fig, ax = plt.subplots(figsize=(9.2, 4.2), dpi=150, facecolor='#FFFFFF')
    ax.set_facecolor('#FFFFFF')
    ax.axis('off')

    def draw_box(x, y, w, h, title, subtitle, bg_color, border_color):
        box = patches.FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.08,rounding_size=0.15",
            facecolor=bg_color, edgecolor=border_color, linewidth=2.0
        )
        ax.add_patch(box)
        ax.text(x + w / 2, y + h * 0.65, title, ha='center', va='center', fontsize=10.5, fontweight='bold', color='#0F172A')
        ax.text(x + w / 2, y + h * 0.32, subtitle, ha='center', va='center', fontsize=8.2, color='#475569', multialignment='center')

    # Step 1: Input
    draw_box(0.05, 0.45, 0.22, 0.45, "1. USER CONFIG", "Choose Landscape\nStart Point (x0, y0)\nLearning Rate (α)", "#F0F9FF", "#0284C7")
    
    # Step 2: Math Topologies
    draw_box(0.32, 0.55, 0.22, 0.38, "2A. TOPOLOGIES", "Bowl, Rosenbrock,\nAckley, Saddle\nExact Gradients ∇f", "#F8FAFC", "#64748B")

    # Step 3: Engine Loop
    draw_box(0.32, 0.08, 0.22, 0.38, "2B. DUAL ENGINE", "Pure NumPy Loop\nDescent: θ - α∇f\nAscent: θ + α∇f", "#FEF2F2", "#E11D48")

    # Step 4: Safety Guards
    draw_box(0.59, 0.32, 0.17, 0.45, "3. SAFETY GUARDS", "Check ||∇f|| < ε\n(Convergence)\nCheck NaN/Inf\n(Divergence Halt)", "#FEFCE8", "#CA8A04")

    # Step 5: Dashboard Output
    draw_box(0.81, 0.32, 0.17, 0.45, "4. UI DASHBOARD", "2D Contour Map\n3D Surface Mesh\nTelemetry Cards\nConvergence Curves", "#F0FDF4", "#16A34A")

    # Connective Arrows
    def arrow(x1, y1, x2, y2):
        ax.annotate(
            '', xy=(x2, y2), xytext=(x1, y1),
            arrowprops=dict(arrowstyle="->,head_width=0.35,head_length=0.5", color='#334155', lw=2)
        )

    arrow(0.27, 0.68, 0.32, 0.72)
    arrow(0.27, 0.65, 0.32, 0.28)
    arrow(0.43, 0.55, 0.43, 0.46)
    arrow(0.54, 0.55, 0.59, 0.55)
    arrow(0.76, 0.55, 0.81, 0.55)

    ax.set_xlim(0, 1.02)
    ax.set_ylim(0, 1.0)
    ax.set_title("Dual-Optimization Sandbox: Architecture and Data Processing Pipeline", fontsize=12, fontweight='bold', pad=10, color='#0F172A')

    plt.tight_layout()
    path = os.path.join(out_dir, "diagram2_architecture.png")
    plt.savefig(path)
    plt.close()
    print("Saved:", path)


if __name__ == "__main__":
    make_diagram1()
    make_diagram2()
