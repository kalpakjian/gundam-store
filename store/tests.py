from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from store.models import Category, Product, Cart, CartItem, Order, OrderItem


class ModelTests(TestCase):
    """Test model creation and methods."""

    def setUp(self):
        self.category = Category.objects.create(name="HG", description="High Grade")
        self.product = Product.objects.create(
            name="RX-78-2 Gundam", description="The classic Gundam model",
            price=Decimal("1200.00"), discount_price=Decimal("999.00"),
            stock=10, category=self.category, scale="HG",
        )

    def test_category_str(self):
        self.assertEqual(str(self.category), "HG")

    def test_product_str(self):
        self.assertEqual(str(self.product), "RX-78-2 Gundam")

    def test_product_get_cover_url_no_image(self):
        self.assertIsNone(self.product.get_cover_url())

    def test_product_get_scale_icon(self):
        self.assertEqual(self.product.get_scale_icon(), "/static/scale/hg.webp")

    def test_product_get_scale_icon_no_scale(self):
        self.product.scale = ""
        self.assertIsNone(self.product.get_scale_icon())

    def test_cartitem_get_subtotal_with_discount(self):
        cart = Cart.objects.create()
        item = CartItem.objects.create(cart=cart, product=self.product, quantity=2)
        self.assertEqual(item.get_subtotal(), Decimal("1998.00"))

    def test_cartitem_get_subtotal_without_discount(self):
        self.product.discount_price = None
        self.product.save()
        cart = Cart.objects.create()
        item = CartItem.objects.create(cart=cart, product=self.product, quantity=3)
        self.assertEqual(item.get_subtotal(), Decimal("3600.00"))

    def test_cart_str_with_user(self):
        user = User.objects.create_user(username="testuser", password="testpass123")
        cart = Cart.objects.create(user=user)
        self.assertIn("testuser", str(cart))

    def test_cart_str_with_session(self):
        cart = Cart.objects.create(session_key="abc123")
        self.assertIn("abc123", str(cart))

    def test_order_str(self):
        order = Order.objects.create(shipping_address="123 Test St", total_price=Decimal("500.00"))
        self.assertIn(str(order.id), str(order))


class ViewTests(TestCase):
    """Test view responses."""

    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="RG", description="Real Grade")
        self.product = Product.objects.create(
            name="RG Nu Gundam", price=Decimal("800.00"),
            stock=5, category=self.category, scale="RG",
        )

    def test_home_view(self):
        response = self.client.get(reverse("store:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "store/home.html")

    def test_product_list_view(self):
        response = self.client.get(reverse("store:product_list"))
        self.assertEqual(response.status_code, 200)

    def test_product_detail_view(self):
        response = self.client.get(reverse("store:product_detail", kwargs={"pk": self.product.pk}))
        self.assertEqual(response.status_code, 200)

    def test_product_detail_404(self):
        response = self.client.get(reverse("store:product_detail", kwargs={"pk": 99999}))
        self.assertEqual(response.status_code, 404)

    def test_category_list_view(self):
        response = self.client.get(reverse("store:category_list"))
        self.assertEqual(response.status_code, 200)

    def test_category_detail_view(self):
        response = self.client.get(reverse("store:category_detail", kwargs={"pk": self.category.pk}))
        self.assertEqual(response.status_code, 200)

    def test_search_products_view(self):
        response = self.client.get(reverse("store:search_products"), {"q": "Gundam"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "RG Nu Gundam")

    def test_cart_view_anonymous(self):
        response = self.client.get(reverse("store:cart"))
        self.assertEqual(response.status_code, 200)

    def test_add_to_cart(self):
        response = self.client.post(
            reverse("store:add_to_cart", kwargs={"product_id": self.product.pk}),
            {"quantity": 2},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CartItem.objects.count(), 1)
        self.assertEqual(CartItem.objects.first().quantity, 2)

    def test_add_to_cart_invalid_quantity(self):
        response = self.client.post(
            reverse("store:add_to_cart", kwargs={"product_id": self.product.pk}),
            {"quantity": "abc"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CartItem.objects.count(), 0)

    def test_add_to_cart_exceeds_stock(self):
        response = self.client.post(
            reverse("store:add_to_cart", kwargs={"product_id": self.product.pk}),
            {"quantity": 100},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CartItem.objects.count(), 0)

    def test_add_to_cart_get_not_allowed(self):
        response = self.client.get(reverse("store:add_to_cart", kwargs={"product_id": self.product.pk}))
        self.assertEqual(response.status_code, 302)

    def test_order_history_requires_login(self):
        response = self.client.get(reverse("store:orders"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_profile_requires_login(self):
        response = self.client.get(reverse("store:profile"))
        self.assertEqual(response.status_code, 302)


class CheckoutTests(TestCase):
    """Test the checkout flow end-to-end."""

    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="PG")
        self.product = Product.objects.create(
            name="PG Strike Gundam", price=Decimal("3000.00"),
            stock=3, category=self.category, scale="PG",
        )

    def test_full_checkout_flow(self):
        """Add to cart -> checkout -> order created, stock reduced."""
        # Step 1: Add product to cart
        self.client.post(
            reverse("store:add_to_cart", kwargs={"product_id": self.product.pk}),
            {"quantity": 2},
        )
        self.assertEqual(CartItem.objects.count(), 1)

        # Step 2: Submit checkout
        response = self.client.post(
            reverse("store:checkout"),
            {"shipping_address": "123 Gundam Street, Tokyo"},
        )
        self.assertEqual(response.status_code, 302)

        # Step 3: Verify order was created
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.total_price, Decimal("6000.00"))
        self.assertEqual(order.status, "pending")
        self.assertEqual(OrderItem.objects.count(), 1)

        # Step 4: Verify stock was reduced
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 1)

        # Step 5: Verify cart was cleared
        self.assertEqual(CartItem.objects.count(), 0)
