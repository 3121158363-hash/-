import json

def run_opinion_miner(plugin_input):
    """
    This is a template for a Public Opinion Miner Plugin.

    It receives a JSON object with a "topic" and "target_sites",
    and it must return a JSON object with the specified structure.
    """
    topic = plugin_input.get("topic", "no topic provided")

    # In a real plugin, you would perform complex web scraping and NLP here.
    # For this template, we will return a hardcoded, structured response.

    plugin_output = {
        "high_frequency_topics": [f"Community discussions about {topic}", f"News articles covering {topic}"],
        "core_pain_points": [f"High cost associated with {topic}.", f"Lack of accessibility for {topic}."],
        "unmet_needs": [f"Users want a more affordable version of {topic}.", f"There is a demand for better documentation for {topic}."]
    }

    return plugin_output
