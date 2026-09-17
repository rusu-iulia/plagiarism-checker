from unittest.mock import patch

import app as app_module

class FakeSearchProvider:
    # simulating a successful search provider API call
    # returning a list of mock search results to avoid real search engines
    def search(self, query, num_results = 5):
        return [
                    {"title": "Example Source", "url": "https://example.com/source-1"},
                    {"title": "Unrelated Source", "url": "https://example.com/source-2"},
                ]

class FailingSearchProvider:
    # simulating an external search API problem
    def search(self, query, num_results = 5):
        raise RuntimeError("simulated API failure")

def make_fake_fetch(pages):
    # factory function returning a mock web scraper implementation.
    def fake_fetch_and_clean(url, timeout = 10):
        return pages.get(url)
    return fake_fetch_and_clean

def test_detects_an_exact_copy_online():
    # verifying that exact duplicate content online is accurately recognised
    original_text = (
           "This is a unique sentence about quantum computing breakthroughs "
           "in superconducting qubits research labs today across the world."
    )
    # defining fake webpage contents. source-1 is an exact match, source-2 is irrelevant
    pages = {
        "https://example.com/source-1": original_text, 
        "https://example.com/source-2": (
            "Completely unrelated content about gardening and tomatoes and "
            "soil pH levels for home growers everywhere this season."
        ),
    }

    # patch external dependencies (search provider and HTTP scraper calls)
    with patch.object(app_module, "search_provider", FakeSearchProvider()), \
        patch("services.scraper.fetch_and_clean", make_fake_fetch(pages)), \
        patch.object(app_module, "fetch_and_clean", make_fake_fetch(pages)):
            results = app_module.run_plagiarism_check(original_text, "test.txt")

    # assertions: expecting positive plagiarism percentage, high/medium risk, and correct source match
    assert results["overall_percent"] > 0
    assert results["risk_level"] in {"Medium", "High"}
    assert any(m["url"] == "https://example.com/source-1" for m in results["matches"])
    assert not any(m["url"] == "https://example.com/source-2" for m in results["matches"])
    
def test_no_match_when_nothing_similar_exists():
    # verifying that when online search results contain no overlapping content, the report returns zero plagiarism percentage and a low risk.
    original_text = (
            "My cat likes to sit by the window every single morning watching "
            "birds outside quietly before breakfast time arrives each day."
        )
    pages = {
        "https://example.com/source-1": "Nothing here relates to that text whatsoever, not even close at all.",
        "https://example.com/source-2": "Stock market analysis reports for quarterly earnings season results.",
    }

    with patch.object(app_module, "search_provider", FakeSearchProvider()), \
            patch.object(app_module, "fetch_and_clean", make_fake_fetch(pages)):
        results = app_module.run_plagiarism_check(original_text, "test.txt")

    assert results["overall_percent"] == 0.0
    assert results["matches"] == []
    assert results["risk_level"] == "Low"

def test_search_failures_not_fatal():
    # ensuring third-party search API crashes are caught gracefully.
    text = "Some reasonably long piece of original text used only for this particular test case."

    with patch.object(app_module, "search_provider", FailingSearchProvider()):
            results = app_module.run_plagiarism_check(text, "test.txt")
    
    assert results["matches"] == []
    assert len(results["errors"]) > 0


def test_index_route_loads():
    # verifying that the home page renders successfully
    client = app_module.app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"Plagiarism Checker" in response.data


def test_check_route_requires_a_file():
    # verifying that submitting the check endpoint without a file prompts a validation message
    client = app_module.app.test_client()
    response = client.post("/check", data={})
    assert response.status_code == 200
    assert b"choose a file" in response.data


def test_missing_report_returns_404():
    client = app_module.app.test_client()
    response = client.get("/report/does-not-exist.pdf")
    assert response.status_code == 404
