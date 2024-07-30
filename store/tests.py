from django.test import TestCase
from .models import Cart, CartItem, Coupons, ProductFilter, RelayPoint, Taille, Categorie, Product, ProductTaille
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.utils import timezone

class TailleModelTest(TestCase):
    def setUp(self):
        self.taille = Taille.objects.create(taille='M')
    
    def test_taille_str(self):
        self.assertEqual(str(self.taille), 'M')

class CategorieModelTest(TestCase):
    def setUp(self):
        self.categorie = Categorie.objects.create(name='Shirts', slug=slugify('Shirts'), genre='homme')
    
    def test_categorie_str(self):
        self.assertEqual(str(self.categorie), 'Shirts')
    
    def test_slug_generation(self):
        self.assertEqual(self.categorie.slug, 'shirts')

class ProductModelTest(TestCase):
    def setUp(self):
        self.categorie = Categorie.objects.create(name='Shirts', slug=slugify('Shirts'), genre='homme')
        self.product = Product.objects.create(
            name='T-shirt',
            slug=slugify('T-shirt'),
            price=10.0,
            short_description='A nice t-shirt',
            long_description='A very nice t-shirt',
            matiere='Cotton',
            couleur='Blue',
            categorie=self.categorie,
            genre='homme'
        )
    
    def test_product_str(self):
        self.assertEqual(str(self.product), 'T-shirt')
    
    def test_product_price(self):
        self.assertEqual(self.product.price, 10.0)

class ProductTailleModelTest(TestCase):
    def setUp(self):
        self.taille = Taille.objects.create(taille='M')
        self.categorie = Categorie.objects.create(name='Shirts', slug=slugify('Shirts'), genre='homme')
        self.product = Product.objects.create(
            name='T-shirt',
            slug=slugify('T-shirt'),
            price=10.0,
            short_description='A nice t-shirt',
            long_description='A very nice t-shirt',
            matiere='Cotton',
            couleur='Blue',
            categorie=self.categorie,
            genre='homme'
        )
        self.product_taille = ProductTaille.objects.create(product=self.product, taille=self.taille, stock=100)
    
    def test_product_taille_str(self):
        self.assertEqual(str(self.product_taille), 'T-shirt - M')
    
    def test_product_taille_stock(self):
        self.assertEqual(self.product_taille.stock, 100)
        
class CouponsModelTest(TestCase):
    def setUp(self):
        self.coupon = Coupons.objects.create(
            code="SAVE10",
            discount=10,
            is_active=True,
            expires_at=timezone.now() + timezone.timedelta(days=1)
        )

    def test_coupon_str(self):
        self.assertEqual(str(self.coupon), "SAVE10")

    def test_coupon_is_active(self):
        self.assertTrue(self.coupon.is_active)
        
class CartItemModelTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(email='testuser@example.com', password='12345')
        self.category = Categorie.objects.create(name="Shirts", slug="shirts")
        self.taille = Taille.objects.create(taille="M")
        self.product = Product.objects.create(
            name="Test Product",
            price=100.0,
            matiere="Cotton",
            couleur="Blue",
            categorie=self.category
        )
        self.product_taille = ProductTaille.objects.create(product=self.product, taille=self.taille, stock=10)
        self.cart_item = CartItem.objects.create(
            user=self.user,
            product=self.product,
            product_taille=self.product_taille,
            quantity=2
        )

    def test_cart_item_str(self):
        self.assertEqual(str(self.cart_item), "Test Product (2)")

    def test_cart_item_subtotal(self):
        self.cart_item.calc_subtotal()
        self.assertEqual(self.cart_item.subtotal, 200.0)

class CartModelTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(email='testuser@example.com', password='12345')
        self.cart = Cart.objects.create(user=self.user)
        self.coupon = Coupons.objects.create(code="SAVE10", discount=10)
        self.cart.coupons.add(self.coupon)

    def test_cart_calculate_totals(self):
        self.cart.calc_totaux()
        self.assertEqual(self.cart.totaux, 0.0)
        self.assertEqual(self.cart.all_quantity, 0)

    def test_cart_str(self):
        self.assertEqual(str(self.cart), f"Cart of {self.user.email}")

class RelayPointModelTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(email='testuser@example.com', password='12345')
        self.relay_point = RelayPoint.objects.create(
            name="Main Relay Point",
            address="123 Main St",
            postcode="12345",
            city="Test City",
            country="FR",
            user=self.user
        )

    def test_relay_point_str(self):
        self.assertEqual(str(self.relay_point), "Main Relay Point, 123 Main St, Test City, 12345, FR")
        
class ProductFilterTest(TestCase):
    def setUp(self):
        self.category = Categorie.objects.create(name="Shirts", slug="shirts")
        self.product1 = Product.objects.create(name="Shirt 1", categorie=self.category)
        self.product2 = Product.objects.create(name="Shirt 2", categorie=self.category)

    def test_product_filter_by_category(self):
        filter = ProductFilter(data={'category': self.category.id})
        self.assertEqual(filter.qs.count(), 2)
