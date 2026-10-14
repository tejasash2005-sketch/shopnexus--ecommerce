from django import forms
from store.models import Product, Category, Brand

class ProductForm(forms.ModelForm):
    image = forms.ImageField(required=False, help_text="Upload an image for the product")

    class Meta:
        model = Product
        fields = [
            'category', 'brand', 'name', 'description', 'short_description',
            'price', 'discount_price', 'stock', 'sku', 'is_active',
            'is_featured', 'is_bestseller', 'weight', 'dimensions', 'tags'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control rounded-xl'}),
            'short_description': forms.TextInput(attrs={'class': 'form-control rounded-xl'}),
            'name': forms.TextInput(attrs={'class': 'form-control rounded-xl'}),
            'price': forms.NumberInput(attrs={'class': 'form-control rounded-xl'}),
            'discount_price': forms.NumberInput(attrs={'class': 'form-control rounded-xl'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control rounded-xl'}),
            'sku': forms.TextInput(attrs={'class': 'form-control rounded-xl'}),
            'category': forms.Select(attrs={'class': 'form-select rounded-xl'}),
            'brand': forms.Select(attrs={'class': 'form-select rounded-xl'}),
            'tags': forms.TextInput(attrs={'class': 'form-control rounded-xl', 'placeholder': 'e.g. tech, popular, new'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control rounded-xl'}),
            'dimensions': forms.TextInput(attrs={'class': 'form-control rounded-xl', 'placeholder': 'e.g. 10x10x10 cm'}),
        }
