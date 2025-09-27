from django import forms
from django.core.validators import RegexValidator
from .models import Business, Product

class BusinessForm(forms.ModelForm):
    class Meta:
        model = Business
        fields = ['name', 'description', 'whatsapp_number', 'city', 'native_place', 'public']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Enter your business name'
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Describe your business, products, or services...'
            }),
            'whatsapp_number': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'placeholder': '+919876543210'
            }),
            'city': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Your city'
            }),
            'native_place': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Your native place'
            }),
            'public': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['whatsapp_number'].required = True
        self.fields['description'].required = False
        self.fields['city'].required = False
        self.fields['native_place'].required = False
        
        # Add WhatsApp number validation
        self.fields['whatsapp_number'].validators = [
            RegexValidator(
                regex=r'^\+?[1-9]\d{1,14}$',
                message='Enter a valid WhatsApp number with country code (e.g., +919876543210)'
            )
        ]
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip()
            if len(name) < 2:
                raise forms.ValidationError('Business name must be at least 2 characters long.')
        return name
    
    def clean_whatsapp_number(self):
        number = self.cleaned_data.get('whatsapp_number')
        if number:
            # Remove spaces and ensure it starts with +
            number = number.replace(' ', '').replace('-', '')
            if not number.startswith('+'):
                number = '+' + number
        return number


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'description', 'image', 'sku', 'active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Enter product name'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Describe your product, its features, specifications...'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'accept': 'image/*'
            }),
            'sku': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Product code or SKU'
            }),
            'active': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['price'].required = False
        self.fields['description'].required = False
        self.fields['image'].required = False
        self.fields['sku'].required = False
        self.fields['active'].initial = True
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip()
            if len(name) < 2:
                raise forms.ValidationError('Product name must be at least 2 characters long.')
        return name
    
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise forms.ValidationError('Price cannot be negative.')
        return price
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Check file size (limit to 5MB)
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Image file too large. Maximum size is 5MB.')
            
            # Check if it's actually an image
            if not image.content_type.startswith('image/'):
                raise forms.ValidationError('Please upload a valid image file.')
        
        return image