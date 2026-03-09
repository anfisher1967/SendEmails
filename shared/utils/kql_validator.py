"""KQL query validation utilities."""

import re
from typing import Tuple, List

import structlog

logger = structlog.get_logger(__name__)


class KQLValidator:
    """Validates KQL (Kusto Query Language) queries for syntax errors."""

    # Common KQL keywords
    KEYWORDS = {
        "where",
        "project",
        "extend",
        "summarize",
        "order",
        "take",
        "distinct",
        "limit",
        "by",
        "asc",
        "desc",
        "group",
    }

    # Operators
    OPERATORS = {
        "==",
        "!=",
        "=~",
        "!~",
        ">",
        "<",
        ">=",
        "<=",
        "and",
        "or",
        "not",
        "in",
        "has",
        "contains",
    }

    @staticmethod
    def validate_query(query: str) -> Tuple[bool, List[str]]:
        """Validate KQL query syntax.
        
        Args:
            query: KQL query string to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Check for empty query
        if not query or not query.strip():
            errors.append("Query is empty")
            return False, errors

        # Check for balanced pipes
        if query.count("|") % 1 == 0:  # Pipes don't need to be balanced in KQL
            pass

        # Check for balanced parentheses
        if query.count("(") != query.count(")"):
            errors.append("Unbalanced parentheses")

        # Check for balanced quotes
        single_quotes = query.count("'") - query.count("\\'")
        double_quotes = query.count('"') - query.count('\\"')
        if single_quotes % 2 != 0:
            errors.append("Unbalanced single quotes")
        if double_quotes % 2 != 0:
            errors.append("Unbalanced double quotes")

        return len(errors) == 0, errors

    @staticmethod
    def extract_tables(query: str) -> List[str]:
        """Extract table names from KQL query.
        
        Args:
            query: KQL query string
            
        Returns:
            List of table names found in query
        """
        tables = []
        
        # Simple regex to find table names (before first pipe or operator)
        match = re.match(r"^\s*([a-zA-Z_][a-zA-Z0-9_]*)", query)
        if match:
            tables.append(match.group(1))

        return tables

    @staticmethod
    def extract_filters(query: str) -> List[str]:
        """Extract WHERE clauses from KQL query.
        
        Args:
            query: KQL query string
            
        Returns:
            List of filter conditions
        """
        filters = []
        
        # Find all where clauses
        where_pattern = r"\|\s*where\s+([^|]+)"
        matches = re.findall(where_pattern, query, re.IGNORECASE)
        filters.extend(matches)

        return filters

    @staticmethod
    def format_query(query: str) -> str:
        """Format KQL query for readability.
        
        Args:
            query: KQL query string
            
        Returns:
            Formatted query string
        """
        # Add newlines after pipes
        formatted = query.replace("|", " |\n")
        
        # Indent continuation lines
        lines = formatted.split("\n")
        result = []
        for i, line in enumerate(lines):
            if i > 0 and line.strip():
                result.append("    " + line)
            else:
                result.append(line)

        return "\n".join(result)

    @staticmethod
    def estimate_query_complexity(query: str) -> str:
        """Estimate query complexity based on operators and joins.
        
        Args:
            query: KQL query string
            
        Returns:
            Complexity level: 'Simple', 'Moderate', or 'Complex'
        """
        complexity_score = 0

        # Count operators
        complexity_score += query.count("|")
        complexity_score += query.count("join")
        complexity_score += query.count("union")
        complexity_score += len(re.findall(r"\|\s*where", query, re.IGNORECASE))

        if complexity_score < 3:
            return "Simple"
        elif complexity_score < 8:
            return "Moderate"
        else:
            return "Complex"
