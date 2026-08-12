# Gundam Model Store

A Django-based online store for Gundam models, featuring product listings, category browsing, search, shopping cart, checkout, and user authentication.

## Features

- **Home page** with featured discounted products and latest product carousel
- **Product listing** with pagination (9 items per page)
- **Product detail** pages with image gallery and scale icons (RG/HG/MG/PG)
- **Category browsing** with pagination (12 items per page)
- **Search** with pagination
- **Shopping cart** for both logged-in and anonymous (session-based) users
- **Checkout** with shipping address and order creation (transaction-safe)
- **Order history** for logged-in users
- **User authentication** with AJAX modal login/register
- **User profile** with avatar upload and address management
- **Image upload** for product images (local storage)
- **Admin interface** for managing products, categories, and images

## Tech Stack

- **Backend:** Django 5.2
- **Database:** SQLite (development) / PostgreSQL (production recommended)
- **Frontend:** Bootstrap 5.3, jQuery 3.3, Font Awesome, Lightbox2
- **Image storage:** Local filesystem (`media/` directory)

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/kalpakjian/gundam-store.git
   cd gundam-store
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file (copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and set your `SECRET_KEY` (generate one with):
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(50))"
   ```

5. Apply migrations:
   ```bash
   python manage.py migrate
   ```

6. (Optional) Populate sample data:
   ```bash
   python manage.py shell < populate_data.py
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

8. Visit http://127.0.0.1:8000

## Project Structure

```
gundam-store/
├── gundam_store/          # Django project settings
│   ├── settings.py        # Settings (reads from .env)
│   ├── urls.py            # Root URL configuration
│   └── ...
├── store/                 # Main store app
│   ├── models.py          # Category, Product, Cart, Order models
│   ├── views.py           # Product, cart, checkout, profile views
│   ├── urls.py            # Store URL routes
│   ├── admin.py           # Admin configuration
│   ├── templates/store/   # Store templates
│   └── templatetags/      # Custom template tags
├── accounts/              # User account app
│   ├── models.py          # UserProfile model
│   ├── views.py           # Login, register, logout views
│   ├── forms.py           # Registration and profile forms
│   ├── context_processors.py  # Injects auth forms into all templates
│   └── templates/accounts/    # Auth modal templates
├── static/                # CSS, JS, images, fonts
├── manage.py
├── requirements.txt
├── .env.example           # Environment variable template
└── .gitignore
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | `django-insecure-dev-key-change-in-production` |
| `DEBUG` | Debug mode (`True`/`False`) | `False` |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | `localhost,127.0.0.1` |

## Future Improvements

- Add unit and integration tests
- Migrate to PostgreSQL for production
- Add cloud storage (S3/Cloudinary) for media files
- Implement payment gateway integration (Stripe/PayPal)
- Add email verification for registration
- Add rate limiting for login attempts
- Optimize product images with thumbnails
- Add product reviews and ratings
