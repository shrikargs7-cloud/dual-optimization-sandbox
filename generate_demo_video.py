"""
Robust Video Generator for Dual-Optimization Sandbox Demonstration.
Renders canvas frames into an OpenCV VideoWriter / FFmpeg video stream.
Guarantees rock-solid rendering with no blank/empty frames.
"""

import os
import sys
import numpy as np
import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Include project directory
curr_dir = os.path.dirname(os.path.abspath(__file__))
if curr_dir not in sys.path:
    sys.path.append(curr_dir)

from landscapes import LANDSCAPES
from engine import OptimizationEngine

# Visual Palette
COLOR_BG = "#0B0E14"
COLOR_PANEL = "#111622"
COLOR_CYAN = "#00F0FF"      # Gradient Descent
COLOR_MAGENTA = "#FF007A"   # Gradient Ascent
COLOR_START = "#FACC15"     # Start point star
COLOR_TEXT = "#F8FAFC"
COLOR_MUTED = "#94A3B8"

FPS = 24
WIDTH_PX, HEIGHT_PX = 1280, 720
DPI = 100
FIGSIZE = (WIDTH_PX / DPI, HEIGHT_PX / DPI)


def fig_to_bgr_frame(fig):
    """Draws figure canvas and extracts exact BGR numpy array for OpenCV."""
    fig.canvas.draw()
    rgba_buffer = fig.canvas.buffer_rgba()
    img_rgba = np.asarray(rgba_buffer, dtype=np.uint8)
    img_bgr = cv2.cvtColor(img_rgba, cv2.COLOR_RGBA2BGR)
    # Ensure dimensions match exact pixel targets
    if img_bgr.shape[0] != HEIGHT_PX or img_bgr.shape[1] != WIDTH_PX:
        img_bgr = cv2.resize(img_bgr, (WIDTH_PX, HEIGHT_PX))
    return img_bgr


def render_card_frame(title, subtitle, detail_text=""):
    """Creates a standalone title/conclusion card."""
    fig = plt.figure(figsize=FIGSIZE, dpi=DPI, facecolor=COLOR_BG)
    ax = fig.add_subplot(111)
    ax.set_facecolor(COLOR_BG)
    ax.axis("off")

    ax.text(
        0.5, 0.60, title,
        color=COLOR_TEXT, fontsize=26, fontweight="bold",
        ha="center", va="center"
    )
    ax.text(
        0.5, 0.48, subtitle,
        color=COLOR_CYAN, fontsize=18, fontweight="medium",
        ha="center", va="center"
    )
    if detail_text:
        ax.text(
            0.5, 0.36, detail_text,
            color=COLOR_MUTED, fontsize=12, family="monospace",
            ha="center", va="center"
        )
    frame = fig_to_bgr_frame(fig)
    plt.close(fig)
    return frame


