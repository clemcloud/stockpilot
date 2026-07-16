import json
import os
import boto3
import psycopg2
import urllib.request
from datetime import datetime, timedelta

DB_HOST = os.environ["DB_HOST"]
DB_NAME = os.environ["DB_NAME"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
S3_BUCKET = os.environ["S3_BUCKET_NAME"]
SES_SENDER = os.environ["SES_SENDER_EMAIL"]
MANAGER_EMAIL = os.environ["MANAGER_EMAIL"]
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"


def get_db_connection():
    """Establishes an isolated DB connection wrapper."""
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        connect_timeout=5,
    )


def get_sales_history(conn, product_id: int) -> list:
    """Uses the reused connection pointer to fetch history."""
    cursor = conn.cursor()
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    cursor.execute("""
        SELECT
            DATE(s.timestamp) as sale_date,
            SUM(si.quantity) as total_sold
        FROM sales_items si
        JOIN sales s ON si.sale_id = s.id
        WHERE si.product_id = %s
        AND s.timestamp >= %s
        GROUP BY DATE(s.timestamp)
        ORDER BY sale_date ASC
    """, (product_id, thirty_days_ago))

    rows = cursor.fetchall()
    cursor.close()

    return [{"date": str(row[0]), "quantity_sold": row[1]} for row in rows]


def get_ai_recommendation(
    product_name: str,
    sku: str,
    current_stock: int,
    min_stock_level: int,
    sales_history: list,
) -> str:
    total_sold = sum(day["quantity_sold"] for day in sales_history)
    days_with_sales = len(sales_history)
    avg_daily_sales = round(total_sold / days_with_sales, 1) if days_with_sales > 0 else 0
    days_until_stockout = round(current_stock / avg_daily_sales, 1) if avg_daily_sales > 0 else "unknown"

    prompt = f"""You are an inventory management assistant.

Product: {product_name} (SKU: {sku})
Current Stock: {current_stock} units
Minimum Stock Level: {min_stock_level} units
Average Daily Sales: {avg_daily_sales} units per day
Estimated Days Until Stockout: {days_until_stockout} days
Sales History last 30 days: {json.dumps(sales_history)}

Based on this data provide a brief actionable restock recommendation.
Include how urgent the situation is, how many units to reorder, and why.
Keep it under 100 words. Be direct and practical."""

    payload = json.dumps({
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }).encode("utf-8")

    req = urllib.request.Request(
        GEMINI_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode("utf-8"))
        return result["candidates"][0]["content"]["parts"][0]["text"]


def save_report_to_s3(report: dict) -> str:
    s3 = boto3.client("s3", region_name=AWS_REGION)
    key = f"reports/{report['sku']}/{datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S')}.json"
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=key,
        Body=json.dumps(report),
        ContentType="application/json",
    )
    return key


def send_alert_email(
    product_name: str,
    sku: str,
    current_stock: int,
    min_stock_level: int,
    recommendation: str,
    s3_key: str,
) -> None:
    ses = boto3.client("ses", region_name=AWS_REGION)
    ses.send_email(
        Source=SES_SENDER,
        Destination={"ToAddresses": [MANAGER_EMAIL]},
        Message={
            "Subject": {
                "Data": f"⚠️ Low Stock Alert — {product_name}"
            },
            "Body": {
                "Text": {
                    "Data": f"""StockPilot Low Stock Alert

Product:        {product_name}
SKU:            {sku}
Current Stock:  {current_stock} units
Minimum Level:  {min_stock_level} units

AI RECOMMENDATION
─────────────────
{recommendation}

Full report saved to S3: {s3_key}

— StockPilot"""
                }
            }
        }
    )


def handler(event, context):
    # Initialize connection context outside loop tracking
    conn = None
    try:
        conn = get_db_connection()
        
        for record in event["Records"]:
            try:
                message = json.loads(record["body"])
                if "Message" in message:
                    message = json.loads(message["Message"])

                product_id = message["product_id"]
                product_name = message["product_name"]
                sku = message["sku"]
                current_stock = message["current_stock"]
                min_stock_level = message["min_stock_level"]

                print(f"Processing alert for {product_name} ({sku})")

                # Pass shared connection handler safely
                sales_history = get_sales_history(conn, product_id)
                print(f"Retrieved {len(sales_history)} days of sales history")

                recommendation = get_ai_recommendation(
                    product_name=product_name,
                    sku=sku,
                    current_stock=current_stock,
                    min_stock_level=min_stock_level,
                    sales_history=sales_history,
                )
                print("Gemini recommendation received")

                report = {
                    "product_id": product_id,
                    "product_name": product_name,
                    "sku": sku,
                    "current_stock": current_stock,
                    "min_stock_level": min_stock_level,
                    "sales_history": sales_history,
                    "recommendation": recommendation,
                    "generated_at": datetime.utcnow().isoformat(),
                }
                s3_key = save_report_to_s3(report)
                print(f"Report saved to S3: {s3_key}")

                send_alert_email(
                    product_name=product_name,
                    sku=sku,
                    current_stock=current_stock,
                    min_stock_level=min_stock_level,
                    recommendation=recommendation,
                    s3_key=s3_key,
                )
                print(f"Alert email sent for {product_name}")

            except Exception as e:
                print(f"Error processing record item: {e}")
                # Re-raise so SQS dead-letter queue mechanics catch broken records
                raise e
                
    finally:
        if conn:
            conn.close()