# app/agent.py
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
        yield f"status: Analyzing trends for '{self.topic}'..."
        summary = {"macro_changes": [], "trending_keywords": []}
        results = google_search(query=f"{self.topic} market trends")
        if results:
            summary["macro_changes"].append(results[0]['snippet'])
            summary["trending_keywords"].extend(["mock keyword 1", "mock keyword 2"])
        self.report['trend_analysis'] = summary
        yield f"status: Trend analysis complete."

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
            plugin_output = {"high_frequency_topics": ["Mock high-frequency topic."], "core_pain_points": ["Mock pain point."], "unmet_needs": ["Mock unmet need."]}

        self.report['public_opinion'] = plugin_output
        yield f"status: Public opinion analysis complete."

    def _analyze_competition(self):
        yield f"status: Analyzing competitive landscape for '{self.topic}'..."
        summary = {"top_players_and_products": [], "negative_intelligence": []}
        results = google_search(query=f"top companies in {self.topic}")
        if results:
            summary["top_players_and_products"].append(results[0]['title'])
            summary["negative_intelligence"].append("Mock negative intelligence.")
        self.report['competitive_landscape'] = summary
        yield f"status: Competitive landscape analysis complete."

    def _analyze_news(self):
        yield f"status: Analyzing news & policy for '{self.topic}'..."
        summary = {"major_events": [], "trends": []}
        results = google_search(query=f"{self.topic} industry news")
        if results:
            summary["major_events"].append(results[0]['snippet'])
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
