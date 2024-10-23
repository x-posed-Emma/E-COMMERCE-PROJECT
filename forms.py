from django import forms
from .models import User,VendorProfile,Ordering,Order,UserProfile,Product
import re

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'username', 'password']

class LoginForm(forms.ModelForm):
    class Mete:
        model = User
        fields = ['username', 'password']
        

class VendorProfileForm(forms.ModelForm):
    class Meta:
        model = VendorProfile
        fields = ['store_name', 'store_logo', 'store_description', 'phonenumber', 'id_type', 'id_number', ]
    
        widgets = {
            'store_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter store name', 'required': True}),
            'store_logo': forms.ClearableFileInput(attrs={'class': 'form-control-file', 'required': True}),
            'store_description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter store description'}),
            'phonenumber': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number', 'required': True}),
            'id_type': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'id_number': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter ID number', 'required': True}),
        }

    def clean_store_name(self):
        store_name = self.cleaned_data.get('store_name')
        if not store_name:
            raise forms.ValidationError('Store name is required.')
        if len(store_name) < 3:
            raise forms.ValidationError('Store name must be at least 3 characters long.')
        return store_name

    def clean_store_logo(self):
        store_logo = self.cleaned_data.get('store_logo')
        # You can add validations for the file type, size, etc. if necessary
        return store_logo

    def clean_phonenumber(self):
        phonenumber = self.cleaned_data.get('phonenumber')
        if not re.match(r'^\+?\d{9,15}$', phonenumber):
            raise forms.ValidationError('Phone number must be between 9 and 15 digits, and can start with a "+" for country code.')
        return phonenumber

    def clean_id_number(self):
        id_type = self.cleaned_data.get('id_type')
        id_number = self.cleaned_data.get('id_number')
        
        if not id_number:
            raise forms.ValidationError('ID number is required.')
        
        if id_type == 'nin' and len(str(id_number)) != 11:
            raise forms.ValidationError('NIN must be exactly 11 digits.')
        elif id_type == 'drivers_licence' and len(str(id_number)) != 10:
            raise forms.ValidationError('Driver\'s Licence number must be 10 digits.')
        elif id_type == 'national_identification_card' and len(str(id_number)) != 9:
            raise forms.ValidationError('National Identification Card number must be 9 digits.')
        elif id_type == 'voters_card' and len(str(id_number)) != 8:
            raise forms.ValidationError('Voter\'s Card number must be 8 digits.')

        return id_number

    def clean(self):
        cleaned_data = super().clean()

        store_description = cleaned_data.get('store_description')
        activated = cleaned_data.get('activated')

        if not store_description:
            raise forms.ValidationError('Store description is required.')
        
        # Custom cross-field validation
        if activated and not self.cleaned_data.get('store_name'):
            raise forms.ValidationError('Activated stores must have a store name.')

        return cleaned_data


class OrderingForm(forms.ModelForm):
    class Meta:
        model = Ordering
        fields = ['name', 'email', 'phone', 'address', 'location', 'additional_notes']

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['user', 'total_amount', 'payment_status',  ]


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'product_description', 'product_price', 'product_image', 'available_quantity', 'discount', 'available', 'category']

        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter product name'}),
            'product_description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter product description'}),
            'product_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter price'}),
            'product_image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'available_quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter available quantity'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter discount (in %)'}),
            'available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_price(self):
        price = self.cleaned_data.get('product_price')
        if price <= 0:
            raise forms.ValidationError('Price must be greater than 0.')
        return price

    def clean_available_quantity(self):
        available_quantity = self.cleaned_data.get('available_quantity')
        if available_quantity < 1:
            raise forms.ValidationError('Available quantity must be at least 1.')
        return available_quantity

    # def clean_discount(self):
    #     discount = self.cleaned_data.get('product_discount')
    #     if discount < 0 or discount > 100:
    #         raise forms.ValidationError('Discount must be between 0% and 100%.')
    #     return discount

    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        discount = cleaned_data.get('discount')

        if price and discount and discount >= price:
            raise forms.ValidationError('Discount cannot be greater than or equal to the price.')

        return cleaned_data