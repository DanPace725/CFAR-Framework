Repo Structure: 
resolution-systems/
├─ README.md                    # What/why, 2-minute tour, quickstart
├─ LICENSE
├─ CODE_OF_CONDUCT.md
├─ CONTRIBUTING.md
├─ GOVERNANCE.md                # Lightweight: decision rules, RFCs, releases
├─ CHANGELOG.md
├─ CITATION.cff
├─ docs/                        # MkDocs (or Docusaurus) site
│  ├─ index.md                  # Overview + mental models
│  ├─ whitepaper.md             # Polished narrative & figures
│  ├─ glossary.md               # Shared vocabulary (C, F, A, NA, λ, k₁…)
│  ├─ patterns.md               # Design patterns & antipatterns
│  ├─ ethics.md                 # Equity, burden, guardrails
│  ├─ rfc/                      # Design proposals (numbered)
│  └─ figures/                  # Diagrams/plots
├─ theory/                      # “Source of truth” for the paradigm
│  ├─ axioms.md                 # Minimal assumptions & invariants
│  ├─ rayleigh-analogy.md       # Mapping from optics → incentives → cognition
│  ├─ state-model.md            # S, Y, N, A, C, B dynamics & parameters
│  ├─ control-arch.md           # PID + bandit + guardrails
│  └─ adr/                      # Architecture Decision Records (ADRs)
├─ engine/                      # Python package: the controller & simulators
│  ├─ resolution_engine/
│  │  ├─ __init__.py
│  │  ├─ state.py               # dataclasses for S_t
│  │  ├─ dynamics.py            # updates for N,A,C,B; noise; costs
│  │  ├─ estimator.py           # estimate NA_eff, λ_eff, k1 from logs
│  │  ├─ controller_pid.py      # PID with deadband/hysteresis
│  │  ├─ controller_bandit.py   # contextual TS/LinUCB + fairness
│  │  ├─ guardrails.py          # equity, burden, spend, oscillation checks
│  │  ├─ planner.py             # merges controller outputs → action plan
│  │  └─ io.py                  # config, logging, audit ledger
│  ├─ configs/                  # YAML project configs (littering, seatbelts…)
│  ├─ cli.py                    # `resys run --config configs/littering.yml`
│  └─ requirements.txt
├─ examples/
│  ├─ littering.ipynb
│  ├─ seatbelts.ipynb
│  └─ dashboards/               # simple Streamlit dashboards
├─ prompts/
│  ├─ system/                   # durable LLM instructions (editing safe)
│  ├─ tasks/                    # “write RFC”, “draft ADR”, “explain figure”
│  └─ style/                    # voice, formatting, citation norms
├─ .github/
│  ├─ workflows/ci.yml          # tests + lint + docs build
│  └─ ISSUE_TEMPLATE/           # bug/feature/RFC templates
└─ ui/                          # optional: small React/Streamlit app
   ├─ streamlit_app.py
   └─ api/ (FastAPI stub)


Core Docs: 
README.md (starter)
# Resolution Systems: A Paradigm & Engine

**TL;DR**: A practical framework for matching *problem resolution* to *system capacity*.
We model behavior with Constraint–Fluctuation–Attention (CFA) and enforce a Rayleigh-style
limit: don’t “print” patterns finer than the system can resolve.

- **Paradigm**: optics → incentives → cognition (Rayleigh analogies)
- **Engine**: PID (slow/medium levers) + bandits (fast levers) + guardrails
- **Outcome**: stable behavior change without relying on money-only incentives

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r engine/requirements.txt
python -m engine.cli run --config engine/configs/littering.yml

Links

docs: docs/ (MkDocs)

theory: theory/

examples: examples/


### `theory/axioms.md` (essentials)
- Systems have **resolution limits**; pushing finer than the limit yields blur/oscillation.  
- **NA_eff** (aperture) rises with sensing richness + actuation addressability.  
- **λ_eff** (wavelength) is intervention granularity/cadence.  
- **k₁** is process uncertainty (habituation, ops error, model misspec).  
- Minimum controllable change: **ΔY_min ≈ k₁·λ_eff / NA_eff**.  
- Controller enforces **deadbands**, **hysteresis**, **change budgets**, **guardrails**.

---

## Minimal engine scaffolding (ready to paste)

### `engine/resolution_engine/state.py`
```python
from dataclasses import dataclass

@dataclass
class State:
    Y: float   # outcome (0..1)
    N: float   # norm
    A: float   # attention
    C: float   # constraint
    B: float   # burden

engine/resolution_engine/dynamics.py
import numpy as np
from .state import State

def sigma(x): return 1/(1+np.exp(-x))

def step(state: State, uA: float, uC: float, eps=0.0,
         beta=( -0.5, 3.0, 2.0, 2.0, 1.5 ), # β0, βN, βA, βC, βB
         eta=0.2, rho=0.9, deltaC=0.02, kappa=0.3):
    β0, βN, βA, βC, βB = beta
    Y = sigma(β0 + βN*state.N + βA*state.A + βC*state.C - βB*state.B + eps)
    N = (1-eta)*state.N + eta*Y
    A = rho*state.A + uA
    C = state.C + uC - deltaC
    B = (1-kappa)*state.B + kappa*cost(uA, uC)
    return State(Y=Y, N=N, A=A, C=C, B=B)

def cost(uA, uC): return 0.6*abs(uA) + 1.0*abs(uC)

engine/resolution_engine/estimator.py
import numpy as np

def estimate_na_eff(sensing_features:int, actuation_channels:int, feedback_latency_days:float):
    # simple monotone proxy in [0,1]
    s = np.tanh(0.15*sensing_features)
    a = np.tanh(0.25*actuation_channels)
    l = 1.0/ (1.0 + 0.1*feedback_latency_days)
    return np.clip(0.5*(s+a)*l, 0, 1)

def estimate_lambda_eff(cadence_days:float, spatial_scale_km:float):
    # dominant scale normalized to ~[0.1, 2]
    t = max(cadence_days, 1.0)/7.0
    x = max(spatial_scale_km, 0.1)/1.0
    return 0.5*(t+x)

def estimate_k1(residual_std:float, ops_variance:float, habituation_rate:float):
    return np.clip(0.3 + 0.7*np.tanh( residual_std + ops_variance + 2*habituation_rate ), 0.2, 2.0)

def min_resolvable_deltaY(na_eff, lam_eff, k1):  # ΔY_min
    if na_eff <= 1e-6: return 1.0
    return np.clip(k1 * lam_eff / na_eff, 0.001, 1.0)

engine/resolution_engine/controller_pid.py
class PID:
    def __init__(self, kp, ki, kd, deadband=0.005, max_step=0.1, hysteresis=0.01):
        self.kp, self.ki, self.kd = kp, ki, kd
        self.i = 0.0
        self.prev_e = 0.0
        self.deadband = deadband
        self.max_step = max_step
        self.hysteresis = hysteresis

    def __call__(self, error, deltaY_min):
        # deadband widened by resolution limit
        band = max(self.deadband, deltaY_min)
        if abs(error) < band: return 0.0
        self.i += error
        d = error - self.prev_e
        self.prev_e = error
        u = self.kp*error + self.ki*self.i + self.kd*d
        # hysteresis: soften direction flips
        if abs(d) > self.hysteresis: u *= 0.7
        return max(-self.max_step, min(self.max_step, u))

engine/resolution_engine/controller_bandit.py (stub)
import numpy as np
class ThompsonBandit:
    def __init__(self, n_arms, prior_alpha=1.0, prior_beta=1.0):
        self.a = np.ones(n_arms)*prior_alpha
        self.b = np.ones(n_arms)*prior_beta

    def select(self):
        return np.argmax(np.random.beta(self.a, self.b))

    def update(self, arm, reward):
        self.a[arm] += reward
        self.b[arm] += (1-reward)

engine/cli.py (demo loop)
import argparse, yaml, numpy as np
from resolution_engine.state import State
from resolution_engine.dynamics import step
from resolution_engine.estimator import *
from resolution_engine.controller_pid import PID
from resolution_engine.controller_bandit import ThompsonBandit

def run(path):
    cfg = yaml.safe_load(open(path))
    s = State(**cfg["init_state"])
    pid = PID(**cfg["pid"])
    bandit = ThompsonBandit(n_arms=len(cfg["fast_arms"]))
    target = cfg["target_Y"]

    for t in range(cfg["horizon_days"]):
        na = estimate_na_eff(**cfg["na_inputs"])
        lam = estimate_lambda_eff(**cfg["lambda_inputs"])
        k1  = estimate_k1(**cfg["k1_inputs"])
        dYmin = min_resolvable_deltaY(na, lam, k1)

        e = target - s.Y
        uC = pid(e, dYmin)                  # structural adjustment
        arm = bandit.select()               # choose message/frame
        uA = cfg["fast_arms"][arm]["dose"]

        s = step(s, uA=uA, uC=uC, eps=np.random.normal(0, 0.02))
        reward = float(s.Y > cfg["reward_threshold"])  # toy reward
        bandit.update(arm, reward)

        print(f"day {t:03d}  Y={s.Y:.3f}  N={s.N:.3f}  A={s.A:.3f}  C={s.C:.3f}  ΔYmin={dYmin:.3f}  uC={uC:+.3f}  arm={arm}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--config", required=True)
    args = ap.parse_args()
    run(args.config)

engine/configs/littering.yml (example)
target_Y: 0.95
horizon_days: 90
init_state: {Y: 0.80, N: 0.50, A: 0.10, C: 0.30, B: 0.20}
pid: {kp: 0.8, ki: 0.2, kd: 0.1, deadband: 0.01, max_step: 0.08, hysteresis: 0.02}
fast_arms:
  - {name: "injunctive", dose: 0.10}
  - {name: "descriptive", dose: 0.10}
  - {name: "identity",   dose: 0.10}
na_inputs: {sensing_features: 8, actuation_channels: 3, feedback_latency_days: 3}
lambda_inputs: {cadence_days: 7, spatial_scale_km: 1.0}
k1_inputs: {residual_std: 0.08, ops_variance: 0.05, habituation_rate: 0.04}
reward_threshold: 0.92