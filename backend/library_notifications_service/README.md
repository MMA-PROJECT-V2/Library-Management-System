# Library Notifications Service

A Django-based microservice for managing library notifications (Email and SMS) with asynchronous processing using Celery.

## Features

- ✅ Email and SMS notifications
- ✅ Template-based notifications with Django template engine
- ✅ Asynchronous processing with Celery
- ✅ Automatic retry with exponential backoff
- ✅ Comprehensive logging and statistics
- ✅ RESTful API with Django REST Framework
- ✅ Bulk operations support
- ✅ Periodic task scheduling
- ✅ Admin interface for management

## Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL 12+ (or SQLite for development)
- Redis 6+
- RabbitMQ 3.8+

### Installation

```bash
# Clone repository
git clone <repository-url>
cd library-notifications-service

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

### Running the Service

```bash
# Terminal 1: Django development server
python manage.py runserver

# Terminal 2: Celery worker
celery -A library_notifications_service worker --loglevel=info

# Terminal 3: Celery beat (periodic tasks)
celery -A library_notifications_service beat --loglevel=info

# Optional: Celery monitoring with Flower
pip install flower
celery -A library_notifications_service flower
# Access at http://localhost:5555
```

## API Documentation

### Base URL
```
http://localhost:8000/api/
```

### Endpoints

#### Notifications

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/notifications/` | List all notifications |
| POST | `/notifications/` | Create notification |
| GET | `/notifications/{id}/` | Get notification details |
| PUT | `/notifications/{id}/` | Update notification |
| DELETE | `/notifications/{id}/` | Delete notification |
| POST | `/notifications/{id}/retry/` | Retry failed notification |
| GET | `/notifications/user/{user_id}/` | Get user notifications |
| GET | `/notifications/pending/` | Get pending notifications |
| GET | `/notifications/recent/` | Get recent notifications |
| GET | `/notifications/stats/` | Get statistics |
| POST | `/notifications/send_from_template/` | Create from template |
| POST | `/notifications/bulk_create/` | Bulk create |

#### Templates

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/templates/` | List all templates |
| POST | `/templates/` | Create template |
| GET | `/templates/{id}/` | Get template details |
| PUT | `/templates/{id}/` | Update template |
| DELETE | `/templates/{id}/` | Delete template |
| POST | `/templates/{id}/test/` | Test template |

### Example Requests

#### Create Notification

```bash
curl -X POST http://localhost:8000/api/notifications/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 123,
    "type": "EMAIL",
    "subject": "Book Due Reminder",
    "message": "Your book is due tomorrow"
  }'
```

#### Send from Template

```bash
curl -X POST http://localhost:8000/api/notifications/send_from_template/ \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": 1,
    "user_id": 123,
    "context": {
      "user_name": "John Doe",
      "book_title": "Django for Beginners",
      "due_date": "2024-12-15"
    }
  }'
```

#### Bulk Create

```bash
curl -X POST http://localhost:8000/api/notifications/bulk_create/ \
  -H "Content-Type: application/json" \
  -d '{
    "notifications": [
      {
        "user_id": 1,
        "type": "EMAIL",
        "subject": "Overdue Book",
        "message": "Please return your book"
      },
      {
        "user_id": 2,
        "type": "SMS",
        "subject": "Reservation Ready",
        "message": "Your book is ready for pickup"
      }
    ]
  }'
```

#### Get Statistics

```bash
curl http://localhost:8000/api/notifications/stats/?days=7
```

## Configuration

### Required Environment Variables

```bash
# Django
SECRET_KEY=your-secret-key
DEBUG=0
ALLOWED_HOSTS=localhost,yourdomain.com

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=library_notifications
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Email (Gmail example)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=1
DEFAULT_FROM_EMAIL=noreply@library.com

# Celery
CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### User Email Integration

**IMPORTANT**: You must implement the `get_user_email()` function in `notifications/tasks.py` to fetch user emails from your user service or database.

