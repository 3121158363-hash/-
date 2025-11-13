import pytest
from unittest.mock import patch, MagicMock
import json
from app.agent import IntellectAgent

def test_report_generation_structure():
    """
    Tests that the _generate_report method produces a report with the correct structure.
    """
    # Arrange
    agent = IntellectAgent("Test Topic")
    agent.report = {
        'trend_analysis': {"macro_changes": ["mock change"]},
        'public_opinion': {"unmet_needs": ["mock need"]},
        'competitive_landscape': {"negative_intelligence": ["mock risk"]},
        'news_analysis': {}
    }

    # Act
    report_str = agent._generate_report()
    report = json.loads(report_str)

    # Assert
    assert "executive_summary" in report
    assert "trends_analysis" in report
    assert "public_opinion" in report
    assert "competitive_landscape" in report
    assert "news_and_policy" in report
    assert "key_takeaways" in report
    assert "opportunity_points" in report["key_takeaways"]
    assert "risk_points" in report["key_takeaways"]

@patch('app.agent.google_search')
def test_agent_analysis_flow(mock_google_search):
    """
    Tests the full analysis flow of the agent, ensuring each stage
    contributes to the final report.
    """
    # Arrange
    mock_google_search.return_value = [{"title": "Mock Title", "snippet": "Mock Snippet"}]
    agent = IntellectAgent("electric vehicles")

    # Act
    # Consume the generator to run the full analysis
    final_update = None
    for update in agent.run_analysis():
        if update.startswith("final_update:"):
            final_update = update

    # Assert
    assert final_update is not None, "Agent did not produce a final report."

    report_json_str = final_update.replace("final_update:", "")
    report_data = json.loads(report_json_str)

    # Check that the report structure is present in the final output
    assert 'report' in report_data
    final_report = json.loads(report_data['report'])

    # Check that each analysis stage has populated its part of the report
    assert len(final_report['trends_analysis']['macro_changes']) > 0
    assert len(final_report['public_opinion']['high_frequency_topics']) > 0
    assert len(final_report['competitive_landscape']['top_players_and_products']) > 0
    assert len(final_report['news_and_policy']['major_events']) > 0
