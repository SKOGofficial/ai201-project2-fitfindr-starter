"""
tools.py

The three required FitFindr tools. Each tool is a standalone function that
can be called and tested independently before being wired into the agent loop.

Complete and test each tool before moving to agent.py.

Tools:
    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)              → str
    create_fit_card(outfit, new_item)               → str
"""

import os

from dotenv import load_dotenv
from groq import Groq

from utils.data_loader import load_listings

load_dotenv()


# ── Groq client ───────────────────────────────────────────────────────────────

def _get_groq_client():
    """Initialize and return a Groq client using GROQ_API_KEY from .env."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not set. Add it to a .env file in the project root."
        )
    return Groq(api_key=api_key)


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    listings = load_listings()

    query_words = set(re.findall(r"\w+", description.lower()))
    scored = []

    for listing in listings:
        # Price filter
        if max_price is not None and listing["price"] > max_price:
            continue

        # Size filter
        if size is not None:
            if size.lower() not in listing["size"].lower():
                continue

        # Build searchable text
        searchable = " ".join([
            listing.get("title", ""),
            listing.get("description", ""),
            listing.get("category", ""),
            " ".join(listing.get("style_tags", [])),
            listing.get("brand", "")
        ]).lower()

        listing_words = set(re.findall(r"\w+", searchable))

        score = len(query_words & listing_words)

        if score > 0:
            scored.append((score, listing))

    scored.sort(key=lambda x: x[0], reverse=True)

    return [listing for _, listing in scored]

# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    wardrobe_items = wardrobe.get("items", [])

    if not wardrobe_items:
        prompt = f"""
You are a fashion stylist.

The user is considering buying:

{new_item['title']}

Description:
{new_item['description']}

Give 1-2 casual styling ideas using common clothing items someone may already own.
Keep the response under 150 words.
"""
    else:
        wardrobe_text = "\n".join(
            f"- {item['name']} ({item['category']})"
            for item in wardrobe_items
        )

        prompt = f"""
You are a fashion stylist.

New thrift item:
{new_item['title']}

Wardrobe:
{wardrobe_text}

Suggest 1-2 outfits that use the thrifted item together with pieces from the wardrobe.
Mention wardrobe items by name.
Keep the response under 200 words.
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
    )

    return response.output_text.strip()


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    if not outfit or not outfit.strip():
        return "Unable to generate a Fit Card because the outfit recommendation is missing."

    prompt = f"""
Write a 2-4 sentence Instagram/TikTok outfit caption.

Requirements:
- Casual and authentic.
- Mention "{new_item['title']}" once.
- Mention the price (${new_item['price']}) once.
- Mention the platform ({new_item['platform']}) once.
- Base the caption on this outfit:

{outfit}

Do not use hashtags.
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        temperature=1.0,
    )

    return response.output_text.strip()