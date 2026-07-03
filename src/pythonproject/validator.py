import ast
from pathlib import Path


# ----


class PyProjectASTValidator(ast.NodeVisitor):
    """
    Enforces that the config file is 100% declarative.
    Bans all procedural logic: custom functions, loops, if statements, classes,
    and foreign imports. Only simple assignments and DSL function calls are allowed.
    """

    def __init__(self):
        self.errors = []
        self.allowed_calls = {
            "project",
            "build_system",
            "dependency_group",
            "tool",
            "version",
            "v",
            "dependency",
            "dep",
            "BuildSystem",
        }

    def validate_file(self, filepath: str) -> bool:
        if not Path(filepath).exists():
            self.errors.append(f"Configuration file '{filepath}' not found.")
            return False

        with open(filepath, "r") as f:
            source = f.read()

        try:
            tree = ast.parse(source, filename=filepath)
        except SyntaxError as e:
            self.errors.append(f"Syntax error while parsing '{filepath}': {e}")
            return False

        self.visit(tree)
        return len(self.errors) == 0

    def visit_FunctionDef(self, node):
        self.errors.append(f"Line {node.lineno}: Defining custom functions is banned.")
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self.errors.append(
            f"Line {node.lineno}: Defining custom async functions is banned."
        )
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.errors.append(f"Line {node.lineno}: Defining custom classes is banned.")
        self.generic_visit(node)

    def visit_For(self, node):
        self.errors.append(f"Line {node.lineno}: For loops are banned in config files.")
        self.generic_visit(node)

    def visit_While(self, node):
        self.errors.append(
            f"Line {node.lineno}: While loops are banned in config files."
        )
        self.generic_visit(node)

    def visit_If(self, node):
        self.errors.append(
            f"Line {node.lineno}: Conditional 'if' statements are banned."
        )
        self.generic_visit(node)

    def visit_With(self, node):
        self.errors.append(f"Line {node.lineno}: 'with' statements are banned.")
        self.generic_visit(node)

    def visit_Try(self, node):
        self.errors.append(f"Line {node.lineno}: Try/except blocks are banned.")
        self.generic_visit(node)

    def visit_Call(self, node):
        # Ensure they are calling specified DSL API functions
        if isinstance(node.func, ast.Name):
            func_name = node.func.id

            if func_name not in self.allowed_calls:
                self.errors.append(
                    f"Line {node.lineno}: Unauthorized function call '{func_name}'. "
                    f"Only {self.allowed_calls} can be called directly."
                )

        self.generic_visit(node)

    def visit_Assign(self, node):
        # Allow simple variable assignments to hold string literals or constant arrays
        for target in node.targets:
            if not isinstance(target, ast.Name):
                self.errors.append(
                    f"Line {node.lineno}: Complex variable assignment is banned."
                )

        # Verify the value of assignment is safe and declarative
        if not self._is_declarative_value(node.value):
            self.errors.append(
                f"Line {node.lineno}: Assignments must only assign static values/literals."
            )
        self.generic_visit(node)

    def _is_declarative_value(self, node) -> bool:
        if isinstance(node, ast.Constant):
            return True
        if isinstance(node, ast.Name):
            return True
        if isinstance(node, ast.List):
            return all(self._is_declarative_value(el) for el in node.elts)
        if isinstance(node, ast.Dict):
            return all(self._is_declarative_value(k) for k in node.keys) and all(
                self._is_declarative_value(v) for v in node.values
            )
        return False
