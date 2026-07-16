# =========================================================================
# RDS POSTGRESQL DATABASE
# =========================================================================
resource "aws_db_subnet_group" "rds" {
  name       = "stockpilot-rds-subnet-group"
  subnet_ids = [aws_subnet.private1.id, aws_subnet.private2.id]

  tags = {
    Name = "stockpilot-rds-subnet-group"
  }
}

resource "aws_db_instance" "postgres" {
  allocated_storage      = 20
  max_allocated_storage  = 100
  engine                 = "postgres"
  engine_version         = "16.3"
  instance_class         = "db.t4g.micro"
  db_name                = "stockpilotdb"
  username               = "stockpilot_admin"
  password               = "SuperSecurePassword123!"
  db_subnet_group_name   = aws_db_subnet_group.rds.name
  vpc_security_group_ids = [aws_security_group.rds.id] # References security.tf cleanly
  skip_final_snapshot    = true
  publicly_accessible    = false

  tags = {
    Name = "stockpilot-postgres"
  }
}
