import boto3
from functools import lru_cache
from config.settings import settings
from mypy_boto3_dynamodb.service_resource import Table
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime


@lru_cache
def get_dynamodb_resource():
    resource = boto3.resource(
        "dynamodb",
        region_name= settings.REGION,
        endpoint_url= settings.ENDPOINT_URL
    )
    return resource


def get_table(table_name: str) -> Table:
    return get_dynamodb_resource().Table(table_name)


class DynamoDBRepository:

    def __init__(self, table_name: str = "CustomerSupport"):
        self.table = get_table(table_name)


    def get_customer(self, customer_id: str) -> dict | None:
        resp = self.table.get_item(Key={"PK": f"CUST#{customer_id}", "SK": "PROFILE"})
        return resp.get("Item")

    def get_order(self, order_id: str) -> dict | None:
        resp = self.table.get_item(Key={"PK": f"ORD#{order_id}", "SK": "METADATA"})
        return resp.get("Item")

    def get_customer_orders(self, customer_id: str) -> list[dict]:
        resp = self.table.query(
            KeyConditionExpression= Key("PK").eq(f"CUST#{customer_id}" & Key("SK").begins_with("ORD#"))
        )
        return resp.get("Items", [])

    def get_shipment(self, order_id: str) -> dict | None:
        resp = self.table.query(
            KeyConditionExpression= Key("PK").eq(f"ORD#{order_id}" & Key("SK").begins_with("SHIP#"))
        )
        items = resp.get("Items", [])
        return items[0] if items else None

    def get_refund(self, order_id: str) -> dict | None:
        resp = self.table.query(
            KeyConditionExpression= Key("PK").eq(f"ORD#{order_id}" & Key("SK").begins_with("REF#"))
        )
        items = resp.get("Items", [])
        return items[0] if items else None

    def get_payment(self, order_id: str) -> dict | None:
        resp = self.table.query(
            KeyConditionExpression= Key("PK").eq(f"ORD#{order_id}" & Key("SK").begins_with("PAY#"))
        )
        items = resp.get("Items", [])
        return items[0] if items else None

    def create_ticket(self, ticket: dict) -> dict:
        self.table.put_item(Item = {
            "PK": f"TKT#{ticket.get("ticket_id")}",
            "SK": "METADATA",
            "entity_type": "TICKET",
            **ticket
        }
        )
        return ticket

    def update_order_status(self, order_id: str, new_status: str) -> dict:
        resp = self.table.update_item(
            Key = {
                "PK": f"ORD#{order_id}",
                "SK": "METADATA"
            },
            UpdateExpression="SET #status = :status",
            ExpressionAttributeNames={
                "#status": "status"
            },
            ExpressionAttributeValues={
                ":status": new_status
            },
            ReturnValues="UPDATED_NEW"
        )
        return resp.get("Attributes", {})

    def create_refund(self, refund: dict) -> dict:
        self.table.put_item(Item = {
            "PK": f"ORD#{refund.get('order_id')}",
            "SK": f"REF#{refund.get('refund_id')}",
            "entity_type": "REFUND",
            **refund
        })
        return refund
            

    def save_conversation_turn(self,session_id: str, seq: str, role: str, content: str):
        self.table.put_item(Item ={
            "PK": f"SESSION#{session_id}",
            "SK": f"TURN#{seq:05d}",
            "entity_type": "CONVERSATION",
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        })


    def get_conversation_history(self, session_id: str) -> list[dict]:
        resp = self.table.query(
            KeyConditionExpression= Key("PK").eq(f"SESSION#{session_id}") & Key("SK").begins_with("TURN#")
        )
        return resp.get("Items", [])
