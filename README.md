# Gundam Model Store

A Django-based online store for Gundam models, featuring product listings, category browsing, shopping cart, user authentication, and order management.

## Features
- **Home page** with featured discounted products
- **Product catalog** with paginated listings (12 items per page)
- **Category browsing** with banner images and hierarchical navigation
- **Product search** with pagination support
- **Shopping cart** with add/remove/update functionality
- **User authentication** (registration, login, logout, profile management)
- **Order management** with checkout and order history
- **Responsive design** using Bootstrap 5
- **Local media storage** for product images and user avatars

## Tech Stack
- **Backend**: Django 4.2+
- **Frontend**: Bootstrap 5, jQuery, custom CSS/JS
- **Database**: SQLite (development), PostgreSQL (production ready)
- **Storage**: Local file system (development), AWS S3 compatible (production ready)
- **Authentication**: Django built-in authentication system

## Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/kalpakjian/gundam-store.git
   cd gundam-store
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root:
   ```
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```

5. **Apply migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Collect static files**
   ```bash
   python manage.py collectstatic --noinput
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```

9. **Access the application**
   - Store: http://127.0.0.1:8000/
   - Admin: http://127.0.0.1:8000/admin/

## Data Setup

### Populate sample data
```bash
# Create sample users
python manage.py create_users

# Populate products and categories
python manage.py populate_data

# Migrate product images (if needed)
python manage.py migrate_images
```

### Backup and restore
```bash
# Create backup
python manage.py dumpdata > backup.json

# Restore from backup
python manage.py loaddata backup.json
```

## Project Structure
```
gundam-store/
├── gundam_store/          # Main Django project
├── accounts/              # User management app
├── store/                 # Product catalog and shopping
├── static/                # Static files (CSS, JS, images)
├── media/                 # User uploaded files
├── templates/             # HTML templates
├── requirements.txt       # Python dependencies
├── manage.py             # Django management script
└── README.md             # This file
```

## Development

### Adding new products
1. Access Django admin at `/admin/`
2. Log in with superuser credentials
3. Navigate to Store > Products
4. Add new products with images and descriptions

### Customization
- **Templates**: Located in `accounts/templates/` and `store/templates/`
- **Static files**: In `static/` directory
- **Models**: Defined in `accounts/models.py` and `store/models.py`
- **Views**: In `accounts/views.py` and `store/views.py`

## Production Deployment

### Environment variables
Set these in production:
```
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DATABASE_URL=postgres://user:password@host:port/database
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_STORAGE_BUCKET_NAME=your-bucket-name
```

### Using Docker
```bash
# Build image
docker build -t gundam-store .

# Run container
docker run -p 8000:8000 gundam-store
```

### Using Gunicorn
```bash
pip install gunicorn
gunicorn gundam_store.wsgi:application --bind 0.0.0.0:8000
```

## Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Support
For support, email support@gundam-store.com or create an issue in the GitHub repository.
