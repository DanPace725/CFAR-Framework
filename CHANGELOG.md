# Changelog

<!-- Release history and notable changes -->

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **MAJOR**: Fluctuation Control System - Complete implementation of engineered gradient creation
  - Added `uF` (fluctuation control) as first-class control input to system dynamics
  - Implemented `FluctuationController` class with attention trap detection
  - Added Rayleigh-gated strategy switching between precision (PID) and fluctuation modes
  - Created gradient strength calculation based on attention, constraint decay, and system stall
  - Added attention trap detector for high A + flat dY/dt + declining C scenarios
  - Enhanced CLI output to show control mode indicators [P]recision vs [F]luctuation
  - Added fluctuation pulse tracking and cooldown management
  - Improved resolution parameters (ΔY_min reduced from ~0.787 to ~0.247)

### Changed
- **BREAKING**: Renamed project to "CFAR Framework" (Constraint-Fluctuation-Attention-Resolution)
  - Updated all documentation, code comments, and user-facing text
  - Changed repository name references to `cfar-framework`
  - Updated CLI description and application titles
  - Enhanced branding consistency across all materials
- **BREAKING**: Implemented dual licensing structure
  - Code (`/engine/`, `/examples/`, `/ui/`, `/configs/`): Apache 2.0 license
  - Documentation/Theory (`/docs/`, `/theory/`): CC BY-NC 4.0 license
  - Updated README.md, CITATION.cff, and CONTRIBUTING.md to reflect dual licensing
  - Added NOTICE.md with comprehensive licensing guidance
  - Replaced single LICENSE file with LICENSE-CODE and docs/LICENSE-DOCS
- **Enhanced System Dynamics**: Extended `step()` function to support fluctuation control
  - Added gradient strength calculation and engineered variance injection
  - Updated cost function to include fluctuation intervention costs
  - Improved parameter estimation for better resolution (NA_eff, λ_eff, k₁)

### Technical Implementation
- **Bimodal Control Strategy**: System automatically switches between precision and fluctuation modes
- **Attention Ecology**: Implements attention-as-energy-flow principles from theoretical foundation
- **Gradient Engineering**: Creates curvature in attention landscape when precision is blocked
- **Resolution-Aware Control**: Respects Rayleigh limits while providing alternative pathways

## [0.1.0] - 2024-09-10
### Added
- **Complete Repository Structure**: Implemented full directory structure as specified in Seed Doc
- **Core Documentation**:
  - Updated README.md with TL;DR, paradigm description, and quickstart instructions
  - Comprehensive glossary with CFA framework definitions and resolution analogies
  - Requirements document (REQUIREMENTS.md) with functional, technical, and non-functional specifications
  - Theory documentation with axioms and mathematical foundations
- **Resolution Engine Implementation**:
  - `State` dataclass with Y, N, A, C, B state variables
  - Complete system dynamics with sigmoid outcome model and CFA updates
  - Parameter estimation functions for NA_eff, λ_eff, k₁, and ΔY_min calculation
  - PID controller with deadband, hysteresis, and resolution-aware control
  - Thompson Sampling bandit for fast intervention selection
  - Guardrails system framework for equity, burden, and oscillation checks
  - Action planner for coordinating PID and bandit outputs
- **CLI Interface**:
  - Functional command-line interface for running simulations
  - Complete demo loop with parameter estimation and control coordination
  - Progress logging with all key system metrics
- **Configuration System**:
  - YAML-based configuration with littering example
  - Configurable system parameters, controller gains, and intervention arms
  - Parameter estimation inputs and reward thresholds
- **Example Applications**:
  - Littering resolution system notebook placeholder
  - Seatbelt usage resolution system notebook placeholder
  - Dashboard framework with Streamlit application structure
- **Project Infrastructure**:
  - GitHub workflows for CI/CD
  - Issue templates for bugs, features, and RFCs
  - Contributing guidelines and governance documentation
  - License and citation files
  - Comprehensive requirements.txt with all dependencies

### Technical Implementation
- **Mathematical Core**: Implemented Rayleigh criterion (ΔY_min ≈ k₁·λ_eff / NA_eff)
- **Control Architecture**: Dual controller system with PID for structural changes and bandits for fast interventions
- **System Dynamics**: Full CFA model with constraint-fluctuation-attention framework
- **Resolution Limits**: Automatic calculation and enforcement of minimum resolvable changes
- **Guardrails**: Framework for equity, burden monitoring, and stability checks

### Fixed
- Import errors in guardrails.py and planner.py (SystemState → State)
- Module dependencies and circular import issues
- CLI argument parsing and simulation execution

### Validated
- ✅ Complete 90-day littering simulation runs successfully
- ✅ All core algorithms implemented and functional
- ✅ Parameter estimation and control coordination working
- ✅ System demonstrates expected behavior patterns (early improvement, constraint decay, attention saturation)

## [0.0.1] - 2024-09-10
### Added
- Initial repository setup
- Basic directory structure from Seed Doc
- Placeholder documentation files