Example implementations are provided in the code comments.

## Templates

Templates use Django template syntax for variable substitution.

### Creating a Template

```python
# Via Django shell
from notifications.models import NotificationTemplate

NotificationTemplate.objects.create(
    name='book_due_reminder',
    type='EMAIL',
    subject_template='Book Due: {{ book_title }}',
    message_template='Hello {{ user_name }}, your book "{{ book_title }}" is due on {{ due_date }}.'
)
```

### Using a Template

```python
# Via API
POST /api/notifications/send_from_template/
{
  "template_id": 1,
  "user_id": 123,
  "context": {
    "user_name": "John",
    "book_title": "Django Guide",
    "due_date": "2024-12-15"
  }
}
```

## Testing

```bash
# Run all tests
python manage.py test

# Run specific test file
python manage.py test notifications.tests

# With coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

## Production Deployment

### Using Gunicorn + Nginx

```bash
# Install Gunicorn
pip install gunicorn

# Run Gunicorn
gunicorn library_notifications_service.wsgi:application --bind 0.0.0.0:8000 --workers 4

# Nginx configuration example
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static/ {
        alias /path/to/staticfiles/;
    }
}
```

### Using Supervisor

Create `/etc/supervisor/conf.d/notifications.conf`:

```ini
[program:notifications_django]
command=/path/to/venv/bin/gunicorn library_notifications_service.wsgi:application --bind 0.0.0.0:8000
directory=/path/to/project
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/notifications/django.log

[program:notifications_celery]
command=/path/to/venv/bin/celery -A library_notifications_service worker --loglevel=info
directory=/path/to/project
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/notifications/celery.log

[program:notifications_beat]
command=/path/to/venv/bin/celery -A library_notifications_service beat --loglevel=info
directory=/path/to/project
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/notifications/beat.log
```

Then:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start all
```

### Docker (Optional)

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "library_notifications_service.wsgi:application", "--bind", "0.0.0.0:8000"]
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgres:14
    environment:
      POSTGRES_DB: library_notifications
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

  rabbitmq:
    image: rabbitmq:3-management-alpine

  web:
    build: .
    command: gunicorn library_notifications_service.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
      - rabbitmq
    env_file:
      - .env

  celery:
    build: .
    command: celery -A library_notifications_service worker --loglevel=info
    volumes:
      - .:/app
    depends_on:
      - db
      - redis
      - rabbitmq
    env_file:
      - .env

  celery-beat:
    build: .
    command: celery -A library_notifications_service beat --loglevel=info
    volumes:
      - .:/app
    depends_on:
      - db
      - redis
      - rabbitmq
    env_file:
      - .env

volumes:
  postgres_data:
```

Run with:
```bash
docker-compose up -d
```

## Monitoring

### Celery Monitoring with Flower

```bash
pip install flower
celery -A library_notifications_service flower

# Access at http://localhost:5555
```

### Logs

```bash
# View Django logs
tail -f logs/notifications.log

# View Celery logs
tail -f logs/celery.log

# All logs
tail -f logs/*.log
```

## Troubleshooting

### Celery Not Processing Tasks

```bash
# Check Celery is running
ps aux | grep celery

# Check RabbitMQ
sudo systemctl status rabbitmq-server

# Check Redis
redis-cli ping

# Purge all tasks
celery -A library_notifications_service purge
```

### Email Not Sending

```bash
# Test SMTP connection
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Message', 'from@example.com', ['to@example.com'])
```

### Database Connection Issues

```bash
# Test database connection
python manage.py dbshell

# Check migrations
python manage.py showmigrations
```

## Admin Interface

Access at: `http://localhost:8000/admin/`

Features:
- View and manage notifications
- Create and test templates
- View notification logs
- Bulk operations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License

## Support

For issues and questions:
- Check logs in `logs/` directory
- Review Django admin at `/admin/`
- Monitor Celery with Flower
- Check notification logs in database