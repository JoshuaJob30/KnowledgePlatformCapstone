# app/agents/date_agent.py
from datetime import date

async def run(query: str) -> str:
    today = date.today()
    return f"Today's date is {today.strftime('%B %d, %Y')}."
