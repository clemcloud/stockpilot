# =========================================================================
# SECURITY GROUPS
# =========================================================================

# ALB Security Group — allows public web traffic
resource "aws_security_group" "alb" {
  name        = "stockpilot-alb-sg"
  description = "Allows public web traffic to hit the load balancer"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "stockpilot-alb-sg"
  }
}

# EKS Pods Security Group — only accepts traffic from ALB
resource "aws_security_group" "eks_pods" {
  name        = "stockpilot-eks-pods-sg"
  description = "Allows traffic strictly coming from the ALB"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "stockpilot-eks-pods-sg"
  }
}

# Lambda Security Group — allows Lambda to reach RDS and AWS services
resource "aws_security_group" "lambda" {
  name        = "stockpilot-lambda-sg"
  description = "Allows Lambda to query RDS and reach AWS services"
  vpc_id      = aws_vpc.main.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "stockpilot-lambda-sg"
  }
}

# RDS Security Group — updated to allow traffic from EKS control plane / Fargate pods
resource "aws_security_group" "rds" {
  name        = "stockpilot-rds-sg"
  description = "Allows database traffic from EKS pods and Lambda"
  vpc_id      = aws_vpc.main.id

  # FIX: Allow ingress on 5432 from the default EKS cluster security group 
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_eks_cluster.main.vpc_config[0].cluster_security_group_id]
  }

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.lambda.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "stockpilot-rds-sg"
  }
}
