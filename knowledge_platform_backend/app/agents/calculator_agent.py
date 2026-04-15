# app/agents/calculator_agent.py
import re
import math

def run(query: str) -> str:
    """
    Calculator agent: safely evaluate simple arithmetic expressions.
    Supports +, -, *, /, parentheses, math functions, and natural language math words.
    Extracts the math part from longer sentences.
    """
    original = query.strip().lower()

    # Normalize common math words to symbols
    normalized = original
    normalized = normalized.replace("times", "*")
    normalized = normalized.replace("plus", "+")
    normalized = normalized.replace("minus", "-")
    normalized = normalized.replace("divided by", "/")
    normalized = normalized.replace("x", "*")

    # Extract the math expression (digits + operators) from the normalized string
    match = re.findall(r"[0-9\+\-\*\/\.\(\)\s]+", normalized)
    if not match:
        return "Error: No valid math expression found."

    expr = "".join(match).strip()

    # Validate allowed characters
    if not re.fullmatch(r"[0-9\+\-\*\/\.\(\)\s]+", expr):
        return f"Error: Invalid expression. (extracted: {expr})"

    try:
        # Safe eval with math functions available
        result = eval(expr, {"__builtins__": {}}, {"math": math})
        return f"{expr} = {result}"
    except Exception as e:
        return f"Error calculating expression: {e}"
