# tests/test_tools.py
import pytest

from tools import (
    search_listings,
    suggest_outfit,
    create_fit_card,
)


def test_search_listings_no_results():
    """Should return an empty list when nothing matches."""
    results = search_listings(
        description="purple dinosaur tuxedo",
        size="XXXL",
        max_price=1.00,
    )

    assert results == []


def test_suggest_outfit_empty_wardrobe(monkeypatch):
    """Should still return styling advice if wardrobe is empty."""

    class FakeResponse:
        output_text = "Pair it with relaxed jeans and white sneakers."

    class FakeClient:
        class responses:
            @staticmethod
            def create(*args, **kwargs):
                return FakeResponse()

    # Replace your global OpenAI client with a fake one
    monkeypatch.setattr("tools.client", FakeClient())

    new_item = {
        "title": "Vintage Graphic Tee",
        "description": "Faded cotton tee",
        "price": 20.0,
        "platform": "Depop",
    }

    wardrobe = {"items": []}

    result = suggest_outfit(new_item, wardrobe)

    assert isinstance(result, str)
    assert len(result) > 0


def test_create_fit_card_missing_outfit():
    """Should return an error message instead of crashing."""

    new_item = {
        "title": "Vintage Graphic Tee",
        "price": 20.0,
        "platform": "Depop",
    }

    result = create_fit_card("", new_item)

    assert isinstance(result, str)
    assert "missing" in result.lower() or "unable" in result.lower()


def test_create_fit_card_whitespace_outfit():
    """Whitespace-only outfits should also be treated as missing."""

    new_item = {
        "title": "Vintage Hoodie",
        "price": 35.0,
        "platform": "Poshmark",
    }

    result = create_fit_card("   ", new_item)

    assert "missing" in result.lower() or "unable" in result.lower()

def test_search_returns_results():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    assert isinstance(results, list)
    assert len(results) > 0

def test_search_empty_results():
    results = search_listings("designer ballgown", size="XXS", max_price=5)
    assert results == []   # empty list, no exception

def test_search_price_filter():
    results = search_listings("jacket", size=None, max_price=10)
    assert all(item["price"] <= 10 for item in results)