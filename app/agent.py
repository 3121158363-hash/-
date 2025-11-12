import json
try:
    from tools import google_search, view_text_website
except ImportError:
    def google_search(query):
        print(f"--- MOCK SEARCH: {query} ---")
        return [{"url": "https://example.com/mock-data", "title": "Mock Search Result", "snippet": "This is a mock result."}]
    def view_text_website(url):
        print(f"--- MOCK VIEW: {url} ---")
        return "Mock website content with keywords and analysis."

class IntellectAgent:
    def __init__(self, topic):
        self.topic = topic
        self.report = {}
        self.status = "Idle"

    def run_analysis(self):
        self.status = "Starting analysis..."
        yield f"status: {self.status}"

        # Stage 1: Trend Analysis with Adaptation
        yield from self._execute_and_adapt(
            primary_method=self._analyze_trends,
            fallback_method=self._analyze_trends_fallback,
            report_key='trend_analysis'
        )

        # Stage 2: Public Opinion Mining
        self.status = "Assessing public opinion data sources..."
        yield f"status: {self.status}"

        needs_plugin = self._assess_public_opinion_data()
        if needs_plugin:
            yield "authorization_required: Public Opinion Miner Plugin"

        self.status = "Analyzing public opinion..."
        yield f"status: {self.status}"
        yield from self._mine_public_opinion()

        # Stage 3: Competitive Landscape with Adaptation
        yield from self._execute_and_adapt(
            primary_method=self._analyze_competition,
            fallback_method=self._analyze_competition_fallback,
            report_key='competitive_landscape'
        )

        # Stage 4: Final Report Generation
        self.status = "Compiling final report..."
        yield f"status: {self.status}"
        final_report_str = self._generate_report()

        self.status = "Analysis complete."
        yield f"final_update: {json.dumps({'status': self.status, 'report': final_report_str})}"

    def _analyze_trends(self):
        """
        Simulates querying structured data sources for trend analysis. This is a generator.
        """
        yield f"status: Querying simulated Trend Analysis APIs for '{self.topic}'..."
        summary = {
            "macro_changes": [],
            "trending_keywords": []
        }

        # Simulate querying a Google Trends API
        trends_api_query = f"structured Google Trends data for {self.topic}"
        trends_results = google_search(query=trends_api_query)

        if trends_results:
            simulated_api_response = {
                "trend_slope": "rising",
                "related_queries": ["innovation in " + self.topic, self.topic + " regulation"]
            }
            if simulated_api_response["trend_slope"] == "rising":
                summary["macro_changes"].append(f"Data indicates a significant rising interest in '{self.topic}'.")
            summary["trending_keywords"].extend(simulated_api_response["related_queries"])

        # Simulate querying a News Analysis API for expert opinions
        news_api_query = f"expert analysis and market reports for {self.topic}"
        news_results = google_search(query=news_api_query)

        if news_results:
            simulated_news_response = {
                "key_findings": [
                    f"Market growth is projected to be strong, driven by new technology.",
                    f"Policy changes are expected to impact the industry."
                ]
            }
            summary["macro_changes"].extend(simulated_news_response["key_findings"])

        self.report['trend_analysis'] = summary
        yield f"status: Trend analysis complete."


    def _assess_public_opinion_data(self):
        """
        Performs a preliminary search to see if basic public opinion data can be found.
        If not, it recommends using the specialized plugin.
        """
        query = f'site:reddit.com "{self.topic}" "review" OR "opinions"'
        preliminary_results = google_search(query=query)

        if not preliminary_results:
            return True
        return False

    def _mine_public_opinion(self):
        """
        Prepares the input for the Public Opinion Miner Plugin and
        is designed to process its output.
        """
        # 1. Define the plugin's input structure
        plugin_input = {
            "topic": self.topic,
            "target_sites": ["reddit.com", "bilibili.com"]
        }

        # 2. In a real system, we would yield this and wait for the orchestrator
        # to call the external plugin. For now, we'll simulate the plugin's output.
        yield f"status: Preparing data for Public Opinion Miner Plugin..."

        # 3. Simulate the output that the external plugin would provide.
        simulated_plugin_output = {
            "high_frequency_topics": ["Community Feature Requests", "Performance Complaints"],
            "core_pain_points": ["Frequent crashes on new hardware.", "High cost of entry."],
            "unmet_needs": ["Users are requesting a more beginner-friendly tutorial.", "Demand for cross-platform play."]
        }

        # 4. Process the plugin's output
        self.report['public_opinion'] = simulated_plugin_output
        yield f"status: Public opinion analysis complete."

    def _analyze_competition(self):
        """
        Simulates querying a financial data API to identify top players and their products,
        and then finds negative intelligence. This is a generator.
        """
        yield f"status: Querying simulated Financial Data APIs for '{self.topic}'..."
        summary = {
            "top_players_and_products": [],
            "negative_intelligence": []
        }

        # Simulate a call to a Financial Data API
        financial_api_query = f"financial data and market share for {self.topic}"
        financial_results = google_search(query=financial_api_query)

        top_players = []
        if financial_results:
            simulated_financial_response = {
                "market_leaders": [
                    {"company": "FutureTech", "market_share": 0.35, "main_product": "FutureOne"},
                    {"company": "InnovateCorp", "market_share": 0.28, "main_product": "InnoPad"}
                ]
            }

            for leader in simulated_financial_response["market_leaders"]:
                market_share_percent = leader['market_share'] * 100
                summary["top_players_and_products"].append(
                    f"{leader['company']} (Product: {leader['main_product']}, Market Share: {market_share_percent:.1f}%)"
                )
                top_players.append(leader['company'])

        # Find negative sentiment for the identified top players
        for player in top_players:
            negative_query = f'"{player}" "{self.topic}" "complaints" OR "issues"'
            negative_results = google_search(query=negative_query)
            if negative_results:
                summary["negative_intelligence"].append(f"{player}: {negative_results[0]['snippet']}")

        self.report['competitive_landscape'] = summary
        yield f"status: Competitive landscape analysis complete."

    def _analyze_trends_fallback(self):
        """Fallback if primary trend analysis fails."""
        fallback_summary = {
            "macro_changes": ["Primary trend data source failed. Found general market discussion instead."],
            "trending_keywords": []
        }
        query = f'"{self.topic}" "market discussion" OR "future of"'
        results = google_search(query=query)
        if results:
            fallback_summary["trending_keywords"].append(results[0]['snippet'])
        self.report['trend_analysis'] = fallback_summary

    def _analyze_competition_fallback(self):
        """Fallback if primary competition analysis fails."""
        fallback_summary = {
            "top_players_and_products": ["Primary competitor data source failed. Found general competitor mentions instead."],
            "negative_intelligence": []
        }
        query = f'"{self.topic}" "competitors" OR "vs"'
        results = google_search(query=query)
        if results:
            fallback_summary["negative_intelligence"].append(results[0]['snippet'])
        self.report['competitive_landscape'] = fallback_summary

    def _execute_and_adapt(self, primary_method, fallback_method, report_key):
        """
        Executes a primary data gathering method and runs a fallback if the result is empty.
        This is a generator that yields status updates.
        """
        yield from primary_method()

        result = self.report.get(report_key, {})
        # A result is considered "empty" if all its list values are empty.
        is_empty = not any(v for v in result.values() if isinstance(v, list) and v)

        if is_empty:
            yield f"status: Primary source for {report_key} returned no data. Adapting..."
            fallback_method()
            yield f"status: Fallback for {report_key} complete."

    def _generate_report(self):
        """
        Synthesizes all collected data into the final five-part report with an enhanced summary.
        """
        # --- 1. Key Takeaways (Derived from other sections) ---
        opportunities = self.report.get('public_opinion', {}).get('unmet_needs', [])
        risks = self.report.get('competitive_landscape', {}).get('negative_intelligence', [])
        key_takeaways = {
            "opportunity_points": opportunities,
            "risk_points": risks
        }

        # --- 2. Executive Summary (Generated last with more intelligence) ---
        summary_parts = []

        # Analyze trends for a headline
        trends = self.report.get('trend_analysis', {})
        if trends.get("macro_changes"):
            headline_trend = next((mc for mc in trends["macro_changes"] if "rising interest" in mc), trends["macro_changes"][0])
            summary_parts.append(f"The market for {self.topic} is showing '{headline_trend}'.")

        # Identify the most pressing opportunity
        if opportunities:
            summary_parts.append(f"A key market gap exists in addressing the need for '{opportunities[0]}'.")
        else:
            summary_parts.append("No specific unmet needs were identified, suggesting a mature or saturated market.")

        # Highlight a competitive threat
        if risks:
            summary_parts.append(f"Competitive pressure is notable, with reports of '{risks[0]}'.")

        summary_statement = " ".join(summary_parts)
        if not summary_statement:
            summary_statement = f"A high-level analysis of {self.topic} was conducted, but no strong conclusions could be drawn from the available data."

        # --- Assemble the final report object ---
        final_report_structure = {
            "executive_summary": summary_statement,
            "trends_analysis": trends,
            "public_opinion": self.report.get('public_opinion', {}),
            "competitive_landscape": self.report.get('competitive_landscape', {}),
            "key_takeaways": key_takeaways
        }

        return json.dumps(final_report_structure, indent=2)
