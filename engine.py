"""
Pure NumPy Mathematical Optimization Engine.

Implements Gradient Descent and Gradient Ascent from first principles,
providing vectorised updates, convergence criteria checks, explosion/divergence
guards, and comprehensive telemetry history traces.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Tuple, Optional
import numpy as np

from landscapes import Landscape


class OptimizationMode(str, Enum):
    DESCENT = "descent"
    ASCENT = "ascent"


class TerminationStatus(str, Enum):
    CONVERGED = "Converged"
    MAX_ITERATIONS = "Max Iterations Reached"
    DIVERGED = "Diverged (NaN/Inf or Exploded)"


@dataclass
class OptimizationResult:
    """Structured container for single optimization routine output."""
    mode: OptimizationMode
    status: TerminationStatus
    status_message: str
    iterations_completed: int
    # Matrix shape (N, 5): [Iteration, X_coord, Y_coord, Function_Value, Gradient_Norm]
    history: np.ndarray
    final_coordinates: Tuple[float, float]
    final_value: float
    final_gradient_norm: float
    total_path_distance: float
    learning_rate: float
    elapsed_steps: int

    @property
    def x_coords(self) -> np.ndarray:
        return self.history[:, 1]

    @property
    def y_coords(self) -> np.ndarray:
        return self.history[:, 2]

    @property
    def values(self) -> np.ndarray:
        return self.history[:, 3]

    @property
    def grad_norms(self) -> np.ndarray:
        return self.history[:, 4]

    def to_dict(self) -> Dict[str, Any]:
        """Convert result telemetry to serializable dictionary."""
        return {
            "mode": self.mode.value,
            "status": self.status.value,
            "status_message": self.status_message,
            "iterations_completed": self.iterations_completed,
            "final_coordinates": self.final_coordinates,
            "final_value": self.final_value,
            "final_gradient_norm": self.final_gradient_norm,
            "total_path_distance": self.total_path_distance,
            "learning_rate": self.learning_rate,
            "history_shape": self.history.shape,
        }


class OptimizationEngine:
    """
    Decoupled, generic mathematical optimization backend using NumPy vectors.
    
    Supports:
      - Gradient Descent: theta_{t+1} = theta_t - alpha * grad(f(theta_t))
      - Gradient Ascent:  theta_{t+1} = theta_t + alpha * grad(f(theta_t))
      - Automated convergence termination when norm(grad) < tolerance
      - Divergence / Explosion guard against NaN, Inf, and overflow bounds
      - Structured telemetry generation tracking:
        [Iteration, X_coord, Y_coord, Function_Value, Gradient_Norm]
    """

    def __init__(
        self,
        divergence_coord_threshold: float = 1e5,
        divergence_val_threshold: float = 1e12,
    ):
        self.divergence_coord_threshold = divergence_coord_threshold
        self.divergence_val_threshold = divergence_val_threshold

    def step(
        self,
        theta: np.ndarray,
        grad: np.ndarray,
        learning_rate: float,
        mode: OptimizationMode = OptimizationMode.DESCENT,
    ) -> np.ndarray:
        """
        Execute single parameter update step based on optimization mode.
        """
        if mode == OptimizationMode.DESCENT:
            return theta - learning_rate * grad
        elif mode == OptimizationMode.ASCENT:
            return theta + learning_rate * grad
        else:
            raise ValueError(f"Unknown optimization mode: {mode}")

    def optimize(
        self,
        landscape: Landscape,
        initial_point: Tuple[float, float] | np.ndarray,
        mode: OptimizationMode | str = OptimizationMode.DESCENT,
        learning_rate: float = 0.05,
        max_iterations: int = 200,
        tolerance: float = 1e-5,
        clip_gradient: Optional[float] = None,
    ) -> OptimizationResult:
        """
        Run iterative mathematical optimization from start coordinate.

        Parameters
        ----------
        landscape : Landscape
            Mathematical surface providing evaluate(x, y) and gradient(x, y).
        initial_point : (x0, y0)
            Starting parameter vector theta_0.
        mode : OptimizationMode or str
            'descent' (minimization) or 'ascent' (maximization).
        learning_rate : float
            Step size alpha.
        max_iterations : int
            Maximum number of optimization iterations to compute.
        tolerance : float
            Convergence threshold: stops when norm(grad) < tolerance.
        clip_gradient : Optional[float]
            If provided, caps gradient vector norm to prevent gradient explosion.

        Returns
        -------
        OptimizationResult
            Complete optimization telemetry and history trace matrix.
        """
        if isinstance(mode, str):
            mode = OptimizationMode(mode.lower())

        theta = np.array(initial_point, dtype=float).flatten()
        if theta.shape[0] != 2:
            raise ValueError("OptimizationEngine currently operates on 2D vectors [x, y].")

        # Telemetry storage: list of rows [step, x, y, f_val, grad_norm]
        history_records = []
        status = TerminationStatus.MAX_ITERATIONS
        status_msg = f"Reached maximum allowed iterations ({max_iterations})."
        total_distance = 0.0

        for t in range(max_iterations + 1):
            x_curr, y_curr = theta[0], theta[1]

            # 1. Divergence / Explosion check on coordinates
            if (
                np.isnan(theta).any()
                or np.isinf(theta).any()
                or np.max(np.abs(theta)) > self.divergence_coord_threshold
            ):
                status = TerminationStatus.DIVERGED
                status_msg = f"Divergence detected: coordinates exploded or became NaN/Inf at step {t}."
                break

            # 2. Function value evaluation & safety check
            try:
                f_val = float(landscape.evaluate(x_curr, y_curr))
            except Exception as e:
                status = TerminationStatus.DIVERGED
                status_msg = f"Function evaluation failed with error: {str(e)}"
                break

            if np.isnan(f_val) or np.isinf(f_val) or abs(f_val) > self.divergence_val_threshold:
                status = TerminationStatus.DIVERGED
                status_msg = f"Divergence detected: function value f(x, y) = {f_val} exploded at step {t}."
                break

            # 3. Analytic gradient evaluation & safety check
            try:
                grad = np.array(landscape.gradient(x_curr, y_curr), dtype=float).flatten()
            except Exception as e:
                status = TerminationStatus.DIVERGED
                status_msg = f"Gradient evaluation failed with error: {str(e)}"
                break

            if np.isnan(grad).any() or np.isinf(grad).any():
                status = TerminationStatus.DIVERGED
                status_msg = f"Divergence detected: gradient evaluated to NaN/Inf at step {t}."
                break

            grad_norm = float(np.linalg.norm(grad))

            # Record step telemetry: [Iteration, X_coord, Y_coord, Function_Value, Gradient_Norm]
            history_records.append([float(t), x_curr, y_curr, f_val, grad_norm])

            # 4. Convergence check (Gradient norm below tolerance)
            if grad_norm < tolerance:
                status = TerminationStatus.CONVERGED
                status_msg = (
                    f"Converged successfully at step {t}: gradient norm ||∇f|| = {grad_norm:.4e} < {tolerance:.4e}."
                )
                break

            # 5. Stop if we've completed max_iterations steps
            if t == max_iterations:
                break

            # Optional gradient clipping for numerical stability if requested
            if clip_gradient is not None and clip_gradient > 0:
                if grad_norm > clip_gradient:
                    grad = (grad / grad_norm) * clip_gradient

            # 6. Parameter update step
            next_theta = self.step(theta, grad, learning_rate, mode=mode)
            step_distance = float(np.linalg.norm(next_theta - theta))
            total_distance += step_distance
            theta = next_theta

        # Convert history list to structured 2D NumPy array
        if len(history_records) == 0:
            history_matrix = np.zeros((0, 5), dtype=float)
            final_coord = (float(initial_point[0]), float(initial_point[1]))
            final_val = float("nan")
            final_norm = float("nan")
        else:
            history_matrix = np.array(history_records, dtype=float)
            final_coord = (float(history_matrix[-1, 1]), float(history_matrix[-1, 2]))
            final_val = float(history_matrix[-1, 3])
            final_norm = float(history_matrix[-1, 4])

        return OptimizationResult(
            mode=mode,
            status=status,
            status_message=status_msg,
            iterations_completed=len(history_records) - 1 if len(history_records) > 0 else 0,
            history=history_matrix,
            final_coordinates=final_coord,
            final_value=final_val,
            final_gradient_norm=final_norm,
            total_path_distance=total_distance,
            learning_rate=learning_rate,
            elapsed_steps=len(history_records),
        )

    def run_dual(
        self,
        landscape: Landscape,
        initial_point: Tuple[float, float] | np.ndarray,
        learning_rate: float = 0.05,
        max_iterations: int = 200,
        tolerance: float = 1e-5,
        clip_gradient: Optional[float] = None,
    ) -> Tuple[OptimizationResult, OptimizationResult]:
        """
        Execute both Gradient Descent and Gradient Ascent simultaneously
        from the exact same starting coordinates.

        Returns
        -------
        Tuple[OptimizationResult, OptimizationResult]
            (descent_result, ascent_result)
        """
        descent_res = self.optimize(
            landscape=landscape,
            initial_point=initial_point,
            mode=OptimizationMode.DESCENT,
            learning_rate=learning_rate,
            max_iterations=max_iterations,
            tolerance=tolerance,
            clip_gradient=clip_gradient,
        )

        ascent_res = self.optimize(
            landscape=landscape,
            initial_point=initial_point,
            mode=OptimizationMode.ASCENT,
            learning_rate=learning_rate,
            max_iterations=max_iterations,
            tolerance=tolerance,
            clip_gradient=clip_gradient,
        )

        return descent_res, ascent_res
