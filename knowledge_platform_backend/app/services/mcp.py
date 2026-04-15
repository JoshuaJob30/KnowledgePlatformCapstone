import inspect
from app.services.agents_core import memory_agent
from app.agents.time_agent import run as time_agent
from app.agents.date_agent import run as date_agent
from app.agents.calculator_agent import run as calculator_agent
from app.agents.code_agent import run as code_agent
from app.agents.finance_agent import run as finance_agent
from app.agents.healthcare_agent import run as healthcare_agent
from app.agents.search_agent import run as search_agent
from app.agents.shopping_agent import run as shopping_agent

AGENT_REGISTRY = {
    "calculator": calculator_agent,
    "code": code_agent,
    "finance": finance_agent,
    "healthcare": healthcare_agent,
    "search": search_agent,
    "shopping": shopping_agent,
    "date": date_agent,
    "time": time_agent,
    "memory": memory_agent,
}

async def mcp_call(route: str, question: str):
    agent = AGENT_REGISTRY.get(route)
    if not agent:
        return None
    try:
        if inspect.iscoroutinefunction(agent):
            result = await agent(question, "", "")  # memory_agent expects 3 args
        else:
            result = agent(question)

        return result if isinstance(result, str) else str(result)
    except Exception as e:
        return f"Error running agent {route}: {e}"
