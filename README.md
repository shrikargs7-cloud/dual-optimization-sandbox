# Dual-Optimization Sandbox (Descent vs. Ascent)

An interactive educational dashboard and simulation engine designed to demonstrate mathematical optimization from first principles using pure **NumPy**, **Plotly**, and **Streamlit**.

It visualizes the operational duality between **Gradient Descent** (minimizing a cost/loss landscape) and **Gradient Ascent** (maximizing an objective/reward landscape) on the exact same coordinate system.

---

## ⚡ Mathematical Duality

Given a differentiable landscape $f(\theta)$ where $\theta = (x, y)^\top \in \mathbb{R}^2$:

- **Gradient Descent (Minimizer)**:
  $$\theta_{t+1} = \theta_t - \alpha \nabla f(\theta_t)$$
  Follows the direction of steepest rate of decrease, descending into valleys and local/global minima.
  *Drawn as an **Electric Cyan (`#00F0FF`)** trail.*

- **Gradient Ascent (Maximizer)**:
  $$\theta_{t+1} = \theta_t + \alpha \nabla f(\theta_t)$$
  Follows the direction of steepest rate of increase, climbing toward peaks, ridges, or diverging to infinity.
  *Drawn as an **Intense Magenta (`#FF007A`)** trail.*

---

## 🏗️ Project Architecture

```
dual_optimization_project/
├── app.py              # Full-featured Streamlit UI with 3 structural panels
├── engine.py           # Pure NumPy vectorized optimization backend & divergence guards
├── landscapes.py       # Mathematical surfaces with exact analytic gradients
├── test_engine.py      # Unit test suite verifying finite-difference gradients & convergence
└── requirements.txt    # Minimal dependencies
```

### 1. Optimization Backend (`engine.py`)
- Generic, decoupled Python class `OptimizationEngine` written in pure vectorized NumPy.
- Convergence termination check: $\|\nabla f(\theta_t)\| < \text{tolerance}$.
- Divergence & explosion protection: Immediate break on `np.isnan`, `np.isinf`, or coordinate/value runaway.
- Returns structured NumPy matrices tracking:
  `[Iteration, X_coord, Y_coord, Function_Value, Gradient_Norm]`

### 2. Mathematical Topologies (`landscapes.py`)
- **Symmetric Bowl (Paraboloid)**:
  $$f(x, y) = x^2 + y^2 \quad \Longrightarrow \quad \nabla f = [2x, 2y]^\top$$
- **Rosenbrock Valley (Banana Function)**:
  $$f(x, y) = (1 - x)^2 + 100(y - x^2)^2 \quad \Longrightarrow \quad \nabla f = [-2(1-x) - 400x(y-x^2), 200(y-x^2)]^\top$$
- **Ackley's Function (Multimodal Surface)**:
  $$f(x, y) = -20 \exp\left(-0.2\sqrt{0.5(x^2+y^2)}\right) - \exp\left(0.5(\cos 2\pi x + \cos 2\pi y)\right) + e + 20$$
- **Hyperbolic Saddle Point**:
  $$f(x, y) = x^2 - y^2 \quad \Longrightarrow \quad \nabla f = [2x, -2y]^\top$$

### 3. User Interface (`app.py`)
Divided into three distinct structural panels with a clean **Light Theme** (and built-in theme toggle):
1. **Left Control Panel (Sidebar)**: Theme selector (Light / Dark), landscape selector, initial coordinate inputs $(x_0, y_0)$, learning rate slider ($\alpha \in [0.001, 1.5]$), max iterations slider ($[10, 500]$), and tolerance options.
2. **Center Plot Canvas**: Interactive 2D contour map (and 3D surface view tab) with click-to-pick coordinates, live trajectory trails, step scrubber playback, and coordinate hovering.
3. **Right Telemetry Panel**: Live metric cards displaying convergence state, final coordinates, function values, gradient norms, path distance, and interactive convergence charts.

---

## 🚀 Getting Started

### Installation
```bash
cd dual_optimization_project
pip install -r requirements.txt
```

### Run the Interactive Dashboard
```bash
streamlit run app.py
```

### Run Unit Tests
```bash
python3 -m unittest discover -s . -p "test_*.py"
```


---

## 🔄 Optimization Engine Workflow

```mermaid
flowchart TD
    Init[User Inputs Objective Function f(x, y) & Hyperparameters] --> Engine[NumPy Optimization Kernel]
    
    subgraph Computational Pipeline
        Engine --> GradCalc[Vectorized Gradient Evaluation]
        
        GradCalc --> DescentBranch[📉 Gradient Descent Step: x := x - α * ∇f]
        GradCalc --> AscentBranch[📈 Gradient Ascent Step: x := x + α * ∇f]
        
        DescentBranch --> Minima[Converges toward Local/Global Minimum]
        AscentBranch --> Maxima[Converges toward Local/Global Maximum]
    end

    subgraph Visualization & Analytics
        Minima & Maxima --> Plotly3D[Plotly 3D Surface & Contour Maps]
        Minima & Maxima --> Metrics[Loss/Objective Curve vs. Iteration Step]
    end

    Plotly3D & Metrics --> StreamlitUI[Interactive Streamlit Dashboard]
```
