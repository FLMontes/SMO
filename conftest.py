# Permite que pytest encuentre el paquete smo dentro de src/ sin instalarlo.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))
