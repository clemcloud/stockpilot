resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "main-vpc"
  }
}

# The next is for the public subnet which will host the public resources like load balancers, bastion hosts, etc.
resource "aws_subnet" "public1" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true

  tags = {
    Name                                       = "stockpilot-public-subnet-1"
    "kubernetes.io/cluster/stockpilot-cluster" = "shared"
    "kubernetes.io/role/elb"                   = "1"
  }
}

resource "aws_subnet" "public2" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "us-east-1b"
  map_public_ip_on_launch = true

  tags = {
    Name                                       = "stockpilot-public-subnet-2"
    "kubernetes.io/cluster/stockpilot-cluster" = "shared"
    "kubernetes.io/role/elb"                   = "1"
  }
}

# The next is for the private subnet which will host the private resources like databases, application servers, etc.
resource "aws_subnet" "private1" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.10.0/24"
  availability_zone = "us-east-1a"

  tags = {
    Name                                       = "stockpilot-private-subnet-1"
    "kubernetes.io/cluster/stockpilot-cluster" = "shared"
    "kubernetes.io/role/internal-elb"          = "1"
  }
}

resource "aws_subnet" "private2" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.11.0/24"
  availability_zone = "us-east-1b"

  tags = {
    Name                                       = "stockpilot-private-subnet-2"
    "kubernetes.io/cluster/stockpilot-cluster" = "shared"
    "kubernetes.io/role/internal-elb"          = "1"
  }
}

# The internet gateway is used to allow communication between the VPC and the internet.
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "stockpilot-igw"
  }
}

# =========================================================================
# NEW UPDATES: NAT Gateway & Outbound Private Route Configurations
# =========================================================================

# Allocate a static public IP address for the NAT Gateway
resource "aws_eip" "nat" {
  domain     = "vpc"
  depends_on = [aws_internet_gateway.igw]

  tags = {
    Name = "stockpilot-nat-eip"
  }
}

# Create the NAT Gateway and house it out in public subnet 1
resource "aws_nat_gateway" "nat" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public1.id

  tags = {
    Name = "stockpilot-nat-gw"
  }

  depends_on = [aws_internet_gateway.igw]
}

# Public Route Table: Directs internet traffic to the Internet Gateway
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "stockpilot-public-rt"
  }
}

resource "aws_route_table_association" "public1" {
  subnet_id      = aws_subnet.public1.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "public2" {
  subnet_id      = aws_subnet.public2.id
  route_table_id = aws_route_table.public.id
}

# Private Route Table: Directs internal outbound traffic to the NAT Gateway
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat.id
  }

  tags = {
    Name = "stockpilot-private-rt"
  }
}

resource "aws_route_table_association" "private1" {
  subnet_id      = aws_subnet.private1.id
  route_table_id = aws_route_table.private.id
}

resource "aws_route_table_association" "private2" {
  subnet_id      = aws_subnet.private2.id
  route_table_id = aws_route_table.private.id
}
