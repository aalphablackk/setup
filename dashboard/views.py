from django.shortcuts import render, redirect, get_object_or_404

from products.models import (
    Product,
    Category,
    ProductImage,
    ProductSpecification
)

from products.forms import (
    ProductForm,
    CategoryForm,
    BrandForm,
    ProductImageForm,
    ProductSpecificationForm
)


# Dashboard Home

def dashboard_home(request):

    total_products = Product.objects.count()
    total_categories = Category.objects.count()


    return render(
        request,
        'dashboard/index.html',
        {
            'total_products': total_products,
            'total_categories': total_categories,
        }
    )



# Product List

def product_list(request):

    products = Product.objects.prefetch_related(
        'images',
        'specifications'
    ).select_related(
        'brand'
    ).order_by(
        '-created_at'
    )


    return render(
        request,
        'dashboard/product_list.html',
        {
            'products': products
        }
    )



# Add Product + Brand + Category

def product_add(request):

    product_form = ProductForm()
    brand_form = BrandForm()
    category_form = CategoryForm()



    if request.method == "POST":


        form_type = request.POST.get("form_type")



        # PRODUCT FORM

        if form_type == "product":


            product_form = ProductForm(
                request.POST
            )


            if product_form.is_valid():


                product = product_form.save()



                return redirect(
                    "product_images",
                    product_id=product.id
                )




        # BRAND FORM

        elif form_type == "brand":


            brand_form = BrandForm(
                request.POST
            )


            if brand_form.is_valid():

                brand_form.save()


                return redirect(
                    "product_add"
                )




        # CATEGORY FORM

        elif form_type == "category":


            category_form = CategoryForm(
                request.POST
            )


            if category_form.is_valid():

                category_form.save()


                return redirect(
                    "product_add"
                )




    return render(
        request,
        "dashboard/product_add.html",
        {
            "product_form": product_form,
            "brand_form": brand_form,
            "category_form": category_form,
        }
    )





# Product Images


def product_images(request, product_id):


    product = get_object_or_404(
        Product.objects.prefetch_related("images"),
        id=product_id
    )



    if request.method == "POST":


        form = ProductImageForm(
            request.POST,
            request.FILES
        )



        if form.is_valid():


            image = form.save(
                commit=False
            )


            image.product = product


            image.save()



            return redirect(
                "product_images",
                product_id=product.id
            )



    else:

        form = ProductImageForm()



    return render(
        request,
        "dashboard/product_images.html",
        {
            "form": form,
            "product": product,
            "images": product.images.all()
        }
    )





# Product Specifications


def product_specifications(request, product_id):


    product = get_object_or_404(
        Product,
        id=product_id
    )



    if request.method == "POST":


        form = ProductSpecificationForm(
            request.POST
        )



        if form.is_valid():


            specification = form.save(
                commit=False
            )


            specification.product = product


            specification.save()



            return redirect(
                "product_specifications",
                product_id=product.id
            )



    else:

        form = ProductSpecificationForm()




    return render(
        request,
        "dashboard/product_specifications.html",
        {
            "form": form,
            "product": product,
            "specifications": product.specifications.all()
        }
    )





# Edit Product


def product_edit(request, product_id):


    product = get_object_or_404(
        Product,
        id=product_id
    )



    if request.method == "POST":


        form = ProductForm(
            request.POST,
            instance=product
        )



        if form.is_valid():

            form.save()


            return redirect(
                "product_list"
            )



    else:


        form = ProductForm(
            instance=product
        )




    return render(
        request,
        "dashboard/product_edit.html",
        {
            "form": form,
            "product": product
        }
    )





# Delete Product


def product_delete(request, product_id):


    if request.method == "POST":


        product = get_object_or_404(
            Product,
            id=product_id
        )


        product.delete()



    return redirect(
        "product_list"
    )





# Delete Product Image


def delete_product_image(request, image_id):


    if request.method == "POST":


        image = get_object_or_404(
            ProductImage,
            id=image_id
        )


        product_id = image.product.id


        image.delete()



        return redirect(
            "product_images",
            product_id=product_id
        )



    return redirect(
        "product_list"
    )





# Set Cover Image


def set_cover_image(request, image_id):


    if request.method == "POST":


        image = get_object_or_404(
            ProductImage,
            id=image_id
        )


        product = image.product



        # Remove existing cover

        ProductImage.objects.filter(
            product=product
        ).update(
            is_cover=False
        )



        # Set selected image as cover

        image.is_cover = True

        image.save()



        return redirect(
            "product_images",
            product_id=product.id
        )



    return redirect(
        "product_list"
    )





# Delete Specification


def delete_specification(request, specification_id):


    if request.method == "POST":


        specification = get_object_or_404(
            ProductSpecification,
            id=specification_id
        )


        product_id = specification.product.id


        specification.delete()



        return redirect(
            "product_specifications",
            product_id=product_id
        )



    return redirect(
        "product_list"
    )





# Edit Specification


def edit_specification(request, specification_id):

    specification = get_object_or_404(
        ProductSpecification,
        id=specification_id
    )


    if request.method == "POST":

        form = ProductSpecificationForm(
            request.POST,
            instance=specification
        )


        if form.is_valid():

            form.save()



    return redirect(
        "product_specifications",
        product_id=specification.product.id
    )