from typing import Any
from typing import overload
from enum import Enum
from pathlib import Path

from .registry import __REGISTRY


# ----


class version:
    def __init__(self, *parts: int) -> None:
        self.parts = parts

    def __repr__(self) -> str:
        repr = ".".join([str(p) for p in self.parts])

        return repr


v = version


class dependency:
    @overload
    def __init__(self, name: str, version: version | None = None) -> None: ...

    @overload
    def __init__(self, name: Path) -> None:
        """For local installs"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        _name = kwargs.get("name")
        _version = kwargs.get("version")
        _path = kwargs.get("path")

        if args:
            if isinstance(args[0], Path):
                _path = args[0].resolve()
            elif isinstance(args[0], str):
                _name = args[0]

            if len(args) > 1:
                _version = args[1]

        if _path and isinstance(_path, Path):
            _path = _path.resolve()

        self.target: str | Path = _name or _path or ""
        self.version: version | None = _version

    def __repr__(self) -> str:
        if isinstance(self.target, str):
            final = self.target

            if self.version:
                final += str(self.version)

            return final
        else:
            return f"{self.target.stem} @ file://{self.target}"


dep = dependency


def project(
    name: str,
    version: version,
    description: str | None = None,
    requires_python: version | None = None,
    dependencies: list[dependency] | None = None,
    readme: Path | None = None,
    license: str | None = None,
    authors: list[dict[str, str]] | None = None,
    **kwargs,
):
    """Declares standard PEP 621 metadata for the [project] table."""

    __REGISTRY.register_project(
        name=name,
        version=">= " + str(version),
        description=description,
        requires_python=str(requires_python) if requires_python else None,
        dependencies=[str(dep) for dep in dependencies] if dependencies else None,
        readme=str(readme) if readme else None,
        license=license,
        authors=authors,
        **kwargs,
    )


class BuildSystem(Enum):
    Hatchling = {"name": "hatchling", "backend": "hatchling.build"}
    setuptools = {"name": "setuptools", "backend": "setuptools.build_meta"}
    Flit = {"name": "flit_core", "backend": "flit_core.buildapi"}
    PDM = {"name": "pdm-backend", "backend": "pdm.backend"}
    uv_build = {"name": "uv_build", "backend": "uv_build"}


Hatchling: BuildSystem = BuildSystem.Hatchling
setuptools: BuildSystem = BuildSystem.setuptools
Flit: BuildSystem = BuildSystem.Flit
PDM: BuildSystem = BuildSystem.PDM
uv_build: BuildSystem = BuildSystem.uv_build


def build_system(buildsys: BuildSystem, version: version):
    """Declares the build backend configuration matching [build-system]."""

    requires = [f"{buildsys.value['name']} >= {version}"]
    build_backend = buildsys.value["backend"]

    __REGISTRY.register_build_system(requires, build_backend)


def dependency_group(name: str, dependencies: list[dependency]):
    """Declares development or optional dependency groups (PEP 735)."""

    deps = [str(dep) for dep in dependencies]

    __REGISTRY.register_dependency_group(name, deps)


def tool(name: str, **kwargs):
    """Declares nested tool configurations like [tool.ruff] or [tool.mypy]."""

    __REGISTRY.register_tool(name, **kwargs)
