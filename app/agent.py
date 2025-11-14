# app/agent.py
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
    filename='app/logs/agent.log',
    filemode='w'
)

def google_search(query):
    """A mock google search function."""
    logging.info(f"--- MOCK SEARCH: {query} ---")
    if "top companies" in query:
        return [{"url": "https://example.com/mock-data", "title": "TopCorp Example Inc.", "snippet": "TopCorp is a leader in the industry."}]
    return [{"url": "https://example.com/mock-data", "title": "Mock Search Result", "snippet": "This is a mock result for your query."}]

def view_text_website(url):
    """A mock website viewer."""
    logging.info(f"--- MOCK VIEW: {url} ---")
    return "Mock website content with keywords and analysis."

def mock_apify_scrape(topic):
    """A mock function to simulate scraping data with Apify."""
    logging.info(f"--- MOCK APIFY SCRAPE for '{topic}' ---")
    # Simulate finding user comments on different platforms
    return [
        {"platform": "Reddit", "comment": f"I love the new {topic}, the battery life is amazing!"},
        {"platform": "Twitter", "comment": f"Can't believe how expensive the new {topic} is."},
        {"platform": "Forum", "comment": f"Hoping they release a version of the {topic} with more color options."},
    ]

def mock_baidu_nlp_analysis(scraped_data):
    """A mock function to simulate NLP analysis with Baidu AI Cloud."""
    logging.info(f"--- MOCK BAIDU NLP ANALYSIS ---")
    # Simulate classifying sentiment and extracting themes
    analysis = {
        "sentiment_distribution": {"positive": 0, "negative": 0, "neutral": 0},
        "key_themes": [],
        "unmet_needs": []
    }
    for item in scraped_data:
        if "amazing" in item["comment"]:
            analysis["sentiment_distribution"]["positive"] += 1
            analysis["key_themes"].append("Battery Life")
        elif "expensive" in item["comment"]:
            analysis["sentiment_distribution"]["negative"] += 1
            analysis["key_themes"].append("Price")
        elif "options" in item["comment"]:
            analysis["sentiment_distribution"]["neutral"] += 1
            analysis["unmet_needs"].append("More customization")

    return analysis

def mock_tushare_financial_analysis(company_name, fail=False):
    """A mock function to simulate financial analysis with Tushare."""
    logging.info(f"--- MOCK TUSHARE ANALYSIS for '{company_name}' ---")
    if fail:
        return None # Simulate an API failure
    return {"company": company_name, "market_cap": "1 Trillion USD", "pe_ratio": 30}

def mock_fmp_financial_analysis(company_name):
    """A mock function to simulate fallback financial analysis with FMP."""
    logging.info(f"--- MOCK FMP FALLBACK ANALYSIS for '{company_name}' ---")
    return {"company": company_name, "stock_price": "$250", "dividend_yield": "1.5%"}

def mock_newsapi_search(topic):
    """A mock function to simulate searching for news with NewsAPI.org."""
    logging.info(f"--- MOCK NEWSAPI SEARCH for '{topic}' ---")
    return [
        {"source": "TechCrunch", "title": f"The Rise of {topic}", "summary": "A new report shows exponential growth in the {topic} sector."},
        {"source": "Wired", "title": f"New Regulations Impact {topic} Market", "summary": "Governments are introducing new policies that could reshape the industry."},
    ]

def mock_google_trends(topic):
    """A mock function to simulate getting trend data from Google Trends."""
    logging.info(f"--- MOCK GOOGLE TRENDS for '{topic}' ---")
    return {"rising_queries": [f"{topic} innovations", f"best {topic} 2025"], "interest_over_time": "High"}

class IntellectAgent:
    def __init__(self, topic):
        self.topic = topic
        self.report = {}
        self.status = "Idle"
        logging.info(f"IntellectAgent initialized for topic: {self.topic}")

    def run_analysis(self):
        logging.info("Starting analysis run...")
        self.status = "Starting analysis..."
        yield f"status: {self.status}"

        # Stage 1: Trend Analysis
        yield from self._analyze_trends()
        logging.info("Trend analysis stage complete.")

        # Stage 2: Public Opinion Mining
        yield from self._mine_public_opinion()
        logging.info("Public opinion stage complete.")

        # Stage 3: Competitive Landscape
        yield from self._analyze_competition()
        logging.info("Competitive landscape stage complete.")

        # Stage 4: News Analysis
        yield from self._analyze_news()
        logging.info("News analysis stage complete.")

        # Stage 5: Final Report Generation
        self.status = "Compiling final report..."
        yield f"status: {self.status}"
        final_report_str = self._generate_report()
        logging.info("Final report generated.")

        self.status = "Analysis complete."
        yield f"final_update: {json.dumps({'status': self.status, 'report': final_report_str})}"
        logging.info("Analysis run finished.")

    def _analyze_trends(self):
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
                summary["trending_keywords"].extend(rising_queries.to_frame().head()['query'].values.tolist())
        except Exception as e:
            logging.error(f"Pytrends API call failed: {e}")
            summary["macro_changes"].append("Google Trends API call failed.")

        self.report['trend_analysis'] = summary
        yield f"status: Trend analysis complete."

    def _mine_public_opinion(self):
        yield f"status: Scraping public opinion data for '{self.topic}' with Apify..."
        summary = {"high_frequency_topics": [], "core_pain_points": [], "unmet_needs": [], "sentiment": {}}
        try:
            apify_client = ApifyClient(config.APIFY_API_KEY)
            # This is a placeholder for a real Apify actor run
            # In a real scenario, you would trigger an actor and wait for its results
            # For now, we will use a small, static dataset to simulate the output
            scraped_data = [{"text": f"The new {self.topic} is revolutionary!"}, {"text": f"I am disappointed with the high price of the {self.topic}."}]

            yield f"status: Analyzing sentiment with Baidu AI Cloud..."
            client = AipNlp(config.BAIDU_APP_ID, config.BAIDU_API_KEY, config.BAIDU_SECRET_KEY)

            sentiments = []
            for item in scraped_data:
                # Baidu NLP API has rate limits, so process a small sample
                result = client.sentimentClassify(item['text'])
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

    def _analyze_competition(self):
        yield f"status: Identifying top competitors for '{self.topic}'..."
        # This is a placeholder for a more sophisticated competitor discovery mechanism
        competitors = [{"name": "Apple", "symbol": "AAPL"}, {"name": "Samsung", "symbol": "005930.KS"}]
        summary = {"financial_profiles": [], "market_position": []}

        ts.set_token(config.TUSHARE_API_KEY)
        pro = ts.pro_api()

        for competitor in competitors:
            financial_data = None
            try:
                yield f"status: Analyzing '{competitor['name']}' with Tushare..."
                # Tushare may require a different API call for non-Chinese stocks
                df = pro.daily(ts_code=competitor['symbol'], start_date='20230101', end_date='20230110')
                if not df.empty:
                    financial_data = df.to_dict('records')
            except Exception as e:
                logging.error(f"Tushare API call failed for {competitor['name']}: {e}")

            if financial_data:
                summary["financial_profiles"].append({competitor['name']: financial_data})
            else:
                yield f"status: Adapting: Tushare failed for '{competitor['name']}'. Trying FMP..."
                try:
                    fmp_client = FMPClient(api_key=config.FMP_API_KEY)
                    quote = fmp_client.quote(competitor['symbol'])
                    if quote:
                        summary["financial_profiles"].append({competitor['name']: quote})
                except Exception as fmp_e:
                    logging.error(f"FMP API call failed for {competitor['name']}: {fmp_e}")
                    summary["financial_profiles"].append({"company": competitor['name'], "error": "All financial data sources failed."})

        self.report['competitive_landscape'] = summary
        yield f"status: Competitive landscape analysis complete."

    def _analyze_news(self):
        yield f"status: Analyzing news & policy for '{self.topic}' with NewsAPI.org..."
        summary = {"major_events": [], "policy_changes": []}
        try:
            newsapi = NewsApiClient(api_key=config.NEWS_API_KEY)
            all_articles = newsapi.get_everything(q=self.topic,
                                                  language='en',
                                                  sort_by='relevancy')

            for article in all_articles['articles']:
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
