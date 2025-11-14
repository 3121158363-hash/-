import pytest
from unittest.mock import patch, MagicMock
import json
from app.agent import IntellectAgent

@patch('app.agent.NewsApiClient')
@patch('app.agent.FMPClient')
@patch('app.agent.ts.pro_api')
@patch('app.agent.AipNlp')
@patch('app.agent.ApifyClient')
@patch('app.agent.TrendReq')
def test_full_analysis_pipeline_with_mocked_apis(
    mock_trend_req, mock_apify, mock_aip_nlp, mock_tushare, mock_fmp, mock_newsapi
):
    """
    An end-to-end test that verifies the agent's full analysis pipeline
    by mocking the API clients themselves. This ensures that the agent's
    logic is tested in isolation, without making any live network calls.
    """
    # Arrange: Configure all the mock clients to return predictable data

    # Mock for Google Trends
    mock_rising_df = MagicMock()
    mock_rising_df.empty = False
    mock_rising_df.to_frame.return_value.head.return_value.values.tolist.return_value = ["e-scooter laws", "bike sharing apps"]
    mock_trend_req.return_value.related_queries.return_value = {'Sustainable Urban Mobility': {'rising': mock_rising_df}}
    mock_trend_req.return_value.interest_over_time.return_value = MagicMock(empty=False)

    # Mock for Apify & Baidu AI Cloud
    mock_apify.return_value.actor.return_value.call.return_value = {"output": [{"text": "Sample comment 1"}, {"text": "Sample comment 2"}]}
    mock_aip_nlp.return_value.sentimentClassify.return_value = {'items': [{'sentiment': 2}]}

    # Mock for Tushare (simulating failure) & FMP (fallback)
    mock_tushare.return_value.daily.return_value = MagicMock(empty=True)
    mock_fmp.return_value.quote.return_value = [{"symbol": "AAPL", "price": 150.0}]

    # Mock for NewsAPI.org
    mock_newsapi.return_value.get_everything.return_value = {"articles": [{"title": "New Tech", "description": "A breakthrough in urban mobility."}]}

    agent = IntellectAgent("Sustainable Urban Mobility")

    # Act
    final_update = None
    for update in agent.run_analysis():
        if update.startswith("final_update:"):
            final_update = update

    # Assert
    assert final_update is not None, "Agent did not produce a final report."

    report_json_str = final_update.replace("final_update:", "")
    report_data = json.loads(report_json_str)
    report = json.loads(report_data['report'])

    # Verify that each section contains data from the mocked APIs
    assert "e-scooter laws" in report["trends_analysis"]["trending_keywords"]
    assert report["public_opinion"]["sentiment"]["positive"] > 0
    assert report["competitive_landscape"]["financial_profiles"][0]["Apple"][0]["price"] == 150.0
    assert "breakthrough" in report["news_and_policy"]["major_events"][0]
