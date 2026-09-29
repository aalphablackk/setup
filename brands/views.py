from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import BrandForm
from .models import Brand

# Create your views here.

@login_required
def brand_list(request):
    brands = Brand.objects.filter(
        created_by=request.user,
        is_active=True,
    )

    return render(
        request,
        "brands/brand_list.html",
        {
            "brands": brands,
        },
    )


@login_required
def brand_create(request):

    if request.method == "POST":
        form = BrandForm(request.POST)

        if form.is_valid():
            brand = form.save(commit=False)
            brand.created_by = request.user
            brand.save()

            return redirect(
                "brands:detail",
                pk=brand.pk,
            )

    else:
        form = BrandForm()

    return render(
        request,
        "brands/brand_form.html",
        {
            "form": form,
            "page_title": "Create your brand",
        },
    )


@login_required
def brand_detail(request, pk):

    brand = get_object_or_404(
        Brand,
        pk=pk,
        created_by=request.user,
    )

    return render(
        request,
        "brands/brand_detail.html",
        {
            "brand": brand,
        },
    )


@login_required
def brand_update(request, pk):

    brand = get_object_or_404(
        Brand,
        pk=pk,
        created_by=request.user,
    )

    if request.method == "POST":
        form = BrandForm(
            request.POST,
            instance=brand,
        )

        if form.is_valid():
            form.save()

            return redirect(
                "brands:detail",
                pk=brand.pk,
            )

    else:
        form = BrandForm(instance=brand)

    return render(
        request,
        "brands/brand_form.html",
        {
            "form": form,
            "brand": brand,
            "page_title": "Update your brand",
        },
    )