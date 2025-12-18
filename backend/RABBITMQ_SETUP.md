# 🚀 RabbitMQ Setup Guide - Complete Instructions

## Prerequisites

- Python 3.9+
- Docker (for RabbitMQ)
- MySQL running with databases
- Redis (for Celery)

---

## Step 1: Install Dependencies

Install `pika` in **ALL** services:

```bash
# User Service
cd backend/user_service
pip install pika==1.3.2

# Books Service
cd ../books_service
pip install pika==1.3.2

# Loans Service
cd ../loans_service
pip install pika==1.3.2

# Notifications Service
cd ../library_notifications_service
pip install pika==1.3.2
```

## Step 2: Environment Configuration

Add these lines to the `.env` file of **EVERY** service:

```bash
# RabbitMQ Configuration
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_VHOST=/
```

## Step 3: Start RabbitMQ

Run RabbitMQ using Docker:

```bash
docker run -d --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  -e RABBITMQ_DEFAULT_USER=guest \
  -e RABBITMQ_DEFAULT_PASS=guest \
  rabbitmq:3.12-management
```

Access the Management UI at: [http://localhost:15672](http://localhost:15672) (guest/guest)

## Step 4: Verify Integration

Run the comprehensive test script to verify all event publishers:

```bash
cd backend
python test_all_events.py
```

## Step 5: Start Notification Consumer

The consumer listens for events and sends emails.

```bash
cd backend/library_notifications_service
python manage.py start_consumer
```

## Step 6: Start User Service Consumer

The User Service now needs a consumer running to process registration requests.

```bash
cd backend/user_service
python manage.py start_user_consumer
```

## Step 7: Start Book Service Consumer

The Books Service also needs a consumer running for async creation/updates.

```bash
cd backend/books_service
python manage.py start_book_consumer
```

## Step 8: Start Loan Service Consumer

The Loans Service consumer handles complex transactions (Create, Return, Renew).

```bash
cd backend/loans_service
python manage.py start_loan_consumer
```

## Troubleshooting

- **ConnectionResetError**: The `rabbitmq_client.py` includes auto-reconnect logic. If errors persist, check if the Docker container is running.
- **ModuleNotFoundError**: Ensure `pika` is installed in the active virtual environment.
- **Authentication Error**: Check `RABBITMQ_USER` and `RABBITMQ_PASSWORD` in `.env` files.
