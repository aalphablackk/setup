from django import forms
from .models import Product, Category, Brand, ProductImage, ProductSpecification


class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = [
            "name"
        ]


class BrandForm(forms.ModelForm):

    class Meta:
        model = Brand
        fields = [
            "name",
            "category"
        ]


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = [
            "name",
            "brand",
            "description",
            "price",
            "is_in_stock",
            "quantity",
        ]

class ProductImageForm(forms.ModelForm):

    class Meta:

        model = ProductImage

        fields = [
            "image",
            "is_cover"
        ]

class ProductSpecificationForm(forms.ModelForm):

    class Meta:

        model = ProductSpecification

        fields = [
            "key",
            "value",
        ]