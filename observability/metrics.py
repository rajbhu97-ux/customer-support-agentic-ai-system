import boto3
from config.settings import settings

cloudwatch = boto3.client("cloudwatch", region_name=settings.AWS_REGION)

def put_metric(metric_name: str, value: float, unit: str = "Count", dimensions: dict = None):
    dim_list = [{"Name": k, "Value": v} for k, v in (dimensions or {}).items()]
    cloudwatch.put_metric_data(
        Namespace="CustomerSupport",
        MetricData=[{
            "MetricName": metric_name,
            "Value": value,
            "Unit": unit,
            "Dimensions": dim_list,
        }]
    )