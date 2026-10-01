"""Punto de entrada: corre el flujo completo del PMV.

    python ejecutar.py                 # usa config/config.yaml
    python ejecutar.py --config X.yaml
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from smo.pipeline import main  # noqa: E402

if __name__ == "__main__":
    main()
