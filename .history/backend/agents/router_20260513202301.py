class RouterAgent:
    def route(self, query: str) -> str:
        query = query.lower()

        if "diabetes" in query:
            return "diabetes"
        elif "diet" in query or "food" in query:
            return "nutrition"
        else:
            return "summary"


router_agent = RouterAgent()