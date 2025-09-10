# Contributing Guide

Thank you for your interest in contributing to the Resolution Systems Framework! This project uses a dual licensing structure that affects how contributions are handled.

## Licensing for Contributors

By contributing to this repository, you agree that your contributions will be licensed under our dual license structure:

- **Code contributions** (`/engine/`, `/examples/`, `/ui/`, `/configs/`): Licensed under **Apache 2.0**
- **Documentation contributions** (`/docs/`, `/theory/`): Licensed under **CC BY-NC 4.0**

See [NOTICE.md](NOTICE.md) for complete details.

## How to Contribute

### 1. Code Contributions
- **Scope**: Engine implementation, examples, UI components, configuration templates
- **License**: Apache 2.0 (commercial use encouraged)
- **Focus**: Bug fixes, performance improvements, new features, testing

### 2. Documentation Contributions
- **Scope**: Theory, axioms, patterns, ethics, educational content
- **License**: CC BY-NC 4.0 (non-commercial with attribution)
- **Focus**: Clarity, accuracy, educational value, theoretical development

### 3. Mixed Contributions
If your contribution spans both code and documentation:
- Code portions will be Apache 2.0 licensed
- Documentation portions will be CC BY-NC 4.0 licensed
- Clearly indicate which parts are which in your PR description

## Development Setup

### Prerequisites
- Python 3.8+
- Git
- Text editor or IDE

### Local Setup
```bash
# Clone the repository
git clone https://github.com/[username]/resolution-systems.git
cd resolution-systems

# Set up Python environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r engine/requirements.txt

# Test the installation
cd engine
python cli.py run --config configs/littering.yml
```

## Pull Request Process

### Before Submitting
1. **Test your changes**: Ensure code runs without errors
2. **Update documentation**: If you change functionality, update relevant docs
3. **Check licensing**: Confirm you understand which license applies to your changes
4. **Follow conventions**: Use consistent code style and documentation format

### PR Submission
1. **Fork** the repository
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes** with clear, atomic commits
4. **Write descriptive commit messages**
5. **Push** to your fork: `git push origin feature/your-feature-name`
6. **Open a Pull Request** with:
   - Clear title and description
   - Reference any related issues
   - Specify if changes affect code, docs, or both
   - Confirm you agree to dual licensing

### Review Process
- Maintainers will review for technical correctness, licensing compliance, and project alignment
- Code changes require functional testing
- Documentation changes require accuracy and clarity review
- Large changes may require discussion before implementation

## Types of Contributions

### 🐛 Bug Reports
- Use GitHub Issues with the bug template
- Include reproduction steps and system information
- Check if the issue exists in the latest version

### 💡 Feature Requests
- Use GitHub Issues with the feature template
- Describe the use case and expected behavior
- Consider if it fits the project's scope and philosophy

### 📚 Documentation Improvements
- Fix typos, improve clarity, add examples
- Ensure mathematical notation is correct
- Maintain consistency with existing style

### 🔬 Research Contributions
- Theoretical improvements to the resolution framework
- New applications or use cases
- Academic collaborations and citations

### 🛠️ Code Improvements
- Performance optimizations
- New algorithms or controllers
- Better error handling and validation
- Testing and quality improvements

## Code Style Guidelines

### Python Code
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Include docstrings for public functions and classes
- Keep functions focused and well-named

### Documentation
- Use clear, concise language
- Include examples where helpful
- Maintain consistent formatting
- Cite sources for theoretical claims

## Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Create a GitHub Issue
- **Ideas**: Start with a GitHub Discussion before creating features
- **Academic Collaboration**: Contact maintainers directly

## Recognition

Contributors will be acknowledged in:
- CHANGELOG.md for significant contributions
- Academic papers citing contributor work where appropriate
- GitHub contributor listings

Thank you for helping make the Resolution Systems Framework better! 🎯
