import pytest
from unittest.mock import patch, MagicMock
import json
from app.agent import IntellectAgent

@patch('app.agent.google_search')
def test_analyze_trends_with_fallback(mock_google_search):
    """
    Tests that the _analyze_trends method correctly uses its internal
    fallback when the primary search fails.
    """
    # Arrange
    mock_google_search.side_effect = [
        [], # Primary search fails
        [{"url": "news.com", "snippet": "Fallback news snippet."}] # Fallback search succeeds
    ]
    agent = IntellectAgent("test topic")

    # Act
    list(agent._analyze_trends()) # Consume the generator
    report = agent.report['trend_analysis']

    # Assert
    assert "Fallback analysis from news indicates: Fallback news snippet." in report['macro_changes']
    mock_google_search.assert_any_call(query='"test topic" market trends news')


@patch('app.agent.google_search')
def test_analyze_competition_with_fallback(mock_google_search):
    """
    Tests that the _analyze_competition method correctly uses its internal
    fallback when the primary search fails.
    """
    # Arrange
    mock_google_search.side_effect = [
        [], # Primary search fails
        [{"url": "competitors.com", "snippet": "General competitor discussion."}] # Fallback search succeeds
    ]
    agent = IntellectAgent("test topic")

    # Act
    list(agent._analyze_competition()) # Consume the generator
    report = agent.report['competitive_landscape']

    # Assert
    assert "Fallback analysis found general competitor discussion: General competitor discussion." in report['top_players_and_products']
    mock_google_search.assert_any_call(query='"test topic" "competitors" OR "vs"')


def test_enhanced_report_generation():
    """
    Tests the enhanced _generate_report method to ensure it correctly
    synthesizes a more intelligent executive summary.
    """
    # Arrange
    agent = IntellectAgent("Electric Scooters")
    agent.report = {
        'trend_analysis': {'macro_changes': ['Data indicates a significant rising interest in the market.'], 'trending_keywords': ['sustainability', 'urban transport']},
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
