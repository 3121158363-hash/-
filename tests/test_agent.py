import pytest
from unittest.mock import patch
import json
from app.agent import IntellectAgent

@patch('app.agent.google_search')
def test_analyze_trends_deep_integration(mock_google_search):
    """
    Tests the refactored _analyze_trends method to ensure it correctly
    handles simulated structured API data.
    """
    # Arrange
    agent = IntellectAgent("test topic")

    # Act
    list(agent._analyze_trends()) # Consume the generator
    report = agent.report['trend_analysis']

    # Assert
    assert "Data indicates a significant rising interest in 'test topic'." in report['macro_changes']
    assert "Market growth is projected to be strong, driven by new technology." in report['macro_changes']
    assert "innovation in test topic" in report['trending_keywords']
    assert "test topic regulation" in report['trending_keywords']

    mock_google_search.assert_any_call(query="structured Google Trends data for test topic")
    mock_google_search.assert_any_call(query="expert analysis and market reports for test topic")


@patch('app.agent.google_search')
def test_plugin_interface_logic(mock_google_search):
    """
    Tests the refactored _mine_public_opinion method to ensure it correctly
    processes the simulated output of a plugin.
    """
    # Arrange
    agent = IntellectAgent("Test Topic")

    # Act
    list(agent._mine_public_opinion()) # Consume the generator
    report = agent.report['public_opinion']

    # Assert
    assert "Users are requesting a more beginner-friendly tutorial." in report['unmet_needs']
    assert "Frequent crashes on new hardware." in report['core_pain_points']
    assert "Community Feature Requests" in report['high_frequency_topics']


@patch('app.agent.google_search')
def test_competitive_landscape_deep_integration(mock_google_search):
    """
    Tests the refactored _analyze_competition method to ensure it correctly
    handles simulated structured financial data.
    """
    # Arrange
    mock_google_search.return_value = [{"url": "https://news.com/complaints", "title": "FutureTech Issues", "snippet": "Customers complain about FutureTech's product overheating."}]
    agent = IntellectAgent("test topic")

    # Act
    list(agent._analyze_competition()) # Consume the generator
    report = agent.report['competitive_landscape']

    # Assert
    assert "FutureTech (Product: FutureOne, Market Share: 35.0%)" in report['top_players_and_products']
    assert "InnovateCorp (Product: InnoPad, Market Share: 28.0%)" in report['top_players_and_products']
    assert "FutureTech: Customers complain about FutureTech's product overheating." in report['negative_intelligence']

    mock_google_search.assert_any_call(query='financial data and market share for test topic')
    mock_google_search.assert_any_call(query='"FutureTech" "test topic" "complaints" OR "issues"')
    mock_google_search.assert_any_call(query='"InnovateCorp" "test topic" "complaints" OR "issues"')


def test_enhanced_report_generation():
    """
    Tests the enhanced _generate_report method to ensure it correctly
    synthesizes a more intelligent executive summary.
    """
    # Arrange
    agent = IntellectAgent("Electric Scooters")
    agent.report = {
        'trend_analysis': {'macro_changes': ['Data indicates a significant rising interest in the market.'], 'trending_keywords': []},
        'public_opinion': {'unmet_needs': ['longer range batteries'], 'core_pain_points': []},
        'competitive_landscape': {'negative_intelligence': ['scooters breaking down easily']}
    }

    # Act
    report_str = agent._generate_report()
    report = json.loads(report_str)

    # Assert
    # Check for the more dynamic and data-driven summary
    assert "rising interest" in report['executive_summary']
    assert "longer range batteries" in report['executive_summary']
    assert "scooters breaking down easily" in report['executive_summary']

    # Ensure all 5 parts are still present
    assert all(k in report for k in ["executive_summary", "trends_analysis", "public_opinion", "competitive_landscape", "key_takeaways"])


@patch('app.agent.google_search')
def test_adaptation_logic(mock_google_search):
    """
    Tests the _execute_and_adapt method to ensure that it calls the
    fallback method when the primary method returns empty data.
    """
    # Arrange
    # The primary searches will return empty lists, forcing the fallback.
    # The fallback search will return a result.
    mock_google_search.side_effect = [
        [], # For primary trends search
        [], # For primary news search
        [{"url": "https://fallback.com", "title": "Fallback Discussion", "snippet": "General discussion about the topic."}] # For fallback
    ]
    agent = IntellectAgent("test topic")

    # Act
    # We need to consume the generator to execute the logic
    updates = list(agent._execute_and_adapt(
        primary_method=agent._analyze_trends,
        fallback_method=agent._analyze_trends_fallback,
        report_key='trend_analysis'
    ))

    # Assert
    report = agent.report['trend_analysis']
    assert "Primary trend data source failed." in report['macro_changes'][0]

    # Check that the status updates reflect the adaptation
    assert any("Adapting..." in update for update in updates)
