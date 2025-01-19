# NTRU Python Implementation

SageMath tests require that `sage.all` is accessible within `python3` environment. In order to run `test_sage`, pytest must be present in sage `venv` and executed as a module inside sage python.

```bash
# Install pytest inside sage-python environment
sage -python -m pip install pytest

# Run tests using sage-python pytest module
sage -python -m pytest
```
