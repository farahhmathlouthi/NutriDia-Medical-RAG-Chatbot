from agents.router import router_agent
from agents.diabetes_agent import diabetes_agent
from agents.nutrition_agent import nutrition_agent
from agents.summary_agent import summary_agent


class AgentOrchestrator:
    def run(self, query: str):

        route = router_agent.route(query)

        if route == "diabetes":
            return diabetes_agent.run(query)

        elif route == "nutrition":
            return nutrition_agent.run(query)

        else:
            return summary_agent.run(query)


orchestrator = AgentOrchestrator()