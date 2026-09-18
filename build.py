"""Create Vercel's static deployment directory from the frontend source."""

from pathlib import Path
from shutil import copytree, rmtree

root = Path(__file__).parent
output = root / "public"
source = root / "frontend"

if output.exists():
    rmtree(output)
copytree(source, output)
