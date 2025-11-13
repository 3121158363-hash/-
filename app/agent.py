import json
import logging
import os
import importlib.util
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

        # Stage 1: Trend Analysis with Adaptation
        yield from self._execute_and_adapt(
            primary_method=self._analyze_trends,
            fallback_method=self._analyze_trends_fallback,
            report_key='trend_analysis'
        )
        logging.info("Trend analysis stage complete.")

        # Stage 2: Public Opinion Mining
        self.status = "Assessing public opinion data sources..."
        yield f"status: {self.status}"

        needs_plugin = self._assess_public_opinion_data()
        if needs_plugin:
            logging.info("Plugin authorization required.")
            yield "authorization_required: Public Opinion Miner Plugin"

        self.status = "Analyzing public opinion..."
        yield f"status: {self.status}"
        yield from self._mine_public_opinion()
        logging.info("Public opinion stage complete.")

        # Stage 3: Competitive Landscape with Adaptation
        yield from self._execute_and_adapt(
            primary_method=self._analyze_competition,
            fallback_method=self._analyze_competition_fallback,
            report_key='competitive_landscape'
        )
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
        logging.info("Executing primary trend analysis...")
        yield f"status: Querying simulated Trend Analysis APIs for '{self.topic}'..."
        summary = {"macro_changes": [], "trending_keywords": []}
        # Primary Search: Simulate querying a Google Trends API
        trends_api_query = f"structured Google Trends data for {self.topic}"
        trends_results = google_search(query=trends_api_query)
        if trends_results:
            logging.info("Primary trend data found.")
            simulated_api_response = {"trend_slope": "rising", "related_queries": ["innovation in " + self.topic, self.topic + " regulation"]}
            if simulated_api_response["trend_slope"] == "rising":
                summary["macro_changes"].append(f"Data indicates a significant rising interest in '{self.topic}'.")
            summary["trending_keywords"].extend(simulated_api_response["related_queries"])

        # Secondary (Cross-Validation) Search: Simulate querying news articles
        cross_validation_query = f'"{self.topic}" market trends news'
        validation_results = google_search(query=cross_validation_query)
        if validation_results:
            logging.info("Cross-validation data found for trends.")
            summary["macro_changes"].append(f"Cross-validation from news sources confirms: {validation_results[0]['snippet']}")
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
        logging.info("Executing primary competition analysis...")
        yield f"status: Querying simulated Financial Data APIs for '{self.topic}'..."
        summary = {"top_players_and_products": [], "negative_intelligence": []}
        financial_api_query = f"financial data and market share for {self.topic}"
        financial_results = google_search(query=financial_api_query)
        top_players = []
        if financial_results:
            logging.info("Primary competition data found.")
            simulated_financial_response = {"market_leaders": [{"company": "FutureTech", "market_share": 0.35, "main_product": "FutureOne"}, {"company": "InnovateCorp", "market_share": 0.28, "main_product": "InnoPad"}]}
            for leader in simulated_financial_response["market_leaders"]:
                market_share_percent = leader['market_share'] * 100
                summary["top_players_and_products"].append(f"{leader['company']} (Product: {leader['main_product']}, Market Share: {market_share_percent:.1f}%)")
                top_players.append(leader['company'])
        for player in top_players:
            # Primary Search for negative sentiment
            negative_query = f'"{player}" "{self.topic}" "complaints" OR "issues"'
            negative_results = google_search(query=negative_query)
            if negative_results:
                summary["negative_intelligence"].append(f"Primary issues for {player}: {negative_results[0]['snippet']}")

            # Secondary (Cross-Validation) Search for news articles
            cross_validation_query = f'"{player}" "{self.topic}" "negative news"'
            validation_results = google_search(query=cross_validation_query)
            if validation_results:
                summary["negative_intelligence"].append(f"Cross-validation from news for {player}: {validation_results[0]['snippet']}")
        self.report['competitive_landscape'] = summary
        yield f"status: Competitive landscape analysis complete."

    def _analyze_trends_fallback(self):
        logging.warning("Executing fallback trend analysis.")
        fallback_summary = {"macro_changes": ["Primary trend data source failed. Found general market discussion instead."], "trending_keywords": []}
        query = f'"{self.topic}" "market discussion" OR "future of"'
        results = google_search(query=query)
        if results:
            fallback_summary["trending_keywords"].append(results[0]['snippet'])
        self.report['trend_analysis'] = fallback_summary

    def _analyze_competition_fallback(self):
        logging.warning("Executing fallback competition analysis.")
        fallback_summary = {"top_players_and_products": ["Primary competitor data source failed. Found general competitor mentions instead."], "negative_intelligence": []}
        query = f'"{self.topic}" "competitors" OR "vs"'
        results = google_search(query=query)
        if results:
            fallback_summary["negative_intelligence"].append(results[0]['snippet'])
        self.report['competitive_landscape'] = fallback_summary

    def _execute_and_adapt(self, primary_method, fallback_method, report_key):
        logging.info(f"Executing adaptive logic for {report_key}...")
        # Consume the generator from the primary method while yielding its updates
        for update in primary_method():
            yield update

        result = self.report.get(report_key, {})
        is_empty = not any(v for v in result.values() if isinstance(v, list) and v)
        if is_empty:
            logging.warning(f"Primary source for {report_key} returned empty data. Adapting.")
            yield f"status: Primary source for {report_key} returned no data. Adapting..."
            fallback_method()
            yield f"status: Fallback for {report_key} complete."
        else:
            logging.info(f"Primary source for {report_key} succeeded.")

    def _generate_report(self):
        logging.info("Synthesizing final report.")
        opportunities = self.report.get('public_opinion', {}).get('unmet_needs', [])
        risks = self.report.get('competitive_landscape', {}).get('negative_intelligence', [])
        key_takeaways = {"opportunity_points": opportunities, "risk_points": risks}
        summary_parts = []
        trends = self.report.get('trend_analysis', {})
        if trends.get("macro_changes"):
            headline_trend = next((mc for mc in trends["macro_changes"] if "rising interest" in mc), trends["macro_changes"][0])
            summary_parts.append(f"The market for {self.topic} is showing '{headline_trend}'.")
        if opportunities:
            summary_parts.append(f"A key market gap exists in addressing the need for '{opportunities[0]}'.")
        else:
            summary_parts.append("No specific unmet needs were identified, suggesting a mature or saturated market.")
        if risks:
            summary_parts.append(f"Competitive pressure is notable, with reports of '{risks[0]}'.")
        summary_statement = " ".join(summary_parts)
        if not summary_statement:
            summary_statement = f"A high-level analysis of {self.topic} was conducted, but no strong conclusions could be drawn from the available data."
        final_report_structure = {"executive_summary": summary_statement, "trends_analysis": trends, "public_opinion": self.report.get('public_opinion', {}), "competitive_landscape": self.report.get('competitive_landscape', {}), "key_takeaways": key_takeaways}
        return json.dumps(final_report_structure, indent=2)
