"""Tests for the SQL guardrail. Pure stdlib (unittest) — runs with zero install.

Run:  python tests/test_sql_guard.py -v
"""
import importlib.util
import unittest
from pathlib import Path

# Load sql_guard.py directly so we don't trigger the package __init__
_path = Path(__file__).resolve().parent.parent / "app" / "ai_core" / "sql_guard.py"
_spec = importlib.util.spec_from_file_location("sql_guard", _path)
sql_guard = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sql_guard)

quote_ident = sql_guard.quote_ident
assert_safe_select = sql_guard.assert_safe_select
is_single_statement = sql_guard.is_single_statement
build_select = sql_guard.build_select
UnsafeSQLError = sql_guard.UnsafeSQLError


class TestQuoteIdent(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(quote_ident("users"), '"users"')

    def test_schema_qualified(self):
        self.assertEqual(quote_ident("public.users"), '"public"."users"')

    def test_rejects_injection(self):
        for bad in ["users; DROP TABLE x", "1abc", "", "us-ers", "a b", "user'"]:
            with self.assertRaises(UnsafeSQLError):
                quote_ident(bad)


class TestSingleStatement(unittest.TestCase):
    def test_single(self):
        self.assertTrue(is_single_statement("SELECT * FROM users"))

    def test_trailing_semicolon_ok(self):
        self.assertTrue(is_single_statement("SELECT 1;"))

    def test_stacked_rejected(self):
        self.assertFalse(is_single_statement("SELECT 1; DROP TABLE users"))

    def test_semicolon_inside_string_is_one_statement(self):
        self.assertTrue(is_single_statement("SELECT * FROM t WHERE s = 'a;b'"))


class TestAssertSafeSelect(unittest.TestCase):
    def test_allows_plain_select(self):
        assert_safe_select("SELECT * FROM users")

    def test_allows_lowercase_and_where(self):
        assert_safe_select("select id, email from users where id = 5")

    def test_allows_cte(self):
        assert_safe_select("WITH t AS (SELECT 1) SELECT * FROM t")

    def test_allows_string_with_keyword_lookalike(self):
        # 'drop' here is data, not a statement — must be allowed.
        assert_safe_select("SELECT * FROM logs WHERE msg = 'please drop by'")

    def test_blocks_drop(self):
        with self.assertRaises(UnsafeSQLError):
            assert_safe_select("DROP TABLE users")

    def test_blocks_delete(self):
        with self.assertRaises(UnsafeSQLError):
            assert_safe_select("DELETE FROM users")

    def test_blocks_stacked_injection(self):
        with self.assertRaises(UnsafeSQLError):
            assert_safe_select("SELECT * FROM users WHERE n = 'a'; DELETE FROM users")

    def test_blocks_comment(self):
        with self.assertRaises(UnsafeSQLError):
            assert_safe_select("SELECT * FROM users -- and then trouble")

    def test_blocks_block_comment(self):
        with self.assertRaises(UnsafeSQLError):
            assert_safe_select("SELECT * /* x */ FROM users")

    def test_blocks_insert(self):
        with self.assertRaises(UnsafeSQLError):
            assert_safe_select("INSERT INTO t VALUES (1)")

    def test_blocks_empty(self):
        with self.assertRaises(UnsafeSQLError):
            assert_safe_select("   ")


class TestBuildSelect(unittest.TestCase):
    def test_basic(self):
        sql, params = build_select("users", ["id", "email"], {"id": 5})
        self.assertEqual(sql, 'SELECT "id", "email" FROM "users" WHERE "id" = %s')
        self.assertEqual(params, [5])

    def test_no_where(self):
        sql, params = build_select("users", ["id"])
        self.assertEqual(sql, 'SELECT "id" FROM "users"')
        self.assertEqual(params, [])

    def test_multi_condition_params_in_order(self):
        sql, params = build_select("orders", ["id"], {"user_id": 7, "status": "paid"})
        self.assertIn('"user_id" = %s', sql)
        self.assertIn('"status" = %s', sql)
        self.assertEqual(params, [7, "paid"])

    def test_requires_columns(self):
        with self.assertRaises(UnsafeSQLError):
            build_select("users", [])

    def test_rejects_bad_table(self):
        with self.assertRaises(UnsafeSQLError):
            build_select("users; DROP TABLE x", ["id"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
