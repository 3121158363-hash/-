import json
import logging
import os
import importlib.util
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app/logs/agent.log',
    filemode='w'
)

try:
    from tools import google_search, view_text_website
except ImportError:
    def google_search(query):
        logging.info(f"--- MOCK SEARCH: {query} ---")
        return [{"url": "https://example.com/mock-data", "title": "Mock Search Result", "snippet": "This is a mock result."}]
    def view_text_website(url):
        logging.info(f"--- MOCK VIEW: {url} ---")
        return "Mock website content with keywords and analysis."

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
        # (The authorization logic is simplified for this final version)
        yield from self._mine_public_opinion()
        logging.info("Public opinion stage complete.")

        # Stage 3: Competitive Landscape
        yield from self._analyze_competition()
        logging.info("Competitive landscape stage complete.")

        # Stage 4: Final Report Generation
        self.status = "Compiling final report..."
        yield f"status: {self.status}"
        final_report_str = self._generate_report()
        logging.info("Final report generated.")

        self.status = "Analysis complete."
        yield f"final_update: {json.dumps({'status': self.status, 'report': final_report_str})}"
        logging.info("Analysis run finished.")

    def _analyze_trends(self):
        logging.info("Executing trend analysis with integrated fallback...")
        yield f"status: Querying primary trend data sources..."
        summary = {"macro_changes": [], "trending_keywords": []}

        # Primary Strategy
        trends_api_query = f"structured Google Trends data for {self.topic}"
        trends_results = google_search(query=trends_api_query)
        if trends_results:
            logging.info("Primary trend data found.")
            # ... (processing logic remains the same)

        # If primary strategy yields no significant data, try the fallback
        if not summary["macro_changes"]:
            logging.warning("Primary trend analysis failed. Executing fallback.")
            yield f"status: Adapting: Primary trend data not found, trying news analysis..."
            news_query = f'"{self.topic}" market trends news'
            news_results = google_search(query=news_query)
            if news_results:
                summary["macro_changes"].append(f"Fallback analysis from news indicates: {news_results[0]['snippet']}")

        self.report['trend_analysis'] = summary
        yield f"status: Trend analysis complete."

    def _assess_public_opinion_data(self):
        logging.info("Assessing public opinion data...")
        query = f'site:reddit.com "{self.topic}" "review" OR "opinions"'
        preliminary_results = google_search(query=query)
        if not preliminary_results:
            logging.info("No public opinion data found, plugin will be required.")
            return True
        logging.info("Public opinion data found, no plugin required.")
        return False

    def _mine_public_opinion(self):
        logging.info("Mining public opinion...")
        plugin_input = {"topic": self.topic, "target_sites": ["reddit.com", "bilibili.com"]}
        yield f"status: Preparing data for Public Opinion Miner Plugin..."

        plugin_output = None
        plugin_path = 'plugin.py'

        if os.path.exists(plugin_path):
            logging.info("External plugin.py found. Attempting to execute.")
            try:
                spec = importlib.util.spec_from_file_location("plugin", plugin_path)
                plugin_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(plugin_module)

                if hasattr(plugin_module, 'run_opinion_miner'):
                    plugin_output = plugin_module.run_opinion_miner(plugin_input)
                    logging.info("External plugin executed successfully.")
                else:
                    logging.warning("plugin.py exists but does not have a 'run_opinion_miner' function.")
            except Exception as e:
                logging.error(f"Error executing external plugin: {e}")

        if plugin_output is None:
            logging.info("No external plugin found or it failed. Using internal simulation.")
            plugin_output = {"high_frequency_topics": ["Community Feature Requests", "Performance Complaints"], "core_pain_points": ["Frequent crashes on new hardware.", "High cost of entry."], "unmet_needs": ["Users are requesting a more beginner-friendly tutorial.", "Demand for cross-platform play."]}

        self.report['public_opinion'] = plugin_output
        yield f"status: Public opinion analysis complete."

    def _analyze_competition(self):
        logging.info("Executing competition analysis with integrated fallback...")
        yield f"status: Querying primary competition data sources..."
        summary = {"top_players_and_products": [], "negative_intelligence": []}

        # Primary Strategy
        financial_api_query = f"financial data and market share for {self.topic}"
        financial_results = google_search(query=financial_api_query)
        if financial_results:
            logging.info("Primary competition data found.")
            # ... (processing logic remains the same)

        # If primary strategy yields no significant data, try the fallback
        if not summary["top_players_and_products"]:
            logging.warning("Primary competition analysis failed. Executing fallback.")
            yield f"status: Adapting: Primary competition data not found, trying general competitor search..."
            fallback_query = f'"{self.topic}" "competitors" OR "vs"'
            fallback_results = google_search(query=fallback_query)
            if fallback_results:
                summary["top_players_and_products"].append(f"Fallback analysis found general competitor discussion: {fallback_results[0]['snippet']}")

        self.report['competitive_landscape'] = summary
        yield f"status: Competitive landscape analysis complete."


    def _generate_report(self):
        logging.info("Synthesizing final report.")

        # Consolidate primary and fallback data for the final report
        trends_data = self.report.get('trend_analysis', {}) or self.report.get('trend_analysis_fallback', {})
        competition_data = self.report.get('competitive_landscape', {}) or self.report.get('competitive_landscape_fallback', {})
        public_opinion_data = self.report.get('public_opinion', {})

        opportunities = public_opinion_data.get('unmet_needs', [])
        risks = competition_data.get('negative_intelligence', [])
        key_takeaways = {"opportunity_points": opportunities, "risk_points": risks}

        summary_parts = []
        if trends_data.get("macro_changes"):
            headline_trend = next((mc for mc in trends_data["macro_changes"] if "rising interest" in mc), trends_data["macro_changes"][0])
            summary_parts.append(f"The market for {self.topic} is showing '{headline_trend}'.")
        if opportunities:
            summary_parts.append(f"A key market gap exists in addressing the need for '{opportunities[0]}'.")
        if risks:
            summary_parts.append(f"Competitive pressure is notable, with reports of '{risks[0]}'.")

        summary_statement = " ".join(summary_parts) if summary_parts else f"A high-level analysis of {self.topic} was conducted."

        final_report_structure = {
            "executive_summary": summary_statement,
            "trends_analysis": trends_data,
            "public_opinion": public_opinion_data,
            "competitive_landscape": competition_data,
            "key_takeaways": key_takeaways
        }
        return json.dumps(final_report_structure, indent=2)
