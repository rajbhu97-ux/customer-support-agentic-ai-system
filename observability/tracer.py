from aws_xray_sdk.core import xray_recorder, patch_all
from config.settings import settings

def setup_tracing():
    if settings.ENABLE_TRACING:
        xray_recorder.configure(
            service="customer-support-ai",
            sampling=True,
            context_missing="LOG_ERROR",
        )
        patch_all()  # auto-instrument boto3, requests, etc.

# Usage as decorator:
# @xray_recorder.capture("intent_agent")
# def intent_agent_node(state):
#     ...