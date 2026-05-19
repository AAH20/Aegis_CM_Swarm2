import os
import json
import vertexai
from vertexai.generative_models import GenerativeModel, Tool


class AegisSwarmNode:
    def __init__(self, agent_role: str, project_id: str, location: str, mcp_tools: list = None):
        self.agent_role = agent_role
        self.is_offline = os.getenv("AEGIS_OFFLINE", "0").lower() in ("1", "true", "yes")

        if not self.is_offline:
            print(f"[*] Bootstrapping Vertex AI (Project: {project_id}, Region: {location})")
            vertexai.init(project=project_id, location=location)
            self.tools = Tool(function_declarations=mcp_tools) if mcp_tools else None
            self.model = GenerativeModel(
                "gemini-2.5-pro",
                system_instruction=[self.agent_role],
                tools=[self.tools] if self.tools else None,
            )
            print(f"[*] Bootstrapped Aegis Swarm Node (ONLINE): {agent_role[:30]}...")
        else:
            print(f"[*] Bootstrapped Aegis Swarm Node (OFFLINE FALLBACK): {agent_role[:30]}...")

    def process_telemetry(self, data: str):
        if self.is_offline:
            return self._offline_fallback(data)

        response = self.model.generate_content(
            f"NEW ISOLATED THREAT EVENT:\n{data}\nAnalyze and execute ALL requested MCP tools immediately."
        )
        return response

    def _offline_fallback(self, data: str):
        class MockCall:
            def __init__(self, name, args):
                self.name = name
                self.args = args

        class MockCandidate:
            def __init__(self, calls):
                self.function_calls = calls

        class MockResponse:
            def __init__(self, calls, text=""):
                self.candidates = [MockCandidate(calls)] if calls else []
                self.text = text

        try:
            payload = json.loads(data)
            cpu = payload.get("metrics", {}).get("cpu_percent", 0.0)
            if cpu > 80.0:
                return MockResponse([
                    MockCall("elevenlabs_trigger_call", {"alert_message": "Offline Demo Alert.", "phone_number": "+1-555-0199"})
                ])
        except Exception:
            pass
        return MockResponse([], "Telemetry normal.")