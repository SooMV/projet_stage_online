from decimal import Decimal
from django.utils import timezone
from django.db import models
from django.utils.text import slugify
from django.views.generic.detail import DetailView
from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import Customer
from django_countries import Countries
from shop.settings import AUTH_USER_MODEL
import django_filters
from iso3166 import countries
from django.conf import settings

# Create your models here.
"""
Produit
-nom
-slug 
-prix
-qtité en stock
-description
-image

"""


class Taille(models.Model):
    taille = models.CharField(max_length=10, blank=True, verbose_name=_("Size"))
    
    def __str__(self) -> str:
        return self.taille
     
    class Meta:
        ordering = ['taille']
        verbose_name = _("Size")
        verbose_name_plural = _("Sizes")
         
class Categorie(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    genre = models.CharField(max_length=128, choices=[('homme', "HOMME"), ('femme', "FEMME"),('vide', ' ')], default="", null=True, blank= True)
   
    def __str__(self):
        return self.nom
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

class Product(models.Model):
    name = models.CharField(max_length=128, verbose_name=_("Name"))
    slug = models.SlugField(max_length=128, blank=True, null=True, verbose_name=_("Slug"))
    price = models.FloatField(default=0.0, verbose_name=_("Price"))
    short_description = models.TextField(blank=True, verbose_name=_("Short Description"))
    long_description = models.TextField(blank=True, verbose_name=_("Long Description"))
    matiere = models.CharField(max_length=128, verbose_name=_("Material"))
    couleur = models.CharField(max_length=128, verbose_name=_("Color"))
    thumbnails1 = models.ImageField(upload_to="products", blank=True, null=True, verbose_name=_("Thumbnail 1"))
    thumbnails2 = models.ImageField(upload_to="products", blank=True, null=True, verbose_name=_("Thumbnail 2"))
    thumbnails3 = models.ImageField(upload_to="products", blank=True, null=True, verbose_name=_("Thumbnail 3"))
    thumbnails4 = models.ImageField(upload_to="products", blank=True, null=True, verbose_name=_("Thumbnail 4"))
    updated_at = models.DateTimeField(blank=True, null=True, verbose_name=_("Updated At"))
    promo = models.BooleanField(default=False, verbose_name=_("Promo"))
    percent_promo = models.IntegerField(default=0, verbose_name=_("Promo Percentage"))
    price_promo = models.FloatField(default=0.0, verbose_name=_("Promo Price"))
    product_stripe_id = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Stripe ID"))
    
    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name=_("Category")
    )
    genre = models.CharField(max_length=128, choices=[('homme', "HOMME"), ('femme', "FEMME"),('vide', ' ')], default="")
    
    tailles = models.ManyToManyField(
        Taille,
        related_name='products',
        through='ProductTaille',
        verbose_name=_("Sizes")
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

class ProductTaille(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_("Product"))
    taille = models.ForeignKey(Taille, on_delete=models.CASCADE, verbose_name=_("Size"))
    stock = models.IntegerField(default=0, verbose_name=_("Stock"))

    def __str__(self):
        return f"{self.product.name} - {self.taille.taille}"
    
    class Meta:
        verbose_name = _("Product Size")
        verbose_name_plural = _("Product Sizes")
        
class ProductFilter(django_filters.FilterSet):
    category = django_filters.ModelChoiceFilter(queryset=Categorie.objects.all(), empty_label="All", field_name='categorie')
    genre = django_filters.ChoiceFilter(choices=[('homme', "HOMME"), ('femme', "FEMME")], empty_label="All")

    class Meta:
        model = Product
        fields = ['category', 'genre']   
        
class Coupons(models.Model):
    code = models.CharField(max_length=10, blank=True, null=True, verbose_name=_("Code"))
    discount = models.IntegerField(default=0, blank=True, null=True, verbose_name=_("Discount"))
    is_active = models.BooleanField(default=True, blank=True, null=True, verbose_name=_("Is Active"))
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_("Created At"))
    expires_at = models.DateTimeField(blank=True, null=True, verbose_name=_("Expires At"))
    
    def __str__(self):
        return self.code

    class Meta:
        verbose_name = _("Coupon")
        verbose_name_plural = _("Coupons")

