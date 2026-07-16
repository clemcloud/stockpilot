# =========================================================================
# EKS CONTROL PLANE BRAIN & ROLES
# =========================================================================
resource "aws_iam_role" "eks_cluster" {
  name = "stockpilot-eks-cluster-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "eks.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "eks_cluster_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.eks_cluster.name
}

resource "aws_eks_cluster" "main" {
  name     = "stockpilot-cluster"
  role_arn = aws_iam_role.eks_cluster.arn

  vpc_config {
    subnet_ids = [
      aws_subnet.private1.id,
      aws_subnet.private2.id,
      aws_subnet.public1.id,
      aws_subnet.public2.id
    ]
    endpoint_private_access = true
    endpoint_public_access  = true
    security_group_ids      = [aws_security_group.eks_pods.id]
  }

  depends_on = [aws_iam_role_policy_attachment.eks_cluster_policy]
}

# =========================================================================
# EKS MANAGED ADD-ONS
# =========================================================================
resource "aws_eks_addon" "vpc_cni" {
  cluster_name                = aws_eks_cluster.main.name
  addon_name                  = "vpc-cni"
  resolve_conflicts_on_update = "PRESERVE"
}

# =========================================================================
# SERVERLESS FARGATE COMPUTE PROFILES & ROLES
# =========================================================================
resource "aws_iam_role" "fargate_pod" {
  name = "stockpilot-fargate-pod-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "eks-fargate-pods.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "fargate_pod_execution" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSFargatePodExecutionRolePolicy"
  role       = aws_iam_role.fargate_pod.name
}

# -------------------------------------------------------------------------
# Messaging Permissions for StockPilot Pods
# -------------------------------------------------------------------------
resource "aws_iam_policy" "fargate_messaging_policy" {
  name        = "stockpilot-fargate-messaging-policy"
  description = "Allows EKS Fargate pods to publish to SNS and process from SQS"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes",
          "sqs:SendMessage"
        ]
        Resource = aws_sqs_queue.task_queue.arn
      },
      {
        Effect = "Allow"
        Action = [
          "sns:Publish"
        ]
        Resource = aws_sns_topic.stock_updates.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "fargate_messaging_attach" {
  policy_arn = aws_iam_policy.fargate_messaging_policy.arn
  role       = aws_iam_role.fargate_pod.name
}

# -------------------------------------------------------------------------
# The Fargate Profile
# -------------------------------------------------------------------------
resource "aws_eks_fargate_profile" "main" {
  cluster_name           = aws_eks_cluster.main.name
  fargate_profile_name   = "stockpilot-app-profile"
  pod_execution_role_arn = aws_iam_role.fargate_pod.arn
  subnet_ids             = [aws_subnet.private1.id, aws_subnet.private2.id]

  selector {
    namespace = "default"
  }
  selector {
    namespace = "stockpilot"
  }
}
