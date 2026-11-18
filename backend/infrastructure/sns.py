
import boto3
from config.settings import settings

sns = boto3.client("sns", region_name=settings.AWS_REGION)

def send_customer_notification(customer_email: str, subject: str, message: str):
    sns.publish(
        TopicArn=settings.SNS_CUSTOMER_TOPIC_ARN,
        Subject=subject,
        Message=message,
        MessageAttributes={
            "email": {"DataType": "String", "StringValue": customer_email}
        }
    )

def send_agent_alert(message: str, priority: str = "MEDIUM"):
    sns.publish(
        TopicArn=settings.SNS_AGENT_ALERT_TOPIC_ARN,
        Subject=f"[{priority}] Agent Alert",
        Message=message,
    )