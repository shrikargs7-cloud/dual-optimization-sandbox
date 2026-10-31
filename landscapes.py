"""
Mathematical Topologies and Analytic Gradients for Optimization Landscapes.

This module provides explicit mathematical surfaces and their exact analytical
partial derivatives for 2D optimization simulations (Descent vs. Ascent).
"""

from dataclasses import dataclass
from typing import Callable, Tuple
import numpy as np


@dataclass
class Landscape:
    """Represents a mathematical 2D optimization surface."""
    name: str
    id: str
    description: str
    formula_latex: str
    equation_str: str
    default_bounds: Tuple[float, float, float, float]  # (xmin, xmax, ymin, ymax)
    default_start: Tuple[float, float]
    default_lr: float
    global_min: Tuple[float, float, float]  # (x, y, z)
    evaluate_fn: Callable[[float | np.ndarray, float | np.ndarray], float | np.ndarray]
    gradient_fn: Callable[[float | np.ndarray, float | np.ndarray], np.ndarray]

    def evaluate(self, x: float | np.ndarray, y: float | np.ndarray) -> float | np.ndarray:
        """Evaluate function value f(x, y). Vectorized over numpy arrays."""
        return self.evaluate_fn(x, y)

    def gradient(self, x: float | np.ndarray, y: float | np.ndarray) -> np.ndarray:
        """Evaluate analytic gradient [df/dx, df/dy] at (x, y)."""
        return self.gradient_fn(x, y)


# ---------------------------------------------------------------------------
# Landscape 1: Symmetric Bowl (Paraboloid)
# ---------------------------------------------------------------------------
def _bowl_eval(x: float | np.ndarray, y: float | np.ndarray) -> float | np.ndarray:
    """f(x, y) = x^2 + y^2"""
    return x**2 + y**2


def _bowl_grad(x: float | np.ndarray, y: float | np.ndarray) -> np.ndarray:
    """df/dx = 2x, df/dy = 2y"""
    dx = 2.0 * x
    dy = 2.0 * y
    return np.array([dx, dy], dtype=float)


BOWL_LANDSCAPE = Landscape(
    name="Symmetric Bowl (Paraboloid)",
    id="bowl",
    description=(
        "Convex baseline benchmark with circular contours and a single unique minimum at the origin (0, 0). "
        "Ideal for observing textbook linear convergence without ill-conditioned curvatures."
    ),
    formula_latex=r"f(x, y) = x^2 + y^2",
    equation_str="f(x, y) = x² + y²",
    default_bounds=(-4.0, 4.0, -4.0, 4.0),
    default_start=(3.0, 2.5),
    default_lr=0.1,
    global_min=(0.0, 0.0, 0.0),
    evaluate_fn=_bowl_eval,
    gradient_fn=_bowl_grad,
)


# ---------------------------------------------------------------------------
# Landscape 2: Rosenbrock Valley (Banana Function)
# ---------------------------------------------------------------------------
def _rosenbrock_eval(x: float | np.ndarray, y: float | np.ndarray) -> float | np.ndarray:
    """f(x, y) = (1 - x)^2 + 100 * (y - x^2)^2"""
    return (1.0 - x)**2 + 100.0 * (y - x**2)**2


def _rosenbrock_grad(x: float | np.ndarray, y: float | np.ndarray) -> np.ndarray:
    """
    df/dx = -2(1 - x) - 400x(y - x^2)
    df/dy = 200(y - x^2)
    """
    dx = -2.0 * (1.0 - x) - 400.0 * x * (y - x**2)
    dy = 200.0 * (y - x**2)
    return np.array([dx, dy], dtype=float)


ROSENBROCK_LANDSCAPE = Landscape(
    name="Rosenbrock Valley (Banana Function)",
    id="rosenbrock",
    description=(
        "Classic non-convex benchmark with an ill-conditioned, parabolic valley. "
        "The global minimum is at (1, 1). While finding the valley is easy, navigating along "
        "the flat floor without extreme oscillation or divergence tests step-size sensitivity."
    ),
    formula_latex=r"f(x, y) = (1 - x)^2 + 100(y - x^2)^2",
    equation_str="f(x, y) = (1 - x)² + 100(y - x²)²",
    default_bounds=(-2.0, 2.0, -1.0, 3.0),
    default_start=(-1.5, 2.0),
    default_lr=0.002,
    global_min=(1.0, 1.0, 0.0),
    evaluate_fn=_rosenbrock_eval,
    gradient_fn=_rosenbrock_grad,
)


