import boto3
import json
from config.settings import settings

sqs = boto3.client("sqs", region_name=settings.AWS_REGION)

QUEUES = {
    "refund_processing": settings.SQS_REFUND_QUEUE_URL,
    "ticket_escalation": settings.SQS_ESCALATION_QUEUE_URL,
    "notification": settings.SQS_NOTIFICATION_QUEUE_URL,
}

def send_message(queue_name: str, message: dict, delay_seconds: int = 0):
    sqs.send_message(
        QueueUrl=QUEUES[queue_name],
        MessageBody=json.dumps(message),
        DelaySeconds=delay_seconds,
    )

def send_refund_request(order_id: str, amount: float, customer_id: str):
    send_message("refund_processing", {
        "action": "process_refund",
        "order_id": order_id,
        "amount": amount,
        "customer_id": customer_id,
    })

def send_escalation(ticket_id: str, reason: str, priority: str):
    send_message("ticket_escalation", {
        "action": "escalate",
        "ticket_id": ticket_id,
        "reason": reason,
        "priority": priority,
    })