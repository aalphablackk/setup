from django.conf import settings
from tavily import TavilyClient

from research.models import ResearchItem, ResearchRunItem
from research.services.planner import ResearchPlanner


class WebResearchService:
    """
    Handles web research for Workbeam.

    The rest of Workbeam should interact with this service
    instead of calling Tavily directly.
    """

    DEPTH_SETTINGS = {
        "quick": {
            "max_queries": 2,
            "results_per_query": 3,
        },
        "standard": {
            "max_queries": 5,
            "results_per_query": 5,
        },
        "deep": {
            "max_queries": 8,
            "results_per_query": 5,
        },
    }

    def __init__(self):
        api_key = settings.TAVILY_API_KEY

        if not api_key:
            raise ValueError(
                "TAVILY_API_KEY is not configured."
            )

        self.client = TavilyClient(api_key=api_key)

    def search(self, query, max_results=5):
        """
        Search the web and return normalized research results.
        """

        response = self.client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results,
            include_answer=False,
            include_raw_content=True,
        )

        results = []

        for result in response.get("results", []):
            results.append(
                {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "raw_content": (
                        result.get("raw_content", "")
                        or result.get("content", "")
                    ),
                    "published_at": result.get("published_date"),
                    "metadata": {
                        "score": result.get("score"),
                    },
                }
            )

        return results

    def collect_for_session(self, session, run):
        source = session.sources.filter(
            source_type="web"
        ).first()

        if not source:
            raise ValueError(
                "No Web research source has been added to this session."
            )

        depth_settings = self.DEPTH_SETTINGS.get(
            session.depth,
            self.DEPTH_SETTINGS["standard"],
        )

        max_queries = depth_settings["max_queries"]
        results_per_query = depth_settings["results_per_query"]

        planner = ResearchPlanner()

        queries = planner.plan(session)
        queries = queries[:max_queries]

        # Preserve the exact queries used by this run.
        run.queries = queries
        run.search_count = len(queries)
        run.save(
            update_fields=[
                "queries",
                "search_count",
            ]
        )

        saved_items = []
        seen_urls = set()

        for query in queries:
            results = self.search(
                query,
                max_results=results_per_query,
            )

            for result in results:
                url = result.get("url")

                if not url:
                    continue

                if url in seen_urls:
                    continue

                seen_urls.add(url)

                item = ResearchItem.objects.filter(
                    source=source,
                    url=url,
                ).first()

                if not item:
                    item = ResearchItem.objects.create(
                        source=source,
                        title=result.get("title", ""),
                        url=url,
                        raw_content=result.get("raw_content", ""),
                        published_at=result.get("published_at"),
                        metadata={
                            **result.get("metadata", {}),
                            "research_query": query,
                        },
                    )

                ResearchRunItem.objects.get_or_create(
                    run=run,
                    item=item,
                )

                saved_items.append(item)

        run.result_count = len(saved_items)

        run.save(
            update_fields=[
                "result_count",
            ]
        )

        return saved_items