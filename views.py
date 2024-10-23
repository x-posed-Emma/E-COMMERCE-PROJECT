from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect, reverse
from decouple import config
from project.settings import PAYSTACK_SECRET_KEY
from .forms import RegistrationForm,VendorProfileForm,OrderForm,OrderingForm ,ProductForm
from django.contrib.auth import authenticate, login , logout
from django.contrib import messages
from .models import User, Product, CartItem,Order,ProductCategory, Ordering, OrderProduct,UserProfile,VendorProfile
from django.views.generic import ListView,TemplateView ,DetailView, View
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
import requests
import json 
from django.http import HttpResponseForbidden
from django.utils.decorators import method_decorator
from django.shortcuts import HttpResponse
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

def Regform(request) :
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            if (username == '' or password == '' or email == ''):
                messages.error(request, "Please input all fields")
        else:
            user = User.objects.create_user(username=username, password= password, email=email)
            user.save()
            messages.success(request, 'Account Creation Successful') 
            login(request, user) 
            return redirect('/')

    return render(request, 'forms/Registrationform.html')        
  
def Loginform(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, "Username or Password Error")
    return render(request, 'forms/loginform.html') 
      
@method_decorator(login_required, name='dispatch')
class Home(TemplateView):
    template_name = 'app1/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        mainQs = Product.objects.all()
        params = self.request.GET
        if params.get("category"):
            mainQs = mainQs.filter(category__name=params.get("category"))
        
        categories = ProductCategory.objects.all()
        context['categories'] = categories
        context['products'] = mainQs
        
        user = self.request.user
        context['user'] = user
        
        try:
            profile = UserProfile.objects.get(user=user)
            context['username'] = user.username
            context['email'] = user.email
            context['last_bought_items'] = profile.last_bought_items
            context['last_searched_items'] = profile.last_searched_items
            context['favorite_products'] = profile.favorite_products
        except UserProfile.DoesNotExist:
            context['username'] = 'Not Found'
            context['email'] = 'Not Found'
            context['last_bought_items'] = 'Not Found'
            context['last_searched_items'] = 'Not Found'
            context['favorite_products'] = 'Not Found'
            context['error'] = 'UserProfile not found'

        return context
    

@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            vendor_profile = request.user.vendor_profile
            product.vendor = vendor_profile  
            product.save()
            return redirect('app1:dashboard')  
    else:
        form = ProductForm()

    return render(request, 'app1/addproduct.html', {'form': form})


def detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    context = {
        'product': product,
    }
    return render(request, 'app1/detail.html', context)  
    
def logout_view(request):
    logout(request)
    return redirect('app1/login')  

@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)

    cart_items = CartItem.objects.filter(user=request.user, ordered=False)
    
    overall_total = sum(item.total_price() for item in cart_items)

    def get_context_data(self,):
        mainQs = Product.objects.all()
        params = self.request.GET
        if params.get("category"):
            mainQs = mainQs.filter(category__name = params.get("category"))
        context = super().get_context_data()
        categories = ProductCategory.objects.all()
        context['categories'] = categories
        context['products'] = mainQs
        context['user'] =  self.request.user
        return context

    context = {
        'cart_items': cart_items,
        'overall_total': overall_total,
    }
    return render(request, 'app1/cart.html', context)


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
        ordered=False
    )
    if created:
        messages.success(request, f"{product.product_name} added to your cart.")
    else:    
        cart_item.quantity += 1
        cart_item.save()
        messages.info(request, f"Quantity updated for {product.product_name}.")
    
    return redirect('/')


import logging

logger = logging.getLogger(__name__)

def vendor_profile_view(request):
    if hasattr(request.user, 'vendorprofile'):
        return redirect('app1:dashboard') 

    if request.method == 'POST':
        form = VendorProfileForm(request.POST, request.FILES)
        if form.is_valid():
            vendor_profile = form.save(commit=False)
            vendor_profile.user = request.user  
            vendor_profile.activated = True 
            vendor_profile.save()
            
            messages.success(request, 'Vendor profile created successfully! Waiting for admin activation.')
            return redirect('app1:update')  
        else:
            messages.error(request, 'There was an error in the form. Please correct it and try again.')
            logger.error(form.errors)  
    else:
        form = VendorProfileForm()

    return render(request, 'forms/vendorprofile.html', {'form': form})


def vendor_dashboard(request):
    vendor_profile = request.user.vendor_profile
    products = Product.objects.filter(vendor=vendor_profile) 
    
    return render(request, 'app1/dashboard.html', {'products': products})


@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    product_name = cart_item.product.product_name
    cart_item.delete()

    messages.success(request, f"{product_name} removed from your cart.")

    return redirect('/cart')  

