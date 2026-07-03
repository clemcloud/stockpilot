# StockPilot

> Prevent stockouts before they happen.

---

## The Problem

Businesses don't run out of stock because they didn't order enough.
They run out because nobody saw it coming.

Most inventory decisions are made from memory, gut feeling, or an end-of-day
manual count. By the time someone notices a product is critically low, the
customer has already left empty handed and the revenue is already gone.

StockPilot is built to close that gap.

---

## What It Is

StockPilot is a cloud-native inventory intelligence platform. It tracks stock
levels in real time through a lightweight POS terminal, detects when products
are approaching critical levels, and uses Amazon Bedrock to analyze sales
patterns and recommend exactly what to reorder and when.

The warehouse manager doesn't chase stock problems. StockPilot surfaces them
automatically with the context needed to act immediately.

---

## How It Works

Every sale recorded at the counter hits the FastAPI backend and updates stock
in real time. When a product crosses its minimum stock threshold, an event
fires to Amazon SNS. From there, SQS buffers it for reliable delivery, Lambda
picks it up, pulls 30 days of sales history from the database, and sends it
to Amazon Bedrock for analysis. The warehouse manager receives an email with
a clear recommendation — current stock level, average daily sales velocity,
estimated days to stockout, and suggested reorder quantity.

No dashboards to refresh. No spreadsheets to update. The right information
reaches the right person at the right time.

---

## Architecture

StockPilot is documented across five engineering layers:

| Layer | Description |
|---|---|
| [Application Layer](./docs/01-application-layer.md) | FastAPI backend, PostgreSQL, business logic and API design |
| [Cloud Infrastructure](./docs/02-cloud-infrastructure.md) | AWS services, Terraform IaC, networking and event pipeline |
| [Platform & Delivery](./docs/03-platform-delivery.md) | Docker, Kubernetes on EKS, GitHub Actions CI/CD |
| [Observability](./docs/04-observability.md) | Prometheus metrics scraping, Grafana dashboards |
| [Security & Identity](./docs/05-security-identity.md) | JWT authentication, AWS IAM least privilege, Secrets Manager |

---

## Technology Stack

**Application**
Python 3.13, FastAPI, SQLAlchemy, Pydantic, Passlib, PostgreSQL

**Cloud Infrastructure**
AWS EKS, RDS, SNS, SQS, Lambda, Bedrock Nova Lite, SES, S3, Terraform

**Platform & Delivery**
Docker, Kubernetes, GitHub Actions, Amazon ECR

**Observability**
Prometheus, Grafana

---

## Project Status

| Layer | Status |
|---|---|
| Application Layer | ✅ Complete |
| Cloud Infrastructure | 🔄 In Progress |
| Platform & Delivery | 🔄 In Progress |
| Observability | ⏳ Planned |
| Security & Identity | ⏳ Planned |

---

## Running Locally

```bash
# Clone the repo
git clone https://github.com/clemcloud/stockpilot.git
cd stockpilot

# Set up environment
python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Open .env and fill in DATABASE_URL and SECRET_KEY

# Create the database
psql -U postgres -c "CREATE DATABASE stockpilot;"

# Start the server
uvicorn main:app --reload
```

API documentation available at `http://localhost:8000/docs`

---

## API Reference

| Method | Endpoint | Description | Protected |
|---|---|---|---|
| POST | /auth/login | Warehouse manager login | No |
| POST | /users | Register a new user | No |
| GET | /users/{id} | Get user by ID | Yes |
| PATCH | /users/{id} | Update user profile | Yes |
| GET | /products | List all products | Yes |
| POST | /products | Add a new product | Yes |
| GET | /products/{id} | Get product by ID | Yes |
| PATCH | /products/{id} | Update product details | Yes |
| POST | /inventory/log | Log a stock movement | Yes |
| GET | /inventory/alerts | View low stock alerts | Yes |
| POST | /sales | Process a sale at POS | No |
| GET | /sales | View all sales history | Yes |
| GET | /sales/{id} | Get sale by ID | Yes |

---

## Repository Structure
