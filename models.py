from django.utils import timezone
from django.contrib import admin
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.hashers import make_password
from django.utils.text import slugify
import hashlib
from django.conf import settings

class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    
    def __str__(self):
        return self.username

class ProductCategory(models.Model):
    name = models.CharField(max_length= 120)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    def __str__(self):
        return self.name
    
    def __str__(self):
        return self.name


class VendorProfile(models.Model):
    ID_TYPE_CHOICES = (
        ('nin', 'Nin'),
        ('drivers_licence', 'Drivers_licence'),
        ('national_identification_card', 'National_identification_card'),
        ('voters_card', 'Voters_card')
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vendor_profile')
    store_name = models.CharField(max_length=250, unique=True, null=True, blank=True)
    store_logo = models.ImageField(upload_to='vendor_logos/', null=True, blank=True)
    store_description = models.TextField(null=True, blank=True)
    phonenumber = models.CharField(max_length=15, null=True, blank=True)
    id_type = models.CharField(max_length=50, choices=ID_TYPE_CHOICES, null=True, blank=True)
    id_number = models.IntegerField( unique=True, null=True, blank=True)
    activated = models.BooleanField(default=False)
    
    def __str__(self):
        return self.store_name
    
    def save(self, *args, **kwargs):
        # return self.store_name
        super().save(*args, **kwargs) 
    

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to='user_profile/', null=True, blank=True)
    last_bought_items = models.TextField(blank=True, null=True)
    last_searched_items = models.TextField(blank=True, null=True)
    favorite_products = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.user.username

    # Add hashing methods or any additional methods here if needed
    def hash_detail(self, detail):
        import hashlib
        return hashlib.sha256(detail.encode('utf-8')).hexdigest()

    def hashed_email(self):
        return self.hash_detail(self.user.email)

    def hashed_username(self):
        return self.hash_detail(self.user.username)

    def hashed_password(self):
        return self.user.password   # Already hashed    
    
class Product(models.Model):
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name='product')    
    product_name = models.CharField(max_length=255)
    product_description = models.TextField(max_length=255)
    product_price = models.DecimalField(editable=True, max_digits=15, decimal_places=2)
    product_image = models.ImageField(upload_to='product_images', null=False, blank=False)
    available_quantity = models.PositiveIntegerField(default=1)
    discount = models.DecimalField(editable=True, max_digits=15, decimal_places=2)
    available = models.BooleanField(default=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name= 'products',null = True)

    def __str__(self):
        return self.product_name
    
class CartItem(models.Model):
    cartitem = models.ForeignKey(ProductCategory, on_delete=models.CASCADE,null = True)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField( default=timezone.now)
    user = models.ForeignKey(User,related_name = 'cart_items',on_delete = models.CASCADE,null=True)
    product = models.ForeignKey(Product,on_delete = models.CASCADE,null=True)
    quantity = models.IntegerField(default = 1)
    ordered = models.BooleanField(default = False)
    delivered = models.BooleanField(default = False)
    def total_price(self):
        return self.product.product_price * self.quantity

    def __str__(self):
        return f"{self.product.product_name} in {self.cartitem.user.username}'s Cart"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    products = models.ManyToManyField(Product, through='OrderProduct')

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.product.name} in Order {self.order.id}"

class Ordering(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    location = models.CharField(max_length=255)  # Add location field
    additional_notes = models.TextField(blank=True, null=True)
    reference_code = models.CharField(max_length=12, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.reference_code} by {self.name}"    
	