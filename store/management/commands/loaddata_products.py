"""Management command: seed the database with the bundled Gundam product fixture.

Usage:
    python manage.py loaddata_products            # load only if database is empty
    python manage.py loaddata_products --force    # wipe store data and reload
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import transaction

from store.models import Product, ProductImage, Category

FIXTURE = 'products_data'


class Command(BaseCommand):
    help = 'Load products_data.json fixture to populate the store with Gundam products.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Delete existing store data before loading the fixture.',
        )

    def handle(self, *args, **options):
        force = options['force']
        existing = Product.objects.count()

        if existing and not force:
            self.stdout.write(self.style.WARNING(
                f'Database already has {existing} products - skipping load. '
                f'Use --force to reload.'
            ))
            return

        with transaction.atomic():
            if force:
                self.stdout.write('Removing existing store data...')
                ProductImage.objects.all().delete()
                Product.objects.all().delete()
                Category.objects.all().delete()

            self.stdout.write('Loading fixture "{}"...'.format(FIXTURE))
            call_command('loaddata', FIXTURE, verbosity=1)

        products = Product.objects.count()
        images = ProductImage.objects.count()
        categories = Category.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f'Loaded {products} products, {images} product images, '
            f'and {categories} categories.'
        ))