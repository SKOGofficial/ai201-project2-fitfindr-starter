"""
agent.py

The FitFindr planning loop. Orchestrates the three tools in response to a
natural language user query, passing state between them via a session dict.

Complete tools.py and test each tool in isolation before implementing this file.

Usage (once implemented):
    from agent import run_agent
    from utils.data_loader import get_example_wardrobe

    result = run_agent(
        query="vintage graphic tee under $30, size M",
        wardrobe=get_example_wardrobe(),
    )
    print(result["fit_card"])
    print(result["error"])   # None on success
"""

from tools import search_listings, suggest_outfit, create_fit_card
import re


# ── session state ─────────────────────────────────────────────────────────────

def _new_session(query: str, wardrobe: dict) -> dict:
    """
    Initialize and return a fresh session dict for one user interaction.

    The session dict is the single source of truth for everything that happens
    during a run — it stores the original query, parsed parameters, tool results,
    and any error that caused early termination.

    You may add fields to this dict as needed for your implementation.
    """
    return {
        "query": query,              # original user query
        "parsed": {},                # extracted description / size / max_price
        "search_results": [],        # list of matching listing dicts
        "selected_item": None,       # top result, passed into suggest_outfit
        "wardrobe": wardrobe,        # user's wardrobe dict
        "outfit_suggestion": None,   # string returned by suggest_outfit
        "fit_card": None,            # string returned by create_fit_card
        "error": None,               # set if the interaction ended early
    }

# ── helper: parser ────────────────────────────────────────────────────────────

def _parse_query(query: str) -> dict:
    """
    Parses the user query using regex to extract description, size, and max_price.
    Implementation note: Regex is used for simplicity and speed.
    """
    # Extract price (e.g., "$30" or "30")
    price_match = re.search(r'\$?(\d+)', query)
    max_price = int(price_match.group(1)) if price_match else None
    
    # Extract size (e.g., "size M" or "size L")
    size_match = re.search(r'size\s+(\w+)', query, re.IGNORECASE)
    size = size_match.group(1).upper() if size_match else None
    
    # Simple description extraction: remove price/size info and clean
    description = re.sub(r'(\$?\d+|size\s+\w+|under)', '', query, flags=re.IGNORECASE).strip()
    
    return {
        "description": description,
        "size": size,
        "max_price": max_price
    }

# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Main agent entry point. Runs the FitFindr planning loop.
    """
    # Step 1: Initialize
    session = _new_session(query, wardrobe)
    
    # Step 2: Parse
    session["parsed"] = _parse_query(query)
    
    # Step 3: Search
    session["search_results"] = search_listings(
        description=session["parsed"]["description"],
        size=session["parsed"]["size"],
        max_price=session["parsed"]["max_price"]
    )
    
    if not session["search_results"]:
        session["error"] = f"No items found matching: {query}"
        return session
    
    # Step 4: Select top item
    session["selected_item"] = session["search_results"][0]
    
    print(session["selected_item"])
    
    # Step 5: Suggest outfit
    session["outfit_suggestion"] = suggest_outfit(
        new_item=session["selected_item"],
        wardrobe=session["wardrobe"]
    )

    print(session["outfit_suggestion"])
    
    # Step 6: Create fit card
    session["fit_card"] = create_fit_card(
        outfit=session["outfit_suggestion"],
        new_item=session["selected_item"]
    )
    
    # Step 7: Return
    return session


# ── CLI test ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe, get_empty_wardrobe

    print("=== Happy path: graphic tee ===\n")
    session = run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    )
    if session["error"]:
        print(f"Error: {session['error']}")
    else:
        print(f"Found: {session['selected_item']['title']}")
        print(f"\nOutfit: {session['outfit_suggestion']}")
        print(f"\nFit card: {session['fit_card']}")

    print("\n\n=== No-results path ===\n")
    session2 = run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    )
    print(f"Error message: {session2['error']}")
