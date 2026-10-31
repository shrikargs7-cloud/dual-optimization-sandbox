"""
Unit tests for Dual-Optimization Sandbox (Descent vs. Ascent).
"""

import unittest
import numpy as np
from landscapes import LANDSCAPES, BOWL_LANDSCAPE, ROSENBROCK_LANDSCAPE, ACKLEY_LANDSCAPE
from engine import OptimizationEngine, OptimizationMode, TerminationStatus


class TestOptimizationLandscapes(unittest.TestCase):
    def test_gradients_numerical_accuracy(self):
        """Check all analytical gradients against two-point finite difference."""
        eps = 1e-7
        test_points = [
            (0.5, 0.5),
            (-1.5, 2.0),
            (1.0, 1.0),
            (0.1, -0.2),
            (-2.0, -1.5),
        ]
        for name, landscape in LANDSCAPES.items():
            for x, y in test_points:
                ana_grad = landscape.gradient(x, y)
                fx_p = landscape.evaluate(x + eps, y)
                fx_m = landscape.evaluate(x - eps, y)
                fy_p = landscape.evaluate(x, y + eps)
                fy_m = landscape.evaluate(x, y - eps)
                num_grad = np.array([(fx_p - fx_m) / (2 * eps), (fy_p - fy_m) / (2 * eps)])
                diff = np.linalg.norm(ana_grad - num_grad)
                self.assertLess(
                    diff,
                    1e-4,
                    f"Gradient mismatch for {name} at ({x}, {y}): analytic={ana_grad}, numeric={num_grad}",
                )

    def test_bowl_minimum(self):
        self.assertAlmostEqual(BOWL_LANDSCAPE.evaluate(0.0, 0.0), 0.0)
        grad = BOWL_LANDSCAPE.gradient(0.0, 0.0)
        self.assertAlmostEqual(np.linalg.norm(grad), 0.0)

    def test_rosenbrock_minimum(self):
        self.assertAlmostEqual(ROSENBROCK_LANDSCAPE.evaluate(1.0, 1.0), 0.0)
        grad = ROSENBROCK_LANDSCAPE.gradient(1.0, 1.0)
        self.assertAlmostEqual(np.linalg.norm(grad), 0.0)


class TestOptimizationEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OptimizationEngine()

    def test_bowl_convergence(self):
        """Gradient descent on paraboloid should converge to (0,0)."""
        res = self.engine.optimize(
            landscape=BOWL_LANDSCAPE,
            initial_point=(3.0, 4.0),
            mode=OptimizationMode.DESCENT,
            learning_rate=0.1,
            max_iterations=100,
            tolerance=1e-5,
        )
        self.assertEqual(res.status, TerminationStatus.CONVERGED)
        self.assertAlmostEqual(res.final_coordinates[0], 0.0, places=3)
        self.assertAlmostEqual(res.final_coordinates[1], 0.0, places=3)
        self.assertLess(res.final_gradient_norm, 1e-5)
        # Check output matrix columns: [Iteration, X, Y, Val, GradNorm]
        self.assertEqual(res.history.shape[1], 5)
        self.assertEqual(res.history[0, 0], 0.0)
        self.assertAlmostEqual(res.history[0, 1], 3.0)
        self.assertAlmostEqual(res.history[0, 2], 4.0)

    def test_divergence_safety_guard(self):
        """Gradient ascent on unbounded paraboloid must trigger divergence safety."""
        res = self.engine.optimize(
            landscape=BOWL_LANDSCAPE,
            initial_point=(2.0, 2.0),
            mode=OptimizationMode.ASCENT,
            learning_rate=0.5,
            max_iterations=100,
        )
        self.assertEqual(res.status, TerminationStatus.DIVERGED)
        self.assertIn("Divergence", res.status_message)

    def test_dual_run_consistency(self):
        """Dual run should produce simultaneous descent and ascent results."""
        desc, asc = self.engine.run_dual(
            landscape=BOWL_LANDSCAPE,
            initial_point=(2.0, 2.0),
            learning_rate=0.05,
            max_iterations=50,
        )
        self.assertEqual(desc.mode, OptimizationMode.DESCENT)
        self.assertEqual(asc.mode, OptimizationMode.ASCENT)
        self.assertAlmostEqual(desc.history[0, 1], 2.0)
        self.assertAlmostEqual(asc.history[0, 1], 2.0)
        # Descent final value should be lower than initial
        self.assertLess(desc.final_value, desc.history[0, 3])
        # Ascent final value should be higher than initial
        self.assertGreater(asc.final_value, asc.history[0, 3])


if __name__ == "__main__":
    unittest.main()
