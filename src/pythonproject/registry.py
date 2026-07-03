from typing import Any


# ----


class PyProjectRegistry:
    def __init__(self):
        self.data: dict[str, Any] = {
            "project": {},
            "build-system": {},
            "dependency-groups": {},
            "tool": {},
        }

    def reset(self):
        self.__init__()

    def register_project(
        self,
        name: str,
        version: str,
        description: str | None = None,
        requires_python: str | None = None,
        dependencies: list[str] | None = None,
        readme: str | None = None,
        license: str | None = None,
        authors: list[dict[str, str]] | None = None,
        **kwargs,
    ):
        project_data = {
            "name": name,
            "version": version,
            "description": description,
            "requires-python": requires_python,
            "dependencies": dependencies,
            "readme": readme,
            "license": {"text": license} if license else None,
            "authors": authors,
            **kwargs,
        }
        # Filter out None values
        self.data["project"] = {k: v for k, v in project_data.items() if v is not None}

    def register_build_system(self, requires: list[str], build_backend: str):
        self.data["build-system"] = {
            "requires": requires,
            "build-backend": build_backend,
        }

    def register_dependency_group(self, name: str, dependencies: list[str]):
        self.data["dependency-groups"][name] = dependencies

    def register_tool(self, name: str, **kwargs):
        self.data["tool"][name] = kwargs


# Globally accessible singleton registry
__REGISTRY = PyProjectRegistry()
