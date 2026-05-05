from ddgs import DDGS

def search_web(query: str, max_results: int = 3) -> str:
    """Searches DuckDuckGo and returns context, with crash protection."""
    try:
        with DDGS() as ddgs:
            # Attempt to search the web
            results = list(ddgs.text(query, max_results=max_results))
            
            if not results:
                return "No search results found on the web."
            
            context = ""
            for res in results:
                context += f"Snippet: {res.get('body')}\n"
                
            return context
            
    except Exception as e:
        # If DuckDuckGo rate-limits us or crashes, catch the error!
        print(f"DuckDuckGo Error: {e}")
        return "WEB SEARCH ERROR: The live web search is temporarily rate-limited. Please wait 30 seconds and try again."
