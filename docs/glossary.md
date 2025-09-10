# Glossary

A working vocabulary for the **CFAR Framework** (Constraint-Fluctuation-Attention-Resolution).  
This is a living document — extend it as concepts evolve.

---

## Core Concepts

**Constraint (C)**  
Structural limits and affordances that shape behavior. Includes rules, laws, default settings, design features, enforcement presence.  
*Analogous to:* viscosity or channel walls in fluid dynamics; aperture stop in optics.

**Fluctuation (F)**  
Variability, randomness, and turbulence in the system. Can be noise, novelty, exploration, or instability.  
*Analogous to:* turbulence in fluids; stochastic jitter in signals.

**Attention (A)**  
Salience and amplification of norms, signals, and cues. Campaigns, prompts, media visibility, and social proof.  
*Analogous to:* light intensity or pressure driving flow.

**Norm (N)**  
Shared belief or expectation about how others behave. Updates dynamically based on observed outcomes.

**Burden (B)**  
Perceived cost, hassle, or fatigue associated with interventions. Rising burden predicts backlash or dropout.

---

## Resolution Analogies

**Rayleigh Criterion**  
In optics: the minimum resolvable feature size is proportional to wavelength / numerical aperture.  
In social systems: the minimum resolvable change is proportional to intervention granularity / sensing-actuation capacity.

**ΔY_min (Minimum Resolvable Change)**  
The smallest reliable shift in outcome the system can detect and control.  
\[
\Delta Y_{\min} \approx k_1 \cdot \frac{\lambda_{\text{eff}}}{\mathrm{NA}_{\text{eff}}}
\]

**Numerical Aperture (NA_eff)**  
Effective “aperture” of the system: how finely it can sense (data richness, feedback speed) and act (number + precision of levers).

**λ_eff (Effective Wavelength)**  
Granularity and cadence of interventions. Longer λ = broad campaigns; shorter λ = micro-timed, targeted pulses.

**k₁ (Process Factor)**  
Slack variable capturing unpredictability: habituation, operational variance, residual model error.

**Depth of Focus (DOF)**  
Robustness margin of an intervention. High NA improves resolution but narrows tolerance to drift, just as in optics.

---

## Control Architecture

**PID Controller**  
Proportional–Integral–Derivative control loop applied to medium/slow levers (laws, defaults, infrastructure).  
- P: respond to error immediately.  
- I: accumulate error and correct drift.  
- D: damp overshoot and oscillation.

**Multi-Armed Bandit**  
Adaptive algorithm for fast levers (messages, prompts, channels). Balances exploration vs. exploitation to avoid habituation.

**Guardrails**  
Automatic checks for equity gaps, burden thresholds, cost ceilings, or oscillatory instability. Trigger rollback or pause if exceeded.

**Deadband**  
Range of error around the target in which the controller takes no action, preventing thrash.

**Hysteresis**  
Intentional lag in switching direction to avoid flip-flopping behavior.

**Change Budget**  
Maximum allowed adjustment per cycle. Ensures stability and prevents overwhelming users or operations.

RFC (Request for Comments)

Purpose: a structured proposal for a new idea, feature, or change.

Format: usually a markdown doc with background, motivation, design details, pros/cons, and open questions.

Workflow:

Someone writes an RFC draft.

It’s circulated for review/discussion (“request for comments”).

After feedback, the team accepts/rejects/archives it.

Think of RFCs as living proposals — the place where exploration and debate happens before implementation.

ADR (Architecture Decision Record)

Purpose: a permanent record of a design or architecture choice that has been made.

Format: very short markdown doc (~1 page), usually with these sections:

Context

Decision

Status (accepted, superseded, deprecated)

Consequences (positive and negative)

Workflow:

Once an RFC or discussion resolves into a final decision, you capture it as an ADR.

Think of ADRs as committed history — the logbook of why the system looks the way it does.

---

## Meta Concepts

**Cognitive Resolution**  
The limit of human/group capacity to meaningfully process complexity. If a problem is scoped finer than this limit, participation degrades into disengagement or oversimplification.

**Cognitive Bandwidth Matcher**  
A scoping tool that decomposes problems to match group capacity, surfaces only resolvable units, and shows connections to larger patterns.

**CFAR Framework**  
The Constraint-Fluctuation-Attention-Resolution paradigm: design problems and interventions so they respect the system's resolution limits (optical, social, cognitive).

---
