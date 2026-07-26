from django.contrib import admin

# Register your models here.

from .models import Category, Brand, Product, ProductImage, ProductSpecification


# admin.site.register(Category) 
# admin.site.register(Brand) 
# admin.site.register(Product) 
# admin.site.register(ProductImage) 
# admin.site.register(ProductSpecification) 

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    pass


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        "brand",
        "price",
        "quantity",
        "is_in_stock",
        "created_at",
        "updated_at",
    ]

    search_fields = [
        'name',
        'brand__name',
    ]

    list_filter = [
    "is_in_stock",
    "brand",
    "created_at"
    ]
    
    

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = [
        "product",
        "is_cover",
        "created_at"
    ]    

@admin.register(ProductSpecification)
class ProductSpecificationAdmin(admin.ModelAdmin):
    list_display = [
        "product",
        "key",
        "value"
    ]
    
    

    

    

    