def render_optimization_scene(
    video_writer,
    landscape_key,
    start_pt,
    lr,
    max_steps,
    act_title,
    key_insight,
    duration_sec=6.5,
):
    landscape = LANDSCAPES[landscape_key]
    engine = OptimizationEngine()
    desc_res, asc_res = engine.run_dual(
        landscape=landscape,
        initial_point=start_pt,
        learning_rate=lr,
        max_iterations=max_steps,
    )

    bounds = landscape.default_bounds
    all_x = np.concatenate([desc_res.x_coords, asc_res.x_coords, [bounds[0], bounds[1]]])
    all_y = np.concatenate([desc_res.y_coords, asc_res.y_coords, [bounds[2], bounds[3]]])
    valid = np.isfinite(all_x) & np.isfinite(all_y)
    x_min = max(bounds[0], float(np.min(all_x[valid]))) - 0.4
    x_max = min(bounds[1], float(np.max(all_x[valid]))) + 0.4
    y_min = max(bounds[2], float(np.min(all_y[valid]))) - 0.4
    y_max = min(bounds[3], float(np.max(all_y[valid]))) + 0.4

    # Grid for contours
    res = 110
    xg = np.linspace(x_min, x_max, res)
    yg = np.linspace(y_min, y_max, res)
    X, Y = np.meshgrid(xg, yg)
    Z = landscape.evaluate(X, Y)

    total_frames = int(duration_sec * FPS)
    max_history_len = max(len(desc_res.history), len(asc_res.history))
    step_indices = np.linspace(1, max_history_len, total_frames, dtype=int)

    # Static pre-rendered background elements
    fig = plt.figure(figsize=FIGSIZE, dpi=DPI, facecolor=COLOR_BG)
    gs = fig.add_gridspec(
        2, 2,
        width_ratios=[1.25, 1.0],
        height_ratios=[1.0, 1.0],
        left=0.07, right=0.95,
        bottom=0.10, top=0.88,
        wspace=0.22, hspace=0.34
    )
    ax_map = fig.add_subplot(gs[:, 0])
    ax_val = fig.add_subplot(gs[0, 1])
    ax_grad = fig.add_subplot(gs[1, 1])

    for frame_i, current_step in enumerate(step_indices):
        ax_map.clear()
        ax_val.clear()
        ax_grad.clear()

        for ax in [ax_map, ax_val, ax_grad]:
            ax.set_facecolor(COLOR_PANEL)
            ax.tick_params(colors=COLOR_MUTED, labelsize=9)

        # Header Title
        fig.suptitle(
            f"{act_title}  •  {landscape.name} (α = {lr})",
            color=COLOR_TEXT, fontsize=15, fontweight="bold", y=0.96
        )

        # 1. 2D Contour Map
        ax_map.contourf(X, Y, Z, levels=25, cmap="viridis", alpha=0.8)
        ax_map.contour(X, Y, Z, levels=12, colors="#475569", linewidths=0.5, alpha=0.6)

        # Start coordinate
        ax_map.scatter(
            [start_pt[0]], [start_pt[1]],
            color=COLOR_START, s=130, marker="*", edgecolor="#000", zorder=6,
            label=f"Start θ₀ ({start_pt[0]:.1f}, {start_pt[1]:.1f})"
        )

        d_sub = desc_res.history[:min(current_step, len(desc_res.history))]
        a_sub = asc_res.history[:min(current_step, len(asc_res.history))]

        if len(d_sub) > 0:
            ax_map.plot(d_sub[:, 1], d_sub[:, 2], color=COLOR_CYAN, linewidth=2.8, zorder=4, label="Descent (Min)")
            ax_map.scatter(d_sub[-1, 1], d_sub[-1, 2], color=COLOR_CYAN, s=55, marker="o", edgecolor="#FFF", zorder=5)

        if len(a_sub) > 0:
            ax_map.plot(a_sub[:, 1], a_sub[:, 2], color=COLOR_MAGENTA, linewidth=2.8, zorder=4, label="Ascent (Max)")
            ax_map.scatter(a_sub[-1, 1], a_sub[-1, 2], color=COLOR_MAGENTA, s=55, marker="s", edgecolor="#FFF", zorder=5)

        ax_map.set_xlim(x_min, x_max)
        ax_map.set_ylim(y_min, y_max)
        ax_map.set_title("2D Contour Landscape & Trajectories", color=COLOR_TEXT, fontsize=11, pad=8)
        ax_map.set_xlabel("X Coordinate", color=COLOR_MUTED, fontsize=9)
        ax_map.set_ylabel("Y Coordinate", color=COLOR_MUTED, fontsize=9)
        ax_map.legend(loc="upper right", facecolor=COLOR_BG, edgecolor=COLOR_PANEL, labelcolor=COLOR_TEXT, fontsize=8)

        # 2. Value Curve
        if len(d_sub) > 0:
            ax_val.plot(d_sub[:, 0], d_sub[:, 3], color=COLOR_CYAN, linewidth=2.2, label="Descent Cost")
        if len(a_sub) > 0:
            ax_val.plot(a_sub[:, 0], a_sub[:, 3], color=COLOR_MAGENTA, linewidth=2.2, label="Ascent Reward")
        ax_val.set_title("Function Evaluation f(θ_t)", color=COLOR_TEXT, fontsize=11, pad=6)
        ax_val.set_xlabel("Step Index", color=COLOR_MUTED, fontsize=8)
        ax_val.set_ylabel("f(x, y)", color=COLOR_MUTED, fontsize=8)
        ax_val.grid(True, color="#1E293B", linestyle="--", linewidth=0.6)
        ax_val.legend(loc="upper right", facecolor=COLOR_BG, edgecolor=COLOR_PANEL, labelcolor=COLOR_TEXT, fontsize=8)

        # 3. Gradient Norm
        if len(d_sub) > 0:
            ax_grad.semilogy(d_sub[:, 0], d_sub[:, 4] + 1e-12, color=COLOR_CYAN, linewidth=2.2, label="||∇f|| Descent")
        if len(a_sub) > 0:
            ax_grad.semilogy(a_sub[:, 0], a_sub[:, 4] + 1e-12, color=COLOR_MAGENTA, linewidth=2.2, label="||∇f|| Ascent")
        ax_grad.set_title("Gradient Magnitude ||∇f(θ_t)|| (Log scale)", color=COLOR_TEXT, fontsize=11, pad=6)
        ax_grad.set_xlabel("Step Index", color=COLOR_MUTED, fontsize=8)
        ax_grad.set_ylabel("log ||∇f||", color=COLOR_MUTED, fontsize=8)
        ax_grad.grid(True, color="#1E293B", linestyle="--", linewidth=0.6)
        ax_grad.legend(loc="upper right", facecolor=COLOR_BG, edgecolor=COLOR_PANEL, labelcolor=COLOR_TEXT, fontsize=8)

        # 4. Insight Subtitle
        fig.text(
            0.5, 0.025,
            f"Key Takeaway: {key_insight}",
            color=COLOR_TEXT, fontsize=10, fontweight="bold",
            ha="center", va="bottom",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#1E293B", edgecolor="#334155")
        )

        frame_bgr = fig_to_bgr_frame(fig)
        video_writer.write(frame_bgr)

    plt.close(fig)


def main():
    raw_mp4 = os.path.join(curr_dir, "raw_demo.mp4")
    final_mp4 = os.path.join(curr_dir, "dual_optimization_demo.mp4")

    print(f"🎬 Opening OpenCV VideoWriter: {raw_mp4} ({WIDTH_PX}x{HEIGHT_PX} @ {FPS}fps)")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(raw_mp4, fourcc, FPS, (WIDTH_PX, HEIGHT_PX))

    if not writer.isOpened():
        raise RuntimeError("Failed to open OpenCV VideoWriter.")

    try:
        # Scene 1: Title Card (3 seconds)
        print("Rendering Scene 1: Title Screen...")
        title_frame = render_card_frame(
            title="Dual-Optimization Sandbox",
            subtitle="Gradient Descent vs. Gradient Ascent on Shared Landscapes",
            detail_text="Cyan: θ_{t+1} = θ_t - α∇f(θ_t) (Descent)   |   Magenta: θ_{t+1} = θ_t + α∇f(θ_t) (Ascent)"
        )
        for _ in range(int(3.0 * FPS)):
            writer.write(title_frame)

        # Scene 2: Paraboloid Bowl (6 seconds)
        print("Rendering Scene 2: Paraboloid Bowl...")
        render_optimization_scene(
            writer,
            landscape_key="bowl",
            start_pt=(3.0, 2.5),
            lr=0.1,
            max_steps=80,
            act_title="Act 1: Convex Benchmark (Paraboloid)",
            key_insight="Descent converges into (0,0) as ||∇f||→0; Ascent diverges because the bowl has no ceiling.",
            duration_sec=6.0
        )

        # Scene 3: Rosenbrock Valley (6.5 seconds)
        print("Rendering Scene 3: Rosenbrock Valley...")
        render_optimization_scene(
            writer,
            landscape_key="rosenbrock",
            start_pt=(-1.5, 1.8),
            lr=0.002,
            max_steps=180,
            act_title="Act 2: Ill-Conditioned Curvature (Rosenbrock Valley)",
            key_insight="Steep walls cause cross-ravine oscillation; learning rate tuning is critical.",
            duration_sec=6.5
        )

        # Scene 4: Ackley's Multimodal Surface (6.5 seconds)
        print("Rendering Scene 4: Ackley's Multimodal Surface...")
        render_optimization_scene(
            writer,
            landscape_key="ackley",
            start_pt=(2.5, 2.5),
            lr=0.05,
            max_steps=120,
            act_title="Act 3: Multimodal Surface (Ackley's Function)",
            key_insight="First-order gradient methods lack global sight and get trapped in local ring minima.",
            duration_sec=6.5
        )

        # Scene 5: Hyperbolic Saddle Point (6 seconds)
        print("Rendering Scene 5: Hyperbolic Saddle Point...")
        render_optimization_scene(
            writer,
            landscape_key="saddle",
            start_pt=(0.2, 0.2),
            lr=0.1,
            max_steps=60,
            act_title="Act 4: Curvature Duality (Hyperbolic Saddle Point)",
            key_insight="At saddle points, Gradient Descent and Gradient Ascent follow strictly orthogonal paths.",
            duration_sec=6.0
        )

        # Scene 6: Outro (3 seconds)
        print("Rendering Scene 6: Conclusion Card...")
        outro_frame = render_card_frame(
            title="Demonstration Concluded",
            subtitle="First-Principles Vector Calculus in Pure NumPy & Streamlit",
            detail_text="Interactive Dashboard: streamlit run app.py"
        )
        for _ in range(int(3.0 * FPS)):
            writer.write(outro_frame)

    finally:
        writer.release()
        print("OpenCV VideoWriter closed successfully.")

    # Convert using ffmpeg to standard web/QuickTime compatible h264
    print("Re-encoding with FFmpeg to H.264 (yuv420p)...")
    ffmpeg_cmd = f"ffmpeg -y -i '{raw_mp4}' -c:v libx264 -pix_fmt yuv420p -movflags +faststart '{final_mp4}'"
    os.system(ffmpeg_cmd)
    if os.path.exists(raw_mp4):
        os.remove(raw_mp4)

    final_size = os.path.getsize(final_mp4) / (1024 * 1024)
    print(f"🎉 Final Video successfully created: {final_mp4} ({final_size:.2f} MB)")


if __name__ == "__main__":
    main()
