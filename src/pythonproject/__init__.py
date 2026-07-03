from .dsl import (
    project,
    build_system,
    dependency_group,
    tool,
    version,
    v,
    dependency,
    dep,
    BuildSystem,
    Hatchling,
    setuptools,
    Flit,
    PDM,
    uv_build,
)


__all__ = [
    "project",
    "build_system",
    "dependency_group",
    "tool",
    "version",
    "v",
    "dependency",
    "dep",
    "BuildSystem",
    "Hatchling",
    "setuptools",
    "Flit",
    "PDM",
    "uv_build",
]


# ----


from pathlib import Path
import sys
import atexit
import inspect

from .registry import __REGISTRY
from .validator import PyProjectASTValidator
from .serializer import serialize_to_toml


def _detect_caller() -> str | None:
    """Inspects execution states to locate the targeting pyproject.py file."""
    main_module = sys.modules.get("__main__")

    if main_module is not None:
        main_file = getattr(main_module, "__file__", None)

        if isinstance(main_file, str):
            return str(Path(main_file).resolve())

    for frame_info in inspect.stack():
        filename = frame_info.filename

        return str(Path(filename).resolve())
    return None


# 3. Secure Hook Setup on Import
_caller_file = _detect_caller()

if _caller_file:
    # Immediately trigger AST check BEFORE allowing standard line execution
    _validator = PyProjectASTValidator()

    if not _validator.validate_file(_caller_file):
        print(f"❌ Security & Standard Validation Failed for '{_caller_file}':")
        for err in _validator.errors:
            print(f"  - {err}")
        print("\nEvaluation halted. No output or modifications were made.")
        sys.exit(1)

    # Lazily register compilation and provisioning loop to fire at runtime exit
    def _build_and_sync():
        import venv
        import subprocess

        # Do not overwrite configurations if the user's execution runtime crashed
        if sys.exc_info()[0] is not None:
            print("\n⚠️ Compilation aborted due to an execution error in the script.")
            return

        caller_path = Path(_caller_file)
        toml_path = caller_path.parent / "pyproject.toml"
        venv_dir = caller_path.parent / ".venv"

        print("\n--- ⚙️  Compiling Configuration ---")
        toml_content = serialize_to_toml(__REGISTRY.data)
        toml_path.write_text(toml_content)
        print(f"✓ Automatically generated and synced: '{toml_path}'")

        print("\n--- 🛠️  Synchronizing Virtual Environment ---")
        if not venv_dir.exists():
            print(f"Creating localized virtual environment in '{venv_dir}'...")
            venv.create(str(venv_dir), with_pip=True)

        if sys.platform == "win32":
            pip_path = venv_dir / "Scripts" / "pip.exe"
        else:
            pip_path = venv_dir / "bin" / "pip"

        if not pip_path.exists():
            print("❌ Error: Could not resolve pip executable inside environment.")
            return

        # Build dynamic package list directly from evaluated objects
        proj_deps = __REGISTRY.data["project"].get("dependencies", [])

        other_deps = []
        for deps in __REGISTRY.data["dependency-groups"].values():
            other_deps.extend(deps)

        all_packages = list(set(proj_deps + other_deps))

        if not all_packages:
            print("No dependencies to synchronize.")
            return

        print(f"Installing dependencies into .venv: {all_packages}")
        try:
            subprocess.run(
                [str(pip_path), "install", "--upgrade", "pip"],
                check=True,
                capture_output=True,
            )
            subprocess.run([str(pip_path), "install"] + all_packages, check=True)
            print(
                "✓ Local packages synchronized and environment configured successfully! 🎉"
            )
        except subprocess.CalledProcessError as e:
            print(f"❌ Synchronizer installation error: {e}")

    # Register our clean exit automation
    atexit.register(_build_and_sync)
