from typing import Any


# ----


def serialize_to_toml(config_data: dict[str, Any]) -> str:
    """Recursively formats PyProjectRegistry data into structured valid TOML."""
    lines = []

    def format_val(val) -> str:
        if isinstance(val, str):
            # Escape double quotes and backslashes
            escaped = val.replace("\\", "\\\\").replace('"', '\\"')
            return f'"{escaped}"'
        elif isinstance(val, bool):
            return "true" if val else "false"
        elif isinstance(val, (int, float)):
            return str(val)
        elif isinstance(val, list):
            items = ", ".join(format_val(x) for x in val)
            return f"[{items}]"
        elif isinstance(val, dict):
            pairs = ", ".join(f"{k} = {format_val(v)}" for k, v in val.items())
            return f"{{ {pairs} }}"
        return "null"

    # [project]
    if proj := config_data.get("project"):
        lines.append("[project]")
        for k, v in proj.items():
            lines.append(f"{k} = {format_val(v)}")
        lines.append("")

    # [build-system]
    if buildsys := config_data.get("build-system"):
        lines.append("[build-system]")
        for k, v in buildsys.items():
            lines.append(f"{k} = {format_val(v)}")
        lines.append("")

    # [dependency-groups]
    if depgroups := config_data.get("dependency-groups"):
        lines.append("[dependency-groups]")
        for k, v in depgroups.items():
            lines.append(f"{k} = {format_val(v)}")
        lines.append("")

    # [tool.*]
    if tl := config_data.get("tool"):
        for tool_name, tool_values in tl.items():
            lines.append(f"[tool.{tool_name}]")
            for k, v in tool_values.items():
                lines.append(f"{k} = {format_val(v)}")
            lines.append("")

    return "\n".join(lines).strip() + "\n"
