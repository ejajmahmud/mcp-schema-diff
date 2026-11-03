"""Command-line interface for MCP Schema Diff."""
import json
import argparse
from .diff import SchemaDiffer

def main():
    parser = argparse.ArgumentParser(description="MCP Schema Diff CLI")
    parser.add_argument("--demo", action="store_true", help="Run demonstration diff check")
    args = parser.parse_args()

    v1 = {
        "type": "object",
        "properties": {"query": {"type": "string"}, "limit": {"type": "integer"}},
        "required": ["query"]
    }
    v2 = {
        "type": "object",
        "properties": {"query": {"type": "string"}, "limit": {"type": "integer"}, "api_key": {"type": "string"}},
        "required": ["query", "api_key"]
    }

    report = SchemaDiffer.compare(v1, v2)
    print("Schema Diff Analysis Result:")
    print("Compatible:", report.is_compatible)
    print("Breaking changes:", report.breaking)
    print("Non-breaking changes:", report.non_breaking)

if __name__ == "__main__":
    main()
