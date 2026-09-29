from django.shortcuts import render

# Create your views here.


from django.shortcuts import render


def home(request):
    context = {
        "opportunities_count": 12,
        "drafts_count": 4,
        "review_count": 2,
        "scheduled_count": 5,

        "opportunities": [
            {
                "title": "AI tools for everyday developers",
                "description": (
                    "Developers are increasingly interested in practical "
                    "ways AI can remove repetitive work."
                ),
                "signal": "High opportunity",
                "icon": "bi-fire",
            },
            {
                "title": "What I learned building with Django",
                "description": (
                    "Educational developer content with a strong "
                    "human-experience angle."
                ),
                "signal": "Strong relevance",
                "icon": "bi-lightbulb",
            },
            {
                "title": "The beginner developer journey",
                "description": (
                    "Relatable content around learning, mistakes and "
                    "building real projects."
                ),
                "signal": "Growing topic",
                "icon": "bi-graph-up-arrow",
            },
        ],
    }

    return render(
        request,
        "dashboard/home.html",
        context,
    )