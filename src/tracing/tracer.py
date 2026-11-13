import time
import uuid
from typing import Dict, Any, Optional
from src.database.db import log_agent_trace_db, get_all_agent_traces_db


class AgentTracer:
    """
    Context manager for capturing agent telemetry, execution latency,
    input states, and output state diffs.
    """

    def __init__(self, agent_name: str, trace_id: Optional[str] = None, input_data: Optional[Dict[str, Any]] = None):
        self.agent_name = agent_name
        self.trace_id = trace_id or f"trace_{uuid.uuid4().hex[:8]}"
        self.input_data = input_data or {}
        self.start_time = 0.0
        self.latency_ms = 0.0
        self.status = "SUCCESS"
        self.output_summary = ""

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def set_output(self, summary: str, status: str = "SUCCESS"):
        self.output_summary = summary
        self.status = status

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.latency_ms = (time.perf_counter() - self.start_time) * 1000.0
        if exc_type:
            self.status = "ERROR"
            self.output_summary = f"Exception: {str(exc_val)}"

        input_str = f"Keys: {list(self.input_data.keys())}" if self.input_data else "None"
        try:
            log_agent_trace_db(
                trace_id=self.trace_id,
                agent_name=self.agent_name,
                latency_ms=self.latency_ms,
                status=self.status,
                input_summary=input_str,
                output_summary=self.output_summary[:500],
            )
        except Exception as e:
            print(f"[Tracer] Warning: could not log trace: {e}")


def get_recent_traces(limit: int = 50):
    return get_all_agent_traces_db(limit=limit)
