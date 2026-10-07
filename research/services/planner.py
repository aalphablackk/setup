import json
import re

from django.conf import settings
from django.utils import timezone
from openai import OpenAI


class ResearchPlanner:
    """
    Converts a research brief into focused, current web research queries.
    """

    MODEL = "gpt-5.6"

    DEPTH_QUERY_LIMITS = {
        "quick": 2,
        "standard": 5,
        "deep": 8,
    }

    def __init__(self):
        api_key = settings.OPENAI_API_KEY

        if not api_key:
            raise ValueError("OPENAI_API_KEY is not configured.")

        self.client = OpenAI(api_key=api_key)

    def plan(self, session):
        current_date = timezone.now().date()
        current_year = current_date.year

        query_limit = self.DEPTH_QUERY_LIMITS.get(
            session.depth,
            self.DEPTH_QUERY_LIMITS["standard"],
        )

        brand_context = ""

        if session.mode == session.Mode.CONNECTED and session.brand:
            brand = session.brand

            brand_context = f"""
Brand context:

Brand name: {brand.name}
Brand type: {brand.get_brand_type_display()}
Industry: {brand.industry}
Niche: {brand.niche}
Primary goal: {brand.get_primary_goal_display()}
Target audience: {brand.target_audience}
Platforms: {brand.platforms}
Additional information: {brand.additional_information}

Use this information only to understand why the research matters.
Do not treat it as external evidence.
"""

        prompt = f"""
You are the Research Planner for Workbeam.

Your job is to convert a research brief into focused, useful web
research queries.

CURRENT DATE:
{current_date}

CURRENT YEAR:
{current_year}

Research title:
{session.title}

Research brief:
{session.research_brief}

Research depth:
{session.depth}

{brand_context}

Generate exactly {query_limit} research queries.

The queries should collectively investigate different useful angles
rather than repeating the same search.

Where appropriate, consider:

- market landscape
- audience needs
- problems
- trends
- demand
- competitors
- existing solutions
- objections or barriers
- opportunities
- recent developments

FRESHNESS RULES:

1. Treat the current date above as authoritative.
2. For current markets, trends, technologies, jobs, competitors,
   products, prices, regulations, and other time-sensitive subjects,
   prioritize the most recent available information.
3. When appropriate, include the current year ({current_year})
   in search queries.
4. Do not automatically use outdated year ranges when researching
   the current state of a topic.
5. Older sources may be used when they provide important historical,
   foundational, or longitudinal evidence.
6. Never describe older information as current merely because it
   is relevant.
7. When recent evidence is unavailable, make that limitation clear.
8. Prefer recent sources where the research question concerns
   the current state of a subject.

QUERY QUALITY RULES:

1. Queries must be specific and useful for web search.
2. Avoid vague queries.
3. Avoid duplicate or nearly identical queries.
4. Do not invent facts.
5. Do not answer the research question yourself.
6. Queries should gather evidence rather than conclusions.
7. Prefer queries that can produce current and authoritative sources.
8. Keep each query concise.
9. Use different research angles across the queries.
10. Return ONLY valid JSON.

Return exactly:

{{
    "queries": [
        "query 1",
        "query 2"
    ]
}}
"""

        response = self.client.responses.create(
            model=self.MODEL,
            input=prompt,
        )

        output = response.output_text.strip()

        try:
            result = json.loads(output)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "The AI returned invalid research plan JSON."
            ) from exc

        queries = result.get("queries")

        if not isinstance(queries, list):
            raise ValueError(
                "Research planner did not return a valid query list."
            )

        queries = [
            query.strip()
            for query in queries
            if isinstance(query, str) and query.strip()
        ]

        if not queries:
            raise ValueError(
                "Research planner returned no usable queries."
            )

        # Deterministic freshness processing.
        queries = [
            self._clean_query(query, current_year)
            for query in queries
        ]

        queries = [
            self._apply_freshness(query, current_year)
            for query in queries
        ]

        return queries[:query_limit]

    def _clean_query(self, query, current_year):
        """
        Remove stale recent years from a search query.
        """

        query = query.strip()

        for year in range(current_year - 3, current_year):
            query = re.sub(
                rf"\b{year}\b",
                "",
                query,
            )

        query = re.sub(
            r"\s+",
            " ",
            query,
        ).strip()

        return query

    def _apply_freshness(self, query, current_year):
        """
        Add the current year to queries that clearly concern
        current or time-sensitive subjects.
        """

        current_terms = (
            "current",
            "latest",
            "trend",
            "trends",
            "demand",
            "hiring",
            "jobs",
            "market",
            "performance",
            "opportunities",
            "skills",
            "business",
            "technology",
            "ai",
            "remote",
        )

        query_lower = query.lower()

        if (
            any(term in query_lower for term in current_terms)
            and str(current_year) not in query
        ):
            query = f"{query} {current_year}"

        return query