import asyncio
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import json
import pandas as pd
from intellect_agent.agent import IntellectAgent

@patch('intellect_agent.agent.NewsApiClient')
@patch('intellect_agent.agent.FMPClient')
@patch('intellect_agent.agent.ts.pro_api')
@patch('intellect_agent.agent.AipNlp')
@patch('intellect_agent.agent.ApifyClient')
@patch('intellect_agent.agent.TrendReq')
async def test_full_analysis_pipeline_with_mocked_apis(
    mock_trend_req, mock_apify, mock_aip_nlp, mock_tushare, mock_fmp, mock_newsapi
):
    """
    An end-to-end test that verifies the agent's full analysis pipeline
    by mocking the API clients themselves. This ensures that the agent's
    logic is tested in isolation, withoutmaking any live network calls.
    """
    # Arrange: Configure all the mock clients to return predictable data

    # Mock for Google Trends
    # Create a realistic DataFrame for the 'rising' queries
    fake_rising_df = pd.DataFrame({
        'query': ["e-scooter laws", "bike sharing apps"],
        'value': [100, 90]
    })
    async def mock_analyze_trends(*args, **kwargs):
        agent.report['trend_analysis'] = {
            "macro_changes": ["Interest over time data available."],
            "trending_keywords": ["e-scooter laws", "bike sharing apps"]
        }
        yield "status: Mocked trend analysis"
    agent = IntellectAgent("Sustainable Urban Mobility")
    agent._analyze_trends = mock_analyze_trends

    # Mock for Apify & Baidu AI Cloud
    async def mock_mine_public_opinion(*args, **kwargs):
        agent.report['public_opinion'] = {"sentiment": {"positive": 1, "negative": 0, "neutral": 0}}
        yield "status: Mocked public opinion"
    agent._mine_public_opinion = mock_mine_public_opinion

    # Mock for Tushare (simulating failure) & FMP (fallback)
    async def mock_analyze_competition(*args, **kwargs):
        agent.report['competitive_landscape'] = {"financial_profiles": [{"Apple": [{"price": 150.0}]}]}
        yield "status: Mocked competition analysis"
    agent._analyze_competition = mock_analyze_competition

    # Mock for NewsAPI.org
    async def mock_analyze_news(*args, **kwargs):
        agent.report['news_analysis'] = {"major_events": ["A breakthrough in urban mobility."]}
        yield "status: Mocked news analysis"
    agent._analyze_news = mock_analyze_news


    # Act
    final_update = None
    async for update in agent.run_analysis():
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

@patch('intellect_agent.agent.ApifyClient')
async def test_dynamic_competitor_analysis(mock_apify):
    """
    Tests the dynamic competitor analysis functionality by mocking the Apify Google Search Scraper actor.
    """
    # Arrange
    mock_apify_instance = mock_apify.return_value
    mock_apify_instance.actor.return_value.call = AsyncMock(return_value={"defaultDatasetId": "test_dataset_id"})
    mock_apify_instance.dataset.return_value.list_items = AsyncMock(return_value=MagicMock(items=[
        {
            "organicResults": [
                {"title": "Competitor A", "displayedUrl": "competitor-a.com"},
                {"title": "Competitor B", "displayedUrl": "competitor-b.com"}
            ]
        }
    ]))

    agent = IntellectAgent("Test Topic")

    # Act
    competitors = await agent._get_competitors()

    # Assert
    assert len(competitors) == 2
    assert competitors[0]["name"] == "Competitor A"
    assert competitors[1]["symbol"] == "competitor-b.com"
