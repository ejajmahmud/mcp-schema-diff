"""Unit tests for SchemaDiffer."""
import unittest
from mcp_schema_diff.diff import SchemaDiffer

class TestSchemaDiffer(unittest.TestCase):
    def test_backward_compatible_addition(self):
        v1 = {"type": "object", "properties": {"q": {"type": "string"}}, "required": ["q"]}
        v2 = {"type": "object", "properties": {"q": {"type": "string"}, "page": {"type": "integer"}}, "required": ["q"]}
        report = SchemaDiffer.compare(v1, v2)
        self.assertTrue(report.is_compatible)
        self.assertEqual(len(report.breaking), 0)
        self.assertEqual(len(report.non_breaking), 1)

    def test_breaking_added_required(self):
        v1 = {"type": "object", "properties": {"q": {"type": "string"}}, "required": ["q"]}
        v2 = {"type": "object", "properties": {"q": {"type": "string"}, "auth": {"type": "string"}}, "required": ["q", "auth"]}
        report = SchemaDiffer.compare(v1, v2)
        self.assertFalse(report.is_compatible)
        self.assertTrue(any("auth" in b for b in report.breaking))

    def test_breaking_type_change(self):
        v1 = {"type": "object", "properties": {"count": {"type": "integer"}}}
        v2 = {"type": "object", "properties": {"count": {"type": "string"}}}
        report = SchemaDiffer.compare(v1, v2)
        self.assertFalse(report.is_compatible)
        self.assertTrue(any("type changed" in b for b in report.breaking))

    def test_enum_expansion(self):
        v1 = {"type": "object", "properties": {"role": {"type": "string", "enum": ["user", "admin"]}}}
        v2 = {"type": "object", "properties": {"role": {"type": "string", "enum": ["user", "admin", "moderator"]}}}
        report = SchemaDiffer.compare(v1, v2)
        self.assertTrue(report.is_compatible)

if __name__ == "__main__":
    unittest.main()
