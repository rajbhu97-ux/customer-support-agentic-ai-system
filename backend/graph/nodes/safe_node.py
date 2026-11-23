
from functools import wraps
import logging 

logger = logging.getLogger(__name__)

MAX_RETRIES = 2

def safe_node(node_name: str, max_retries: int = MAX_RETRIES, fallback_message:str=None):
    def decorator(func):
        @wraps(func)
        def wrapper(state):
            retry_count = state.get("retry_count")
            try:
                result = func(state)
                result["node_status"] = "success"
                result["current_node"] = node_name
                result["retry_count"] = 0
                result
            except Exception as e:
                logger.exception(f"Error in node {node_name}: {str(e)}")
                if retry_count < max_retries:
                    return {
                        "node_status": "retry",
                        "current_node": node_name,
                        "retry_count": retry_count + 1,
                        "error_info": {
                            "node": node_name,
                            "error_type": type(e).__name__,
                            "message": str(e)
                        }
                    }
                if fallback_message:
                    logger.warning(f"[{node_name}] all retries exhausted, using fallback")
                    return {
                        "node_status": "fallback",
                        "current_node": node_name,
                        "retry_count": 0,
                        "final_response": fallback_message,
                        "error_info": {
                            "node": node_name,
                            "error_type": type(e).__name__,
                            "message": str(e)
                        }
                    }
                logger.error(f"[{node_name}] all retries exhausted, no fallback")
                return {
                    "node_status": "failed",
                    "current_node": node_name,
                    "retry_count": 0,
                    "error_info": {
                        "node": node_name,
                        "error_type": type(e).__name__,
                        "message": str(e)
                    }
                }
