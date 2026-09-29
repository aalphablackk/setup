from django import forms

from .models import Brand


class BrandForm(forms.ModelForm):

    INDUSTRY_CHOICES = [
        ("", "Choose an industry"),
        ("technology", "Technology"),
        ("beauty", "Beauty & Skincare"),
        ("fashion", "Fashion"),
        ("food", "Food & Beverage"),
        ("education", "Education"),
        ("finance", "Finance"),
        ("health", "Health & Wellness"),
        ("real_estate", "Real Estate"),
        ("ecommerce", "E-commerce"),
        ("entertainment", "Entertainment"),
        ("professional_services", "Professional Services"),
        ("travel", "Travel"),
        ("other", "Other"),
    ]

    AUDIENCE_CHOICES = [
        ("Individuals", "Individuals"),
        ("Businesses", "Businesses"),
        ("Developers", "Developers"),
        ("Creators", "Creators"),
        ("Students", "Students"),
        ("Professionals", "Professionals"),
        ("Entrepreneurs", "Entrepreneurs"),
        ("Parents", "Parents"),
        ("Beginners", "Beginners"),
        ("Experts", "Experts"),
        ("Other", "Other"),
    ]

    PLATFORM_CHOICES = [
        ("LinkedIn", "LinkedIn"),
        ("Instagram", "Instagram"),
        ("TikTok", "TikTok"),
        ("YouTube", "YouTube"),
        ("Facebook", "Facebook"),
        ("X", "X"),
        ("Threads", "Threads"),
        ("Pinterest", "Pinterest"),
    ]

    target_audience = forms.MultipleChoiceField(
        choices=AUDIENCE_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    platforms = forms.MultipleChoiceField(
        choices=PLATFORM_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    industry = forms.ChoiceField(
        required=False,
        choices=INDUSTRY_CHOICES,
        widget=forms.Select(attrs={
            "class": "form-select",
        }),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["industry"].widget.attrs.update({
            "class": "form-select",
        })
    class Meta:
        model = Brand

        fields = [
            "name",
            "brand_type",
            "industry",
            "niche",
            "primary_goal",
            "target_audience",
            "platforms",
            "additional_information",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control form-control-lg",
                    "placeholder": "e.g. James, ALPHIX, Glow Beauty",
                }
            ),

            "brand_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "niche": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. Web Development & AI",
                }
            ),

            "primary_goal": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "additional_information": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 6,
                    "placeholder": (
                        "Tell Workbeam anything else about your brand. "
                        "You can write naturally — your story, products, "
                        "audience, personality, goals, or anything useful."
                    ),
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Convert stored comma-separated text back into selections.
        if self.instance and self.instance.pk:
            self.fields["target_audience"].initial = [
                item.strip()
                for item in self.instance.target_audience.split(",")
                if item.strip()
            ]

            self.fields["platforms"].initial = [
                item.strip()
                for item in self.instance.platforms.split(",")
                if item.strip()
            ]

    def save(self, commit=True):
        instance = super().save(commit=False)

        instance.target_audience = ", ".join(
            self.cleaned_data.get("target_audience", [])
        )

        instance.platforms = ", ".join(
            self.cleaned_data.get("platforms", [])
        )

        if commit:
            instance.save()

        return instance