# représente un élément individuel dans le panier 
class CartItem(models.Model):
    # on attribue l'article à un utilisateur 
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("User"))
    # on spécifie l'article 
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, verbose_name=_("Product"))
    product_taille = models.ForeignKey(ProductTaille, on_delete=models.CASCADE, null=True, verbose_name=_("Product Size"))
    quantity = models.IntegerField(default=1, verbose_name=_("Quantity"))
    # on indique si cet article a été commandé 
    # donc par défaut non 
    ordered = models.BooleanField(default=False, verbose_name=_("Ordered"))
    # date d'ajout 
    ordered_date = models.DateTimeField(blank=True, null=True, verbose_name=_("Ordered Date"))
    subtotal = models.FloatField(default=0.0, verbose_name=_("Subtotal"))

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    class Meta:
        verbose_name = _("Cart Item")
        verbose_name_plural = _("Cart Items")

    
    def __str__(self) -> str:
      return f"{self.product.name} ({self.quantity})"
   
    def calc_subtotal(self):
        if self.product.promo:
            self.subtotal = self.product.price_promo * self.quantity
        else:
            self.subtotal = self.product.price * self.quantity
        self.save()


class Cart(models.Model):
    # on attribue un panier à un utilisateur, si le user est supprimé, le panier l'est également
    user = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("User"))
    # un panier peut contenir plusieurs articles
    # un article peut être dans plusieurs paniers
    orders = models.ManyToManyField(CartItem, verbose_name=_("Orders"))
    ordered = models.BooleanField(default=False, verbose_name=_("Ordered"))
    ordered_date = models.DateTimeField(blank=True, null=True, verbose_name=_("Ordered Date"))
    # total du panier
    totaux = models.FloatField(default=0.0, verbose_name=_("Total"))
    # quantité totale d'articles dans le panier
    all_quantity = models.IntegerField(default=0, verbose_name=_("Total Quantity"))
    coupons = models.ManyToManyField(Coupons, blank=True, verbose_name=_("Coupons"))
    

    def calc_totaux(self):
        cart = []
        self.totaux = 0
        self.all_quantity = 0
        
    #    ici on vérifie si un produit est en promotion
    # cart.append : push dans le tableau
    # si oui on applique le prix promo
    # si non on applique le tarif de base 
        for order in self.orders.all():
            if order.product.promo :
                cart.append([order, order.product.price_promo * order.quantity, order.quantity])
            else :
                cart.append([order, order.product.price * order.quantity, order.quantity])
              
        # après le push, on met a jour le total du panier 
        # et quantité  au panier 
        for item in cart :
         self.totaux += item[1]
         self.all_quantity += item[2]
         
    # convertit le tableau en un objet décimale, pour arrondir le total à 2 décimales 
    # Sauvegarde et persist le panier en bdd 
        self.totaux = Decimal(self.totaux).quantize(Decimal("0.00"))
        
        if self.coupons.exists():
          for coupon in self.coupons.all():
              discount_amount = self.totaux * (Decimal(coupon.discount) / Decimal(100))
              self.totaux -= discount_amount.quantize(Decimal("0.00"))
              
        self.save()
    
     
    def delete_order(self, name):
       for order in self.orders.all():
        if order.product.name == name :
            if order.quantity >= 1:
                order.quantity -= 1
                order.calc_subtotal()
                order.save()
                if order.quantity == 0:
                    order.delete()
        
    def delete(self, *arg, **kwargs):
        # Boucle sur toutes les commandes associé au panier
        for order in self.orders.all():
            # on indique que cette article a été commandé 
            order.ordered = True 
            # enregistre la date et l'heure de la commande 
            order.ordered_date = timezone.now()
            # Supprimer la commande
            order.save()
            # Ici on appelle la classe model.Model 
            # qui possède une fonction interne appelé delete()
        super().delete(*arg, **kwargs)
        
    def count_orders(self):
        return self.orders.count()
    
    def calculate_total_quantity(self):
        total_quantity = 0
        for order in self.orders.all():
            total_quantity += order.quantity
        self.all_quantity = total_quantity
        self.save()
        
    
    def __str__(self):
        return f"Cart of {self.user.email}"
    
    class Meta:
        verbose_name = _("Cart")
        verbose_name_plural = _("Carts")
        
        


class RelayPoint(models.Model):
    name = models.CharField(max_length=255,null=True , blank=True)
    address = models.CharField(max_length=255, null=True , blank=True)
    postcode = models.CharField(max_length=20, null=True , blank=True)
    city = models.CharField(max_length=255, null=True , blank=True)
    country = models.CharField(max_length=2, choices=[(c.alpha2.lower(), c.name) for c in countries], null=True , blank=True)
    user = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="relay_points", verbose_name=_("User"), null=True, blank=True)

    class Meta:
        verbose_name = _("Relay Point")
        verbose_name_plural = _("Relay Points")

    def __str__(self):
        return f"{self.name}, {self.address}, {self.city}, {self.postcode}, {self.country}"
    
    
    