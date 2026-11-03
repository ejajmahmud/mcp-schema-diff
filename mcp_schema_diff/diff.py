"""Semantic schema diffing and backward-compatibility evaluator."""
from typing import Dict, List, Any


class DiffReport:
    def __init__(self, is_compatible: bool, breaking: List[str], non_breaking: List[str]):
        self.is_compatible = is_compatible
        self.breaking = breaking
        self.non_breaking = non_breaking

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_compatible": self.is_compatible,
            "breaking_changes": self.breaking,
            "non_breaking_changes": self.non_breaking
        }


class SchemaDiffer:
    @staticmethod
    def compare(old_schema: Dict[str, Any], new_schema: Dict[str, Any]) -> DiffReport:
        breaking: List[str] = []
        non_breaking: List[str] = []

        old_props = old_schema.get("properties", {})
        new_props = new_schema.get("properties", {})

        old_req = set(old_schema.get("required", []))
        new_req = set(new_schema.get("required", []))

        # Check newly added required properties (Breaking)
        added_req = new_req - old_req
        for prop in added_req:
            if prop not in old_props:
                breaking.append(f"Newly added required property '{prop}' breaks legacy callers.")
            else:
                breaking.append(f"Optional property '{prop}' was promoted to required.")

        # Check removed properties
        removed_props = set(old_props.keys()) - set(new_props.keys())
        for prop in removed_props:
            if prop in old_req:
                breaking.append(f"Required property '{prop}' was removed from schema.")
            else:
                non_breaking.append(f"Optional property '{prop}' was removed.")

        # Check added optional properties (Non-breaking)
        added_props = set(new_props.keys()) - set(old_props.keys())
        for prop in added_props:
            if prop not in new_req:
                non_breaking.append(f"Added new optional property '{prop}'.")

        # Check type and constraint changes for overlapping properties
        common = set(old_props.keys()).intersection(set(new_props.keys()))
        for prop in common:
            old_p = old_props[prop]
            new_p = new_props[prop]
            old_type = old_p.get("type")
            new_type = new_p.get("type")

            if old_type != new_type:
                breaking.append(f"Property '{prop}' type changed from '{old_type}' to '{new_type}'.")

            # Check enum restrictions
            if "enum" in old_p and "enum" in new_p:
                removed_enums = set(old_p["enum"]) - set(new_p["enum"])
                if removed_enums:
                    breaking.append(f"Enum '{prop}' removed allowable values: {sorted(list(removed_enums))}")
                added_enums = set(new_p["enum"]) - set(old_p["enum"])
                if added_enums:
                    non_breaking.append(f"Enum '{prop}' added values: {sorted(list(added_enums))}")

        is_compatible = len(breaking) == 0
        return DiffReport(is_compatible=is_compatible, breaking=breaking, non_breaking=non_breaking)
