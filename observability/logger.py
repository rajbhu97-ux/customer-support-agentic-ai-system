import logging
import json
import watchtower
import boto3
from config.settings import settings

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))

    # CloudWatch handler
    cw_handler = watchtower.CloudWatchLogHandler(
        log_group_name=f"/customer-support/{settings.ENVIRONMENT}",
        stream_name=name,
        boto3_client=boto3.client("logs", region_name=settings.AWS_REGION),
    )
    cw_handler.setFormatter(logging.Formatter(
        json.dumps({
            "timestamp": "%(asctime)s",
            "level": "%(levelname)s",
            "logger": "%(name)s",
            "message": "%(message)s",
        })
    ))
    logger.addHandler(cw_handler)

    # Console handler for local dev
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(console)

    return logger