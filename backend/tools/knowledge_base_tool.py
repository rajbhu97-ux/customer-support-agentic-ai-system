from langchain_core.tools import tool


@tool
def search_knowledge_base(query: str) -> list[dict]:
    """Search the knowledge base by keyword matching against tags and title."""
    # query_lower = query.lower()
    # results = []
    # for article in get_knowledge_base():
    #     tags_match = any(query_lower in tag for tag in article["tags"])
    #     title_match = query_lower in article["title"].lower()
    #     body_match = query_lower in article["body"].lower()
    #     if tags_match or title_match or body_match:
    #         results.append(article)
    # return results if results else [{"message": "No articles found matching your query"}]
    pass