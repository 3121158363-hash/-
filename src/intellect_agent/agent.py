# src/intellect_agent/agent.py
import json
import logging
import os
import importlib.util
from pytrends.request import TrendReq
from apify_client import ApifyClient
from aip import AipNlp
import tushare as ts
from fmp_api_python.fmp import FMPClient
from newsapi import NewsApiClient
from . import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='src/intellect_agent/logs/agent.log',
    filemode='w'
)

class IntellectAgent:
    def __init__(self, topic):
        self.topic = topic
        self.report = {}
        self.status = "Idle"
        logging.info(f"IntellectAgent initialized for topic: {self.topic}")

    def run_analysis(self, deep_dive=False):
        logging.info(f"Starting analysis run... (Deep Dive: {deep_dive})")
        self.status = "Starting analysis..."
        yield f"status: {self.status}"

        # Stage 1: Trend Analysis
        yield from self._analyze_trends(deep_dive=deep_dive)
        logging.info("Trend analysis stage complete.")

        # Stage 2: Public Opinion Mining
        yield from self._mine_public_opinion(deep_dive=deep_dive)
        logging.info("Public opinion stage complete.")

        # Stage 3: Competitive Landscape
        yield from self._analyze_competition(deep_dive=deep_dive)
        logging.info("Competitive landscape stage complete.")

        # Stage 4: News Analysis
        yield from self._analyze_news(deep_dive=deep_dive)
        logging.info("News analysis stage complete.")

        # Stage 5: Final Report Generation
        self.status = "Compiling final report..."
        yield f"status: {self.status}"
        final_report_str = self._generate_report()
        logging.info("Final report generated.")

        self.status = "Analysis complete."
        yield f"final_update: {json.dumps({'status': self.status, 'report': final_report_str})}"
        logging.info("Analysis run finished.")

    def _analyze_trends(self, deep_dive=False):
        yield f"status: Analyzing trends for '{self.topic}' with Google Trends..."
        summary = {"macro_changes": [], "trending_keywords": []}
        try:
            pytrends = TrendReq(hl='en-US', tz=360)
            pytrends.build_payload([self.topic], cat=0, timeframe='today 3-m', geo='', gprop='')

            interest_over_time_df = pytrends.interest_over_time()
            if not interest_over_time_df.empty:
                summary["macro_changes"].append("Interest over time data available.")

            related_queries = pytrends.related_queries()
            rising_queries = related_queries[self.topic]['rising']
            if rising_queries is not None and not rising_queries.empty:
                summary["trending_keywords"].extend(rising_queries['query'].tolist())
        except Exception as e:
            logging.error(f"Pytrends API call failed: {e}")
            summary["macro_changes"].append("Google Trends API call failed.")

        self.report['trend_analysis'] = summary
        yield f"status: Trend analysis complete."

    def _mine_public_opinion(self, deep_dive=False):
        yield f"status: Scraping public opinion data for '{self.topic}' with Apify..."
        summary = {"high_frequency_topics": [], "core_pain_points": [], "unmet_needs": [], "sentiment": {}}
        try:
            apify_client = ApifyClient(config.APIFY_API_KEY)

            max_results = 2000 if deep_dive else 200
            yield f"status: (Deep Dive: {deep_dive}) Scraping up to {max_results} items..."
            # This is a placeholder for a real Apify actor run
            scraped_data = [{"text": f"The new {self.topic} is revolutionary!"}, {"text": f"I am disappointed with the high price of the {self.topic}."}] * (max_results // 2)

            yield f"status: Analyzing sentiment with Baidu AI Cloud..."
            client = AipNlp(config.BAIDU_APP_ID, config.BAIDU_API_KEY, config.BAIDU_SECRET_KEY)

            sentiments = []
            # Batching: Process comments in chunks of 10
            for i in range(0, len(scraped_data), 10):
                batch = [item['text'] for item in scraped_data[i:i+10]]
                # The Baidu NLP SDK does not support batching directly, so we send multiple texts in one request.
                for text in batch:
                    result = client.sentimentClassify(text)
                    if 'items' in result:
                        sentiments.append(result['items'][0]['sentiment'])

            summary['sentiment'] = {
                "positive": sentiments.count(2),
                "neutral": sentiments.count(1),
                "negative": sentiments.count(0)
            }
        except Exception as e:
            logging.error(f"Public opinion analysis failed: {e}")
            summary['core_pain_points'].append("API call for public opinion failed.")

        self.report['public_opinion'] = summary
        yield f"status: Public opinion analysis complete."

    def _analyze_competition(self, deep_dive=False):
        yield f"status: Identifying top competitors for '{self.topic}'..."
        competitors = [{"name": "Apple", "symbol": "AAPL"}, {"name": "Samsung", "symbol": "005930.KS"}]
        summary = {"financial_profiles": [], "market_position": []}

        ts.set_token(config.TUSHARE_API_KEY)
        pro = ts.pro_api()
        fmp_client = FMPClient(api_key=config.FMP_API_KEY)

        for competitor in competitors:
            financial_data = None
            try:
                yield f"status: Analyzing '{competitor['name']}' with Tushare..."
                if deep_dive:
                    yield f"status: (Deep Dive) Fetching 90-day time series..."
                    df = pro.daily(ts_code=competitor['symbol'], start_date='20230101', end_date='20230331')
                else:
                    df = pro.realtime_quotes(ts_code=competitor['symbol'])
                if not df.empty:
                    financial_data = df.to_dict('records')
            except Exception as e:
                logging.error(f"Tushare API call failed for {competitor['name']}: {e}")

            if financial_data:
                summary["financial_profiles"].append({competitor['name']: financial_data})
            else:
                yield f"status: Adapting: Tushare failed for '{competitor['name']}'. Trying FMP..."
                try:
                    if deep_dive:
                         quote = fmp_client.historical_price_full(competitor['symbol'], from_date='2023-01-01', to_date='2023-03-31')
                    else:
                        quote = fmp_client.quote(competitor['symbol'])
                    if quote:
                        summary["financial_profiles"].append({competitor['name']: quote})
                except Exception as fmp_e:
                    logging.error(f"FMP API call failed for {competitor['name']}: {fmp_e}")
                    summary["financial_profiles"].append({"company": competitor['name'], "error": "All financial data sources failed."})

        self.report['competitive_landscape'] = summary
        yield f"status: Competitive landscape analysis complete."

    def _analyze_news(self, deep_dive=False):
        yield f"status: Analyzing news & policy for '{self.topic}' with NewsAPI.org..."
        summary = {"major_events": [], "policy_changes": []}
        try:
            newsapi = NewsApiClient(api_key=config.NEWS_API_KEY)

            if deep_dive:
                yield f"status: (Deep Dive) Searching full news archive..."
                all_articles = newsapi.get_everything(q=self.topic,
                                                      language='en',
                                                      sort_by='relevancy')
            else:
                all_articles = newsapi.get_top_headlines(q=self.topic,
                                                         language='en',
                                                         category='business')

            for article in all_articles.get('articles', []):
                if "regulation" in article['title'].lower() or "policy" in article['title'].lower():
                    summary['policy_changes'].append(article['description'])
                else:
                    summary['major_events'].append(article['description'])
        except Exception as e:
            logging.error(f"NewsAPI call failed: {e}")
            summary['major_events'].append("NewsAPI call failed.")

        self.report['news_analysis'] = summary
        yield f"status: News analysis complete."

    def _generate_report(self):
        logging.info("Synthesizing final report.")

        trends_data = self.report.get('trend_analysis', {})
        public_opinion_data = self.report.get('public_opinion', {})
        competition_data = self.report.get('competitive_landscape', {})
        news_data = self.report.get('news_analysis', {})

        opportunities = public_opinion_data.get('unmet_needs', [])
        risks = competition_data.get('negative_intelligence', [])
        key_takeaways = {"opportunity_points": opportunities, "risk_points": risks}

        summary_parts = []
        if trends_data.get("macro_changes"):
            summary_parts.append(f"Market trend: {trends_data['macro_changes'][0]}")
        if opportunities:
            summary_parts.append(f"Key opportunity: {opportunities[0]}")
        if risks:
            summary_parts.append(f"Key risk: {risks[0]}")

        summary_statement = ". ".join(summary_parts) + "." if summary_parts else f"A high-level analysis of {self.topic} was conducted."

        final_report_structure = {
            "executive_summary": summary_statement,
            "trends_analysis": trends_data,
            "public_opinion": public_opinion_data,
            "competitive_landscape": competition_data,
            "news_and_policy": news_data,
            "key_takeaways": key_takeaways
        }
        return json.dumps(final_report_structure, indent=2)
