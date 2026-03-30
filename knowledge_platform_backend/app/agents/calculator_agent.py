# app/agents/calculator_agent.py
import re
import math

def run(query: str) -> str:
    """
    Calculator agent: safely evaluate simple arithmetic expressions.
    Supports +, -, *, /, parentheses, and math functions.
    """
    expr = query.strip()

    # Only allow digits, operators, parentheses, decimal points, and math functions
    if not re.fullmatch(r"[0-9\+\-\*\/\.\(\)\s]+", expr):
        return "Error: Invalid expression."

    try:
        # Safe eval with math functions available
        result = eval(expr, {"__builtins__": {}}, {"math": math})
        return f"{expr} = {result}"
    except Exception as e:
        return f"Error calculating expression: {e}"
