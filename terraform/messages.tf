# =========================================================================
# ASYNCHRONOUS MESSAGING: SNS (Pub/Sub) & SQS (Queue)
# =========================================================================

# 1. The SNS Topic: Acts as the "Broadcast Hub"
resource "aws_sns_topic" "stock_updates" {
  name = "stockpilot-updates-topic"
}

# 2. The SQS Queue: Acts as the "Holding Pen" for tasks
resource "aws_sqs_queue" "task_queue" {
  name                       = "stockpilot-task-queue"
  delay_seconds              = 0
  max_message_size           = 2048
  message_retention_seconds  = 86400 # 1 day
  receive_wait_time_seconds  = 10
  visibility_timeout_seconds = 360 # Fixed: Must be >= 6x the Lambda timeout (60s * 6)
}

# 3. The Subscription: Bridges SNS to SQS
# This ensures that any message sent to the topic is automatically forwarded to the queue
resource "aws_sns_topic_subscription" "queue_subscription" {
  topic_arn = aws_sns_topic.stock_updates.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.task_queue.arn
}

# 4. SQS Queue Policy: Allows the SNS topic to push messages into the queue
resource "aws_sqs_queue_policy" "sqs_policy" {
  queue_url = aws_sqs_queue.task_queue.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "sns.amazonaws.com" }
      Action    = "sqs:SendMessage"
      Resource  = aws_sqs_queue.task_queue.arn
      Condition = {
        ArnEquals = { "aws:SourceArn" : aws_sns_topic.stock_updates.arn }
      }
    }]
  })
}
