"""Callbacks para observabilidad, métricas de latencia, tokens y llamadas de agentes."""

import time
from typing import Dict, Any, List, Optional
from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.outputs import LLMResult


class MetricsCollector:
    """Almacén centralizado de métricas del sistema multiagente."""

    def __init__(self):
        self.total_requests: int = 0
        self.out_of_scope_rejections: int = 0
        self.character_limit_trims: int = 0
        self.agent_invocations: Dict[str, int] = {
            "supervisor": 0,
            "formalization_agent": 0,
            "tax_agent": 0,
            "cost_agent": 0,
            "escalation_agent": 0,
            "greeting_agent": 0,
            "fallback": 0,
        }
        self.total_prompt_tokens: int = 0
        self.total_completion_tokens: int = 0
        self.latencies_ms: List[float] = []

    def record_request(self):
        self.total_requests += 1

    def record_agent_call(self, agent_name: str):
        if agent_name in self.agent_invocations:
            self.agent_invocations[agent_name] += 1
        else:
            self.agent_invocations[agent_name] = 1

    def record_guardrail_action(self, action: str):
        if action == "out_of_scope_replaced":
            self.out_of_scope_rejections += 1
        elif action == "truncated_to_max_chars":
            self.character_limit_trims += 1

    def record_tokens(self, prompt_tokens: int, completion_tokens: int):
        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens

    def record_latency(self, latency_ms: float):
        self.latencies_ms.append(latency_ms)
        # Mantener historial acotado a los últimos 1000 registros
        if len(self.latencies_ms) > 1000:
            self.latencies_ms.pop(0)

    def get_summary(self) -> Dict[str, Any]:
        avg_latency = (
            sum(self.latencies_ms) / len(self.latencies_ms)
            if self.latencies_ms
            else 0.0
        )
        return {
            "total_requests": self.total_requests,
            "out_of_scope_rejections": self.out_of_scope_rejections,
            "character_limit_trims": self.character_limit_trims,
            "agent_invocations": self.agent_invocations,
            "total_tokens": {
                "prompt_tokens": self.total_prompt_tokens,
                "completion_tokens": self.total_completion_tokens,
                "total": self.total_prompt_tokens + self.total_completion_tokens,
            },
            "latency_ms": {
                "average": round(avg_latency, 2),
                "last": round(self.latencies_ms[-1], 2) if self.latencies_ms else 0.0,
            },
        }


# Instancia global de métricas
metrics_collector = MetricsCollector()


class PNTEMetricsCallbackHandler(BaseCallbackHandler):
    """Callback de LangChain para auditar tokens y latencia de llamadas a modelos."""

    def __init__(self, agent_name: str = "unknown"):
        super().__init__()
        self.agent_name = agent_name
        self.start_time: float = 0.0

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        self.start_time = time.perf_counter()

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        duration_ms = (time.perf_counter() - self.start_time) * 1000
        metrics_collector.record_latency(duration_ms)

        if response.llm_output and "token_usage" in response.llm_output:
            usage = response.llm_output["token_usage"]
            metrics_collector.record_tokens(
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0),
            )
