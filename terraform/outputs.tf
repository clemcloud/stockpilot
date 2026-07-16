# The EKS Cluster Endpoint
output "eks_cluster_endpoint" {
  description = "The endpoint for your Kubernetes API server"
  value       = aws_eks_cluster.main.endpoint
}

# The Cluster Name
output "eks_cluster_name" {
  description = "The name of your Kubernetes cluster"
  value       = aws_eks_cluster.main.name
}

# The Database Endpoint
output "rds_database_endpoint" {
  description = "The connection string (host:port) for your PostgreSQL database"
  value       = aws_db_instance.postgres.endpoint
}

# The Fargate Role ARN
output "fargate_pod_role_arn" {
  description = "The ARN of the IAM role used by Fargate pods"
  value       = aws_iam_role.fargate_pod.arn
}

# SNS Topic ARN — paste this into .env as SNS_TOPIC_ARN
output "sns_topic_arn" {
  description = "The ARN of the SNS topic for stock events"
  value       = aws_sns_topic.stock_updates.arn
}

# SQS Queue URL — useful for debugging
output "sqs_queue_url" {
  description = "The URL of the SQS task queue"
  value       = aws_sqs_queue.task_queue.url
}
