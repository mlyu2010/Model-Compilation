#!/usr/bin/env python3
"""
Documentation generation script using pdoc3.

This script generates HTML documentation from the codebase docstrings.
Run with: python scripts/generate_docs.py
"""

import subprocess
import sys
from pathlib import Path


def generate_documentation():
    """Generate HTML documentation using pdoc3."""
    print("Generating documentation...")

    # Get project root
    project_root = Path(__file__).parent.parent
    docs_output = project_root / "docs"

    # Create docs directory if it doesn't exist
    docs_output.mkdir(exist_ok=True)

    # Generate documentation
    try:
        cmd = [
            "pdoc3",
            "--html",
            "--output-dir",
            str(docs_output),
            "--force",
            "app",
        ]

        result = subprocess.run(
            cmd,
            cwd=project_root,
            capture_output=True,
            text=True,
            check=True,
        )

        print(f"Documentation generated successfully in: {docs_output}")
        print(f"Open {docs_output}/app/index.html in your browser to view.")

        return 0

    except subprocess.CalledProcessError as e:
        print(f"Error generating documentation: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return 1
    except FileNotFoundError:
        print("Error: pdoc3 not found. Install with: pip install pdoc3")
        return 1


if __name__ == "__main__":
    sys.exit(generate_documentation())