# ---------------------------------------------------------------------------
# Landscape 3: Ackley's Function (Oscillatory Multimodal Surface)
# ---------------------------------------------------------------------------
def _ackley_eval(x: float | np.ndarray, y: float | np.ndarray) -> float | np.ndarray:
    """
    f(x, y) = -20 * exp(-0.2 * sqrt(0.5*(x^2 + y^2)))
              - exp(0.5 * (cos(2pi*x) + cos(2pi*y))) + e + 20
    """
    r = np.sqrt(0.5 * (x**2 + y**2))
    term1 = -20.0 * np.exp(-0.2 * r)
    term2 = -np.exp(0.5 * (np.cos(2.0 * np.pi * x) + np.cos(2.0 * np.pi * y)))
    return term1 + term2 + np.e + 20.0


def _ackley_grad(x: float | np.ndarray, y: float | np.ndarray) -> np.ndarray:
    """
    Exact analytical gradient for Ackley's function with origin-singularity guard.
    """
    r = np.sqrt(0.5 * (x**2 + y**2))
    exp_radial = np.exp(-0.2 * r)
    exp_trig = np.exp(0.5 * (np.cos(2.0 * np.pi * x) + np.cos(2.0 * np.pi * y)))

    # Handle origin r -> 0 smoothly
    if np.isclose(r, 0.0):
        grad_r_x = 0.0
        grad_r_y = 0.0
    else:
        grad_r_x = (2.0 * x / r) * exp_radial
        grad_r_y = (2.0 * y / r) * exp_radial

    grad_trig_x = np.pi * np.sin(2.0 * np.pi * x) * exp_trig
    grad_trig_y = np.pi * np.sin(2.0 * np.pi * y) * exp_trig

    dx = grad_r_x + grad_trig_x
    dy = grad_r_y + grad_trig_y
    return np.array([dx, dy], dtype=float)


ACKLEY_LANDSCAPE = Landscape(
    name="Ackley's Function (Multimodal Surface)",
    id="ackley",
    description=(
        "Highly oscillatory landscape featuring a nearly flat outer region punctuated by dense concentric "
        "ripples and a sharp central hole at (0, 0). Demonstrates how gradient methods get trapped in local extrema."
    ),
    formula_latex=r"f(x, y) = -20 e^{-0.2\sqrt{0.5(x^2+y^2)}} - e^{0.5(\cos 2\pi x + \cos 2\pi y)} + e + 20",
    equation_str="f(x, y) = -20·exp(-0.2·√(0.5(x²+y²))) - exp(0.5(cos 2πx + cos 2πy)) + e + 20",
    default_bounds=(-4.0, 4.0, -4.0, 4.0),
    default_start=(2.5, 2.5),
    default_lr=0.05,
    global_min=(0.0, 0.0, 0.0),
    evaluate_fn=_ackley_eval,
    gradient_fn=_ackley_grad,
)


# ---------------------------------------------------------------------------
# Landscape 4: Saddle Point (Hyperbolic Paraboloid) - High Value Demonstration
# ---------------------------------------------------------------------------
def _saddle_eval(x: float | np.ndarray, y: float | np.ndarray) -> float | np.ndarray:
    """f(x, y) = x^2 - y^2"""
    return x**2 - y**2


def _saddle_grad(x: float | np.ndarray, y: float | np.ndarray) -> np.ndarray:
    """df/dx = 2x, df/dy = -2y"""
    return np.array([2.0 * x, -2.0 * y], dtype=float)


SADDLE_LANDSCAPE = Landscape(
    name="Hyperbolic Saddle Point",
    id="saddle",
    description=(
        "Showcases curvature duality: along the x-axis the landscape slopes upward (convex), "
        "while along the y-axis it slopes downward (concave). Gradient Descent and Ascent travel in orthogonal directions."
    ),
    formula_latex=r"f(x, y) = x^2 - y^2",
    equation_str="f(x, y) = x² - y²",
    default_bounds=(-3.0, 3.0, -3.0, 3.0),
    default_start=(0.2, 0.2),
    default_lr=0.1,
    global_min=(0.0, 0.0, 0.0),
    evaluate_fn=_saddle_eval,
    gradient_fn=_saddle_grad,
)


LANDSCAPES = {
    "bowl": BOWL_LANDSCAPE,
    "rosenbrock": ROSENBROCK_LANDSCAPE,
    "ackley": ACKLEY_LANDSCAPE,
    "saddle": SADDLE_LANDSCAPE,
}
