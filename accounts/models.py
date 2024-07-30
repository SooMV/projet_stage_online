from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
import requests
from django_countries.fields import CountryField
import stripe
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def create_user(self,email, password, **Kwargs):
        if not email :
           raise ValueError("L'addresse email est obligatoire.")
        
        # convertit la partie du domaine en minuscule / élimine les espaces .
        email = self.normalize_email(email)
        
        # permet la création d'une nouvelle instance
        user = self.model(email = email, **Kwargs)
        
        # fournissant un algorithme de hashage de mot de passe 
        user.set_password(password)
        
        # sauvegarde la nouvelle instance de l'utilisateur crée
        user.save()
        
        return user
    
    def create_superuser(self, email, password, **Kwargs):
        Kwargs['is_staff'] = True
        Kwargs['is_superuser'] = True
        Kwargs['is_active'] = True
        
        return self.create_user(email = email, password = password, **Kwargs)

ADDRESSE_FORMAT = """ 

{name}
{phone_number}
{address_1}
{address_2}
{city} , {zip_code}
{country}

"""
    
class Customer(AbstractUser):
    username = models.CharField(max_length=90, blank = True, null =True) 
    email = models.EmailField(max_length=240, unique = True, verbose_name=_("User_Email"))
    stripe_id = models.CharField(max_length=90, blank = True,)
    
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [] 
    
    objects = CustomUserManager()
    
    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name = _("Customer")
        verbose_name_plural = _("Customers")
    

class ShippingAddress(models.Model):
    # Typage des variables afin de spécifier quel sera la valeur du user
    user = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name="addresses", verbose_name=_("User"))  
    name = models.CharField(max_length=255, choices=[("Domicile", "Domicile"), ('Travail', "Travail"), ('Vide', "---------")], default="", null=True, blank=True)
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    address_1 = models.CharField(max_length=1024, help_text=_("Street address and number"), verbose_name=_("Address 1"))
    city = models.CharField(max_length=1024, verbose_name=_("City"))
    zip_code = models.CharField(max_length=32,verbose_name=_("Zip Code"))
    phone_number = models.CharField(max_length=12, blank=True, null=True, verbose_name=_("Phone Number") )
    country = CountryField(blank_label='(choisissez un pays)')
    default = models.BooleanField(default=False, verbose_name=_("Default Address"))
    
    class Meta:
        verbose_name = _("Shipping Address")
        verbose_name_plural = _("Shipping Addresses")
        
    def __str__(self):
        data = self.__dict__.copy()
        data.update(country = self.get_country_display())
        return ADDRESSE_FORMAT.format(**data)

    def as_dict(self):
        return {
            "city" : self.city,
            "country" : self.country,
            "line1" : self.address_1,
            
            "postal_code" : self.zip_code,
            "phone_number": self.phone_number
        }
        
    def set_default(self):
        if not self.user.stripe_id:
            raise ValueError(f"L'utilisateur {self.user.email} n'a pas de stripe ID")
        self.user.addresses.update(default = False)
        self.default = True
        self.save()
        
        stripe.Customer.modify(
            self.user.stripe_id,
            shipping ={
                "name" : self.name,
                "address": self.as_dict()
            },
            address=self.as_dict()
        )
    def __str__(self):
        return f"{self.name}, {self.first_name}, {self.last_name},{self.address_1}, {self.city}, {self.zip_code}, {self.country}"

