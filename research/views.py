from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
import threading
from brands.models import Brand

from .models import ResearchSession, ResearchSource, ResearchItem
from .services.run import ResearchRunService
from research.services.intelligence import ResearchIntelligenceService
from django.http import JsonResponse

# Create your views here.

@login_required
def research_home(request):
    sessions = ResearchSession.objects.filter(
        created_by=request.user
    ).select_related("brand")

    independent_sessions = ResearchSession.objects.filter(
        created_by=request.user,
        brand__isnull=True,
    )

    sessions = (sessions | independent_sessions).order_by("-updated_at")

    brands = Brand.objects.filter(
        created_by=request.user,
        is_active=True,
    )

    return render(
        request,
        "research/research_home.html",
        {
            "sessions": sessions,
            "brands": brands,
        },
    )


@login_required
def research_create(request):
    if request.method == "POST":
        mode = request.POST.get("mode")
        depth = request.POST.get(
            "depth",
            ResearchSession.Depth.STANDARD,
        )
        title = request.POST.get("title", "").strip()
        research_brief = request.POST.get(
            "research_brief",
            "",
        ).strip()
        brand_id = request.POST.get("brand")

        if not title or not research_brief:
            return render(
                request,
                "research/research_create.html",
                {
                    "brands": Brand.objects.filter(
                        created_by=request.user,
                        is_active=True,
                    ),
                    "error": "Please provide a title and research brief.",
                },
            )

        # Validate depth
        if depth not in ResearchSession.Depth.values:
            depth = ResearchSession.Depth.STANDARD

        brand = None

        if mode == ResearchSession.Mode.CONNECTED and brand_id:
            brand = get_object_or_404(
                Brand,
                pk=brand_id,
                created_by=request.user,
                is_active=True,
            )

        session = ResearchSession.objects.create(
            created_by=request.user,
            brand=brand,
            mode=mode,
            depth=depth,
            title=title,
            research_brief=research_brief,
        )

        return redirect(
            "research:home"
        )

    brands = Brand.objects.filter(
        created_by=request.user,
        is_active=True,
    )

    return render(
        request,
        "research/research_create.html",
        {
            "brands": brands,
        },
    )



@login_required
def research_detail(request, pk):
    session = get_object_or_404(
        ResearchSession.objects.select_related("brand"),
        pk=pk,
        created_by=request.user,
    )

    sources = session.sources.filter(is_active=True)

    latest_run = session.runs.first()

    # All evidence collected for this research session
    items = (
        ResearchItem.objects
        .filter(source__session=session)
        .select_related("source")
        .distinct()
    )

    # All findings accumulated across research runs
    findings = session.findings.all()

    intelligence_service = ResearchIntelligenceService()

    what_matters_now = (
        intelligence_service.get_what_matters_now(
            session=session,
            limit=5,
        )
    )

    signal_counts = {
        "problems": findings.filter(
            finding_type="problem"
        ).count(),

        "trends": findings.filter(
            finding_type="trend"
        ).count(),

        "opportunities": findings.filter(
            finding_type="opportunity_signal"
        ).count(),

        "questions": findings.filter(
            finding_type="question"
        ).count(),
    }

    confidence_order = {
        "high": 0,
        "medium": 1,
        "low": 2,
    }

    ordered_findings = sorted(
        findings,
        key=lambda finding: (
            confidence_order.get(
                finding.confidence,
                3,
            ),
            finding.created_at,
        ),
    )
    

    key_findings = ordered_findings[:5]
    all_findings = ordered_findings[5:]

    return render(
        request,
        "research/research_detail.html",
        {
            "session": session,
            "sources": sources,
            "items": items,
            "findings": findings,
            "key_findings": key_findings,
            "signal_counts": signal_counts,
            "all_findings": all_findings,
            "latest_run": latest_run,
            "what_matters_now": what_matters_now,
        },
    )

@login_required
def research_source_add(request, pk):
    session = get_object_or_404(
        ResearchSession,
        pk=pk,
        created_by=request.user,
    )

    if request.method == "POST":
        source_type = request.POST.get("source_type")
        name = request.POST.get("name", "").strip()
        url = request.POST.get("url", "").strip()

        if source_type != ResearchSource.SourceType.WEB or not name:
            return render(
                request,
                "research/research_source_add.html",
                {
                    "session": session,
                    "error": "Only Web research sources are currently supported.",
                },
            )

        # Prevent duplicate URLs within the same session.
        if url and session.sources.filter(
            source_type=ResearchSource.SourceType.WEB,
            url__iexact=url,
            is_active=True,
        ).exists():
            return render(
                request,
                "research/research_source_add.html",
                {
                    "session": session,
                    "error": "This source URL has already been added to this research session.",
                },
            )

        ResearchSource.objects.create(
            session=session,
            source_type=source_type,
            name=name,
            url=url,
        )

        return redirect("research:detail", pk=session.pk)

    return render(
        request,
        "research/research_source_add.html",
        {"session": session},
    )


@login_required
def research_run(request, pk):
    session = get_object_or_404(
        ResearchSession,
        pk=pk,
        created_by=request.user,
    )

    if request.method != "POST":
        return redirect("research:detail", pk=session.pk)

    if session.status == ResearchSession.Status.RESEARCHING:
        return redirect("research:detail", pk=session.pk)
    
    posted_depth = request.POST.get("depth")

    if posted_depth in ResearchSession.Depth.values:
        session.depth = posted_depth
        session.save(update_fields=["depth", "updated_at"])

    def run_research():
        try:
            ResearchRunService().execute(session)
        except Exception:
            # The service records the failure on ResearchRun.
            pass

    thread = threading.Thread(
        target=run_research,
        daemon=True,
    )

    thread.start()

    return redirect("research:detail", pk=session.pk)


@login_required
def research_run_status(request, pk):
    session = get_object_or_404(
        ResearchSession,
        pk=pk,
        created_by=request.user,
    )

    run = session.runs.first()

    if not run:
        return JsonResponse({
            "status": "idle",
            "stage": None,
            "message": "No research run has started.",
        })

    return JsonResponse({
        "status": run.status,
        "stage": run.stage,
        "message": run.stage_message,
        "search_count": run.search_count,
        "result_count": run.result_count,
        "error": run.error_message if run.status == "failed" else None,
    })

@login_required
def research_source_remove(request, pk, source_pk):
    if request.method != "POST":
        return redirect("research:detail", pk=pk)

    session = get_object_or_404(
        ResearchSession,
        pk=pk,
        created_by=request.user,
    )

    source = get_object_or_404(
        ResearchSource,
        pk=source_pk,
        session=session,
        is_active=True,
    )

    source.is_active = False
    source.save(update_fields=["is_active"])

    return redirect("research:detail", pk=session.pk)