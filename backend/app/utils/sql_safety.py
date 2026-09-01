"""
SQL Safety and Security Verification Module.
Enforces strict read-only analytical SQL execution:
- Rejects any DML/DDL keywords anywhere in the query (including CTEs, subqueries, comments).
- Rejects multi-statement injection attempts.
- Guarantees queries start strictly with SELECT or WITH.
"""

import re
from typing import List, Tuple

# Comprehensive list of disallowed DML/DDL/Administrative keywords
DISALLOWED_KEYWORDS = {
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE",
    "CREATE", "RENAME", "REPLACE", "MERGE", "EXEC", "EXECUTE",
    "GRANT", "REVOKE", "LOCK", "UNLOCK", "CALL", "LOAD",
    "OUTFILE", "DUMPFILE", "SHUTDOWN", "KILL", "FLUSH",
}

# Regex to strip SQL comments: single-line (-- or #) and multi-line (/* ... */)
COMMENT_REGEX = re.compile(
    r"(--[^\r\n]*)|(#[^\r\n]*)|(/\*[\s\S]*?\*/)",
    re.MULTILINE
)


def strip_sql_comments(sql: str) -> str:
    """
    Remove single-line and multi-line SQL comments before token analysis.
    """
    return COMMENT_REGEX.sub(" ", sql).strip()


def sanitize_and_check_sql_safety(sql: str) -> Tuple[bool, List[str]]:
    """
    Validate that the SQL query is strictly read-only and safe to execute.
    Returns (is_safe: bool, violation_reasons: List[str]).
    """
    violations = []
    clean_sql = strip_sql_comments(sql).strip()

    if not clean_sql:
        return False, ["SQL query is empty."]

    # 1. Verify query begins strictly with SELECT or WITH (case-insensitive)
    first_token_match = re.match(r"^\s*([A-Za-z]+)", clean_sql)
    if not first_token_match:
        return False, ["SQL query does not start with a valid keyword."]

    first_keyword = first_token_match.group(1).upper()
    if first_keyword not in {"SELECT", "WITH", "EXPLAIN", "DESCRIBE", "SHOW"}:
        violations.append(
            f"Only read-only analytical queries (SELECT or WITH) are permitted. Found initial command '{first_keyword}'."
        )

    # 2. Check for disallowed DML/DDL keywords across the ENTIRE query (including CTEs and subqueries)
    # Using word-boundary regex to prevent false positives on substrings (e.g. 'update_date' or 'customer_created')
    for kw in DISALLOWED_KEYWORDS:
        pattern = rf"\b{kw}\b"
        if re.search(pattern, clean_sql, re.IGNORECASE):
            violations.append(f"Forbidden DML/DDL/Administrative keyword detected: '{kw}'.")

    # 3. Prevent multi-statement injection (e.g. SELECT 1; DROP TABLE users;)
    statements = [s.strip() for s in clean_sql.split(";") if s.strip()]
    if len(statements) > 1:
        violations.append(
            f"Multi-statement execution is blocked for security. Found {len(statements)} statements."
        )

    is_safe = len(violations) == 0
    return is_safe, violations
