# Real's Mobile Inventory System

A Django-based inventory management system for tracking products, raw materials, sales, and expenses.

## Features

- 📦 Product & Raw Material Stock Management
- 💰 Sales & Expenses Tracking
- 📜 History Log & Audit Trail
- 🔔 Low Stock Notifications
- 📊 Batch Management for Products & Materials
- 🔐 User Authentication & Authorization
- 📱 Mobile-Responsive Design with PWA Support

## Tech Stack

- **Backend**: Django 5.x
- **Database**: PostgreSQL
- **Frontend**: Bootstrap 5, Vanilla JavaScript
- **Fonts**: Google Fonts (Poppins)

## Setup Instructions

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   cd mobile_inventory
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables**
   - Copy `.env.example` to `.env`
   - Update the values in `.env`:
     ```
     SECRET_KEY=your-secret-key-here
     DEBUG=True
     DB_NAME=reals_local
     DB_USER=postgres
     DB_PASSWORD=your-password
     DB_HOST=localhost
     DB_PORT=5432
     ALLOWED_HOSTS=localhost,127.0.0.1
     ```

6. **Create PostgreSQL database**
   ```sql
   CREATE DATABASE reals_local;
   ```

7. **Run migrations** (if using managed models)
   ```bash
   python manage.py migrate
   ```

8. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

9. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

10. **Run the development server**
    ```bash
    python manage.py runserver
    ```

11. **Access the application**
    - Main app: http://localhost:8000
    - Admin panel: http://localhost:8000/admin

## Project Structure

```
mobile_inventory/
├── inventory/              # Main app
│   ├── models.py          # Database models
│   ├── views.py           # View functions
│   ├── admin.py           # Admin panel configuration
│   └── migrations/        # Database migrations
├── mobile_inventory/      # Project settings
│   ├── settings.py        # Django settings
│   ├── urls.py            # URL routing
│   └── wsgi.py            # WSGI configuration
├── templates/             # HTML templates
│   ├── base.html          # Base template
│   ├── dashboard.html     # Dashboard
│   ├── login.html         # Login page
│   └── ...
├── static/                # Static files
│   ├── images/            # Images
│   └── service-worker.js  # PWA service worker
├── staticfiles/           # Collected static files
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
└── README.md              # This file
```

## Security Notes

⚠️ **Important Security Practices:**

1. **Never commit `.env` file** - It contains sensitive credentials
2. **Change SECRET_KEY** - Generate a new one for production
3. **Set DEBUG=False** in production
4. **Update ALLOWED_HOSTS** - Add your domain/IP
5. **Use strong database passwords**
6. **Keep dependencies updated** - Run `pip list --outdated` regularly

## Database Schema

The system uses the following main tables:
- `products` - Product catalog
- `product_inventory` - Stock levels
- `raw_materials` - Raw material catalog
- `raw_material_inventory` - Raw material stock
- `sales` - Sales records
- `expenses` - Expense records
- `withdrawals` - Stock withdrawals
- `notifications` - Low stock alerts

## Admin Panel

Access the Django admin panel at `/admin` to:
- Manage products and raw materials
- View and edit inventory levels
- Track sales and expenses
- Monitor stock changes
- Manage users and permissions

## PWA Features

The app includes a service worker for offline functionality:
- Caches important pages and assets
- Works offline with cached data
- Automatic cache updates

## Development

### Running Tests
```bash
python manage.py test
```

### Creating Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Database Shell
```bash
python manage.py dbshell
```

## Production Deployment

1. Set environment variables:
   - `DEBUG=False`
   - `SECRET_KEY=<strong-random-key>`
   - `ALLOWED_HOSTS=yourdomain.com`

2. Use a production database (e.g., Supabase, AWS RDS)

3. Configure static files serving (e.g., WhiteNoise, CDN)

4. Use a production server (e.g., Gunicorn, uWSGI)

5. Set up HTTPS/SSL

6. Configure database backups

## License

Proprietary - Real's Inventory System

## Support

For issues or questions, contact the development team.
