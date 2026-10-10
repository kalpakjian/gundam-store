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
- **Image upload** for product images, stored on Cloudinary and served from its CDN
- **Admin interface** for managing products, categories, and images
- **Bundled product catalogue** — a fixture with 46 products, 11 categories and 220 images, seeded with a single command

## Tech Stack

- **Backend:** Django 5.2.18 (LTS)
- **Database:** SQLite (development) / PostgreSQL (production recommended)
- **Frontend:** Bootstrap 5.3.8 with vanilla JavaScript (no jQuery or icon-font dependencies)
- **Image storage:** Cloudinary — images are uploaded to and served from Cloudinary's CDN, keeping the application itself lightweight

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/kalpakjian/gundam-store.git
   cd gundam-store
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate     # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file (copy from `.env.example`) and fill in the values:
   ```bash
   cp .env.example .env
   ```
   - `SECRET_KEY` — generate one with:
     ```bash
     python -c "import secrets; print(secrets.token_urlsafe(50))"
     ```
   - `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET` — from your
     Cloudinary console (Settings → API Keys). The API key needs **upload (create)** permission.

5. Start the server:
   ```bash
   # Windows helper: applies migrations, seeds the product catalogue, then runs the server
   start.bat

   # Or manually, on any platform
   python manage.py migrate
   python manage.py loaddata_products
   python manage.py runserver
   ```

6. Visit http://127.0.0.1:8000

## Product Data

The repository ships with a fixture holding the full product catalogue
(`store/fixtures/products_data.json`): 46 products, 11 categories and 220
product images. The images live on Cloudinary and are referenced by URL, so no
binary files are stored in the repository.

Seed it with:

```bash
python manage.py loaddata_products          # loads only when the store is empty
python manage.py loaddata_products --force  # wipes store data and reloads
```

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
│   ├── fixtures/          # products_data.json (product catalogue)
│   ├── management/commands/  # loaddata_products, update_image_paths, update_product_scale
│   ├── templates/store/   # Store templates
│   └── templatetags/      # Custom template tags
├── accounts/              # User account app
│   ├── models.py          # UserProfile model
│   ├── views.py           # Login, register, logout views
│   ├── forms.py           # Registration and profile forms
│   ├── context_processors.py  # Injects auth forms into all templates
│   └── templates/accounts/    # Auth modal templates
├── static/                # Bootstrap CSS/JS, banners, icons, images
├── manage.py
├── start.bat              # Windows helper: migrate + seed + run
├── start_server.py        # Smoke-test helper (start, probe, stop)
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
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name | — |
| `CLOUDINARY_API_KEY` | Cloudinary API key (needs upload permission) | — |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret | — |

> `.env` holds credentials and is **not** committed — see `.gitignore`. Use `.env.example` as the template.

## Testing

```bash
python manage.py test
```

The suite covers models, views, the cart, checkout and authentication (37 tests).

## Future Improvements

- Migrate to PostgreSQL for production
- Implement payment gateway integration (Stripe/PayPal)
- Add email verification for registration
- Add rate limiting for login attempts
- Optimize product images with thumbnails
- Add product reviews and ratings
