import re
import json
import time
from typing import Callable, Any, Dict, Optional


def safe_json_parse(text: str, fallback_dict: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Robust JSON parser that strips markdown fences, conversational preambles,
    and extracts the outermost JSON object cleanly.
    """
    if not text:
        return fallback_dict or {}

    # Strip triple-backtick markdown blocks if present
    cleaned = re.sub(r"```(?:json)?\s*([\s\S]*?)\s*```", r"\1", text).strip()

    # Find first { and last }
    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start != -1 and end != -1 and end > start:
        candidate = cleaned[start : end + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    try:
        return json.loads(cleaned)
    except Exception:
        return fallback_dict or {}


def retry_with_exponential_backoff(
    func: Callable,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    *args,
    **kwargs,
) -> Any:
    """
    Executes a callable with exponential backoff retry on transient errors.
    """
    delay = initial_delay
    last_exception = None

    for attempt in range(1, max_retries + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            if attempt == max_retries:
                break
            time.sleep(delay)
            delay *= backoff_factor

    raise RuntimeError(f"Operation failed after {max_retries} attempts: {last_exception}")
