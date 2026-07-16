import json
import logging
import boto3
from app.config import settings

logger = logging.getLogger(__name__)


def publish_stock_event(
    product_id: int,
    product_name: str,
    sku: str,
    current_stock: int,
    min_stock_level: int,
) -> None:
    event = {
        "product_id": product_id,
        "product_name": product_name,
        "sku": sku,
        "current_stock": current_stock,
        "min_stock_level": min_stock_level,
    }

    if not settings.SNS_TOPIC_ARN:
        logger.info(f"[DEV] Stock event skipped: {json.dumps(event)}")
        return

    try:
        sns = boto3.client("sns", region_name=settings.AWS_REGION)
        sns.publish(
            TopicArn=settings.SNS_TOPIC_ARN,
            Message=json.dumps(event),
            Subject=f"Low Stock Alert: {product_name}",
        )
        logger.info(f"SNS event published: {sku}")
    except Exception as e:
        logger.error(f"SNS publish failed: {e}")