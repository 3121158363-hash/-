import pytest
from unittest.mock import patch
import json
from app.agent import IntellectAgent

# Mock search results to be returned by the patched google_search tool
MOCK_SEARCH_RESULTS_PRIMARY = [
    {"url": "https://trends.example.com", "title": "Google Trends Result", "snippet": "Data shows rising interest in the topic."}
]
MOCK_SEARCH_RESULTS_SECONDARY = [
    {"url": "https://analysis.example.com", "title": "Market Analysis 2024", "snippet": "Significant market growth and innovation noted."},
    {"url": "https://news.example.com", "title": "Industry News", "snippet": "New regulations are impacting the market."}
]

# Mock website content to be returned by the patched view_text_website tool
MOCK_WEBSITE_CONTENT = "Breakout interest detected. Top related queries include 'new features' and 'competitors'."

@patch('app.agent.google_search')
@patch('app.agent.view_text_website')
def test_analyze_trends_logic(mock_view_text_website, mock_google_search):
    """
    Tests the _analyze_trends method to ensure it correctly processes
    mocked API responses and structures the report data.
    """
    # Arrange: Configure the mocks to return predefined data
    mock_google_search.side_effect = [
        MOCK_SEARCH_RESULTS_PRIMARY,
        MOCK_SEARCH_RESULTS_SECONDARY
    ]
    mock_view_text_website.return_value = MOCK_WEBSITE_CONTENT

    # Act: Initialize the agent and call the method under test
    agent = IntellectAgent("test topic")
    agent._analyze_trends()

    # Assert: Verify that the report was populated with the expected data
    report = agent.report['trend_analysis']

    # Check that data from both primary and secondary searches is present
    assert "Significant rising interest noted in 'test topic'." in report['macro_changes']
    assert "Expert analysis suggests: Significant market growth and innovation noted." in report['macro_changes']

    # Check that keywords were extracted correctly
    assert "Keywords related to primary search are present." in report['trending_keywords']
    assert "market growth" in report['trending_keywords']
    assert "innovation" in report['trending_keywords']
    assert "regulation" in report['trending_keywords']

    # Verify that the tools were called with the correct queries
    mock_google_search.assert_any_call(query="Google Trends analysis for test topic")
    mock_google_search.assert_any_call(query="market trends and analysis for test topic 2024")
    mock_view_text_website.assert_called_once_with(url="https://trends.example.com")


@patch('app.agent.google_search')
def test_public_opinion_logic(mock_google_search):
    """
    Tests the public opinion analysis methods to ensure they correctly
    assess the need for a plugin and mine data from search results.
    """
    # Arrange: Mock the search results for the various opinion queries
    mock_google_search.side_effect = [
        # Preliminary search finds results, so plugin is not needed
        [{"url": "https://reddit.com/review", "title": "Review of Test Topic", "snippet": "Overall positive."}],
        # "wish" query
        [{"url": "https://reddit.com/wish", "title": "Feature Wishlist", "snippet": "I wish it had a dark mode."}],
        # "missing" query
        [{"url": "https://reddit.com/missing", "title": "What's Missing?", "snippet": "A key feature is missing."}],
        # "worst part" query
        [{"url": "https://reddit.com/worst", "title": "Worst Part", "snippet": "The worst part is the battery life."}],
    ]

    # Act
    agent = IntellectAgent("Test Topic")
    needs_plugin = agent._assess_public_opinion_data()
    agent._mine_public_opinion()
    report = agent.report['public_opinion']

    # Assert
    assert not needs_plugin
    assert "I wish it had a dark mode." in report['unmet_needs']
    assert "A key feature is missing." in report['unmet_needs']
    assert "The worst part is the battery life." in report['core_pain_points']
    assert "Feature Wishlist" in report['high_frequency_topics']


@patch('app.agent.google_search')
def test_competitive_landscape_logic(mock_google_search):
    """
    Tests the competitive landscape analysis to ensure it correctly
    identifies top players and finds negative sentiment.
    """
    # Arrange
    mock_google_search.side_effect = [
        # Search for top players
        [{"url": "https://markets.com/top", "title": "MegaCorp Leads the Pack", "snippet": "MegaCorp has the highest market share."}],
        # Search for negative sentiment
        [{"url": "https://news.com/complaints", "title": "MegaCorp Under Fire", "snippet": "Customers complain about MegaCorp's poor service."}]
    ]

    # Act
    agent = IntellectAgent("test topic")
    agent._analyze_competition()
    report = agent.report['competitive_landscape']

    # Assert
    assert "MegaCorp Leads the Pack" in report['top_players_and_products']
    assert "Customers complain about MegaCorp's poor service." in report['negative_intelligence']
    mock_google_search.assert_any_call(query='top companies in test topic market share')
    mock_google_search.assert_any_call(query='"MegaCorp" "test topic" "complaints" OR "issues"')


def test_final_report_generation():
    """
    Tests the _generate_report method to ensure it correctly synthesizes
    all collected data into the final five-part structure.
    """
    # Arrange
    agent = IntellectAgent("Electric Scooters")
    agent.report = {
        'trend_analysis': {'macro_changes': ['Rise of micro-mobility'], 'trending_keywords': ['sustainability', 'urban transport']},
        'public_opinion': {'unmet_needs': ['longer range batteries'], 'core_pain_points': ['lack of bike lanes']},
        'competitive_landscape': {'negative_intelligence': ['scooters breaking down easily']}
    }

    # Act
    report_str = agent._generate_report()
    report = json.loads(report_str)

    # Assert
    assert "executive_summary" in report
    assert "trends_analysis" in report
    assert "public_opinion" in report
    assert "competitive_landscape" in report
    assert "key_takeaways" in report

    assert "Rise of micro-mobility" in report['executive_summary']
    assert "longer range batteries" in report['executive_summary']

    assert report['key_takeaways']['opportunity_points'] == ['longer range batteries']
    assert report['key_takeaways']['risk_points'] == ['scooters breaking down easily']
