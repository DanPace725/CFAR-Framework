# Axioms

<!-- Minimal assumptions & invariants -->

## Core Resolution Principles

### 1. Resolution Limits
Systems have **resolution limits**; pushing finer than the limit yields blur/oscillation.

### 2. Numerical Aperture (NA_eff)
**NA_eff** (aperture) rises with sensing richness + actuation addressability.

### 3. Effective Wavelength (λ_eff)
**λ_eff** (wavelength) is intervention granularity/cadence.

### 4. Process Uncertainty (k₁)
**k₁** is process uncertainty (habituation, ops error, model misspec).

### 5. Minimum Controllable Change
Minimum controllable change: **ΔY_min ≈ k₁·λ_eff / NA_eff**.

### 6. Controller Constraints
Controller enforces **deadbands**, **hysteresis**, **change budgets**, **guardrails**.

## System Invariants

### Invariant 1: Rayleigh Bound
No intervention can reliably produce changes smaller than ΔY_min without risking system instability.

### Invariant 2: Conservation of Attention
Total system attention is bounded; increasing focus in one area necessarily decreases it elsewhere.

### Invariant 3: Burden Accumulation
System burden B accumulates with intervention intensity and decays slowly, requiring active management.

## Mathematical Foundation

The core relationship governing resolution systems:

```
ΔY_min = k₁ · λ_eff / NA_eff
```

Where:
- **ΔY_min**: Minimum resolvable change in outcome
- **k₁**: Process factor (uncertainty, habituation, operational variance)
- **λ_eff**: Effective wavelength (intervention granularity/cadence)
- **NA_eff**: Numerical aperture (sensing × actuation capacity)

This relationship directly parallels the Rayleigh criterion in optics, establishing fundamental limits on system resolution.
