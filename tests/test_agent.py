import pytest
from unittest.mock import patch, MagicMock
import json
from app.agent import IntellectAgent

@patch('app.agent.google_search')
def test_analyze_trends_deep_integration(mock_google_search):
    """
    Tests the refactored _analyze_trends method to ensure it correctly
    handles simulated structured API data.
    """
    # Arrange
    mock_google_search.side_effect = [
        [{"url": "trends.com", "snippet": "rising"}], # For primary trends search
        [{"url": "news.com", "snippet": "Cross-validation confirms growth."}]   # For cross-validation search
    ]
    agent = IntellectAgent("test topic")

    # Act
    list(agent._analyze_trends()) # Consume the generator
    report = agent.report['trend_analysis']

    # Assert
    assert "Data indicates a significant rising interest in 'test topic'." in report['macro_changes']
    assert "Cross-validation from news sources confirms: Cross-validation confirms growth." in report['macro_changes']

    mock_google_search.assert_any_call(query="structured Google Trends data for test topic")
    mock_google_search.assert_any_call(query='"test topic" market trends news')


@patch('app.agent.google_search')
def test_competitive_landscape_cross_validation(mock_google_search):
    """
    Tests the cross-validation logic in the _analyze_competition method.
    """
    # Arrange
    mock_google_search.side_effect = [
        [{"url": "markets.com", "snippet": "Top players."}], # For financial data
        [{"url": "complaints.com", "snippet": "Primary issue."}], # For FutureTech complaints
        [{"url": "news.com", "snippet": "Negative news."}], # For FutureTech news
        [{"url": "complaints.com", "snippet": "Another issue."}], # For InnovateCorp complaints
        [] # For InnovateCorp news (to test robustness)
    ]
    agent = IntellectAgent("test topic")

    # Act
    list(agent._analyze_competition()) # Consume the generator
    report = agent.report['competitive_landscape']

    # Assert
    assert "Primary issues for FutureTech: Primary issue." in report['negative_intelligence']
    assert "Cross-validation from news for FutureTech: Negative news." in report['negative_intelligence']
    assert "Primary issues for InnovateCorp: Another issue." in report['negative_intelligence']

    # Verify that the cross-validation search for InnovateCorp was still attempted
    mock_google_search.assert_any_call(query='"InnovateCorp" "test topic" "negative news"')


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

@patch('app.agent.os.path.exists', return_value=True)
@patch('app.agent.importlib.util')
def test_external_plugin_execution(mock_importlib_util, mock_path_exists):
    """
    Tests that the agent correctly discovers, loads, and executes a plugin.py file.
    """
    # Arrange
    # Mock the plugin module and its function
    mock_plugin_module = MagicMock()
    mock_plugin_module.run_opinion_miner.return_value = {
        "high_frequency_topics": ["From External Plugin"],
        "core_pain_points": ["Plugin Pain Point"],
        "unmet_needs": ["Plugin Unmet Need"]
    }

    # Configure the importlib mock to simulate a successful import
    spec = MagicMock()
    spec.loader.exec_module.return_value = None
    mock_importlib_util.spec_from_file_location.return_value = spec
    mock_importlib_util.module_from_spec.return_value = mock_plugin_module

    agent = IntellectAgent("test topic")

    # Act
    list(agent._mine_public_opinion()) # Consume the generator
    report = agent.report['public_opinion']

    # Assert
    assert report["high_frequency_topics"] == ["From External Plugin"]
    mock_plugin_module.run_opinion_miner.assert_called_once()


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