@login_required
def create_order(request):
    user = request.user
    cart_items = CartItem.objects.filter(user=user)
    total_amount = sum(item.product.product_price * item.quantity for item in cart_items)

    if request.method == 'POST':
        order = Order.objects.create(user=user, total_amount=total_amount)

        headers = {
            "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        data = {
            "email": user.email,
            "amount": int(total_amount * 100), 
            "reference": f"ORDER-{order.id}",
            "callback_url": request.build_absolute_uri(reverse('app1:payment_callback'))
        }
        response = requests.post("https://api.paystack.co/transaction/initialize", json=data, headers=headers)
        response_data = response.json()

        if response_data["status"]:
            payment_url = response_data["data"]["authorization_url"]
            return redirect(payment_url)
        else:
            return render(request, 'app1/cart.html', {'error': 'Payment initiation failed', 'cart_items': cart_items, 'total_amount': total_amount})

    context = {
        'cart_items': cart_items,
        'total_amount': total_amount
    }
    return render(request, 'app1/cart.html', context)


def payment_callback(request):
    reference = request.GET.get('reference')
    
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
    }
    
    response = requests.get(f"https://api.paystack.co/transaction/verify/{reference}", headers=headers)
    response_data = response.json()

    print("Response Data from Paystack:", response_data)

    if response_data["status"] and "data" in response_data:
        data = response_data["data"]
    
        if data["status"] == "success":
            metadata_str = data.get("metadata", "")  
            try:
                metadata = json.loads(metadata_str)  
                order_id = metadata.get("order_id")  
            except json.JSONDecodeError:
                print("Error decoding metadata JSON.")  
                return redirect('/order_failed')

            if order_id:
                order = Order.objects.get(id=order_id)
                order.payment_status = "Completed"
                order.save()
                return redirect('order_success')
            else:
                print("Order ID not found in metadata.")  
                return redirect('app1/order_failed')
        else:
            print("Payment verification failed with status:", data["status"])  
    else:
        print("Invalid response or transaction verification failed.") 
    
    return redirect('app1/order_failed')

def order_failed(request):
    return render(request, 'app1/order_failed.html', {
        'message': 'Your payment is successful and is now pending confirmations. You would receive a notification when the payment is confirmed'
    })

def category_view(request,):
    categories = ProductCategory.objects.all()

    return {'categories': categories,}


import random
import string

def generate_order_reference():
    """Generates a 12-character alphanumeric reference code with symbols."""
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    
    reference_code = ''.join(random.choice(chars) for _ in range(12))
    
    return reference_code    


@login_required
def order_profile(request):
    orders = Order.objects.filter(user=request.user)

    order_data = []
    for order in orders:
        order_products = OrderProduct.objects.filter(order=order)
        
        products = [
            {
                'name': op.product.name,
                'quantity': op.quantity,
                'price': op.product.price,
                'total': op.quantity * op.product.price
            }
            for op in order_products
        ]

        # Append the order and its products to the list
        order_data.append({
            'id': order.id,
            'total_amount': order.total_amount,
            'payment_status': order.payment_status,
            'created_at': order.created_at,
            'products': products  # Include the products list
        })

    return render(request, 'app1/orderprofile.html', {'orders': order_data})

@login_required
def order_view(request):
    if request.method == 'POST':
        form = OrderingForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            address = form.cleaned_data['address']
            location = form.cleaned_data['location']
            additional_notes = form.cleaned_data.get('additional_notes', '')

            order_reference = generate_order_reference()

            ordering_instance = Ordering.objects.create(
                name=name,
                email=email,
                phone=phone,
                address=address,
                location=location,  
                additional_notes=additional_notes,
                reference_code=order_reference
            )

            request.session['order_reference'] = order_reference

            return redirect('app1:create_order') 

        else:
            return render(request, 'forms/ordering.html', {'form': form})
     

def search(request):
    query = Q(product_name__contains = request.GET.get("params")) | Q(product_name__icontains = request.GET.get("params"))
    queryset = Product.objects.filter(query).all()
    context = {}
    params = request.GET
    if params.get("category"):
        mainQs = mainQs.filter(category__name = params.get("category"))
    categories = ProductCategory.objects.all()
    context['categories'] = categories
    context['products'] = queryset
    context['user'] =  request.user
    return render(request,"app1/home.html",context)



@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()  

@login_required
def user_profile_view(request):
    user = request.user  
    try:
        profile = UserProfile.objects.get(user=user)
        context = {
            'username': user.username,  
            'email': user.email,        
            'password': user.password,  
            'last_bought_items': profile.last_bought_items,
            'last_searched_items': profile.last_searched_items,
            'favorite_products': profile.favorite_products
        }
    except UserProfile.DoesNotExist:
        context = {'error': 'UserProfile not found'}

    return render(request, 'app1/userprofile.html', context) 

def update(request):
    """
    View function to display a message when an order fails.
    """
    return render(request, 'app1/update.html')


def user_is_vendor(user):
    """Check if the user is a vendor."""
    return hasattr(user, 'vendor_profile') 

@login_required
def some_view(request):
    is_vendor = user_is_vendor(request.user)

    return render(request, 'some_template.html', {
        'is_vendor': is_vendor
    })

