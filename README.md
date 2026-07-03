# pythonproject

This project reflects an **opinionated** view of how Python project configurations should be expressed.

Writing the configuration in Python means the editor treats it like ordinary code, providing autocomplete, type hints, and signature help as you build it out.

```python
# quick example

from pythonproject import *

build_system(setuptools, v(77, 0, 0))

project(
    name="My Cool Project",
    version=v(0, 1, 0),
    requires_python=v(3, 12, 0),
    dependencies=[dep("ruff")],
)
```

When you run the configuration file, it handles the entire project environment.

The same file handles both describing a project and bootstrapping its environment seamlessly!

## Backwards Compatibility

Although it can be used completely standalone, it would break a lot of current setups. For this reason it can also produce a `pyproject.toml` file next to it at runtime.

## Safety

To keep configurations safe, a validator inspects the file before any code executes, ensuring nothing dangerous runs at import time.



