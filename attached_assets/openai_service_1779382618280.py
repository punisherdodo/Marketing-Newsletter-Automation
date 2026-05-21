import os
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI


class OpenAIService:
    def __init__(self):
        root = Path(__file__).resolve().parent.parent
        load_dotenv(root / ".env", override=True)

        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-5.4")

    def ideate_campaign_topics(self, business_context: str = "") -> dict:
        prompt = f"""
You are a growth content strategist for NovaMind, an early-stage AI startup that helps small creative agencies automate daily workflows.

Your job is to ideate campaign topics before content is generated.

Business context:
{business_context if business_context else "NovaMind wants to grow inbound traffic and newsletter conversions among small creative agencies."}

Return a valid JSON object with this structure:
{{
  "topic_options": [
    {{
      "topic": "...",
      "target_persona": "...",
      "angle": "...",
      "why_this_is_promising": "..."
    }},
    {{
      "topic": "...",
      "target_persona": "...",
      "angle": "...",
      "why_this_is_promising": "..."
    }},
    {{
      "topic": "...",
      "target_persona": "...",
      "angle": "...",
      "why_this_is_promising": "..."
    }}
  ]
}}

Rules:
- Give exactly 3 topic options
- The options should be meaningfully different
- Focus on realistic B2B content ideas for creative agencies
- Make each option specific enough to draft immediately
- Return valid JSON only
"""

        response = self.client.responses.create(
            model=self.model,
            input=prompt
        )

        return json.loads(response.output_text)

    def generate_campaign_content(self, topic: str) -> dict:
        prompt = f"""
You are writing for NovaMind, an early-stage AI startup that helps small creative agencies automate daily workflows.

Target personas:
1. Agency Founder
2. Operations Manager
3. Creative Lead
4. Account / Client Services Lead
5. Strategy / Marketing Lead

Task:
Generate a JSON object with these keys:
- blog_title
- blog_outline (array of 5 concise bullets)
- blog_draft (400 to 600 words)
- newsletters (object with keys "Agency Founder", "Operations Manager", "Creative Lead", "Account / Client Services Lead", "Strategy / Marketing Lead")

### Blog writing rules
- The blog should be practical, modern, and clear
- The blog should stay grounded in real agency workflow problems
- The tone should be useful and specific, not generic or overly promotional

### Newsletter writing rules
- The 5 newsletters should each be 220 to 300 words
- Each newsletter should read like one cohesive mini-essay, not separate blocks stitched together
- Each newsletter should still naturally cover:
  - the core pain point
  - how AI helps
  - why it matters for that persona
  - one practical starting point or takeaway
- Use 3 to 4 paragraphs
- Keep the tone practical, specific, and human

### Persona focus
- Founder version should focus on growth, margins, and scalability
- Operations Manager version should focus on workflows, approvals, and efficiency
- Creative Lead version should focus on protecting creative time and reducing admin drag
- Account / Client Services Lead should focus on client communication, responsiveness, and delivery visibility
- Strategy / Marketing Lead should focus on planning leverage, campaign execution, and better use of strategic time

### Output rules
- Return valid JSON only
- Do not include markdown fences

Topic: {topic}
"""

        response = self.client.responses.create(
            model=self.model,
            input=prompt
        )

        return json.loads(response.output_text)

    def generate_performance_summary(self, metrics_text: str) -> str:
        prompt = f"""
You are a growth analyst for NovaMind.

Below is newsletter performance by persona for one campaign.

{metrics_text}

Write a short performance summary in 5 to 7 sentences.

Rules:
- Be specific
- Identify the strongest persona
- Explain what likely worked
- Explain what underperformed
- Recommend one improvement for the next campaign
- Keep it concise and practical
"""

        response = self.client.responses.create(
            model=self.model,
            input=prompt
        )

        return response.output_text

    def generate_optimization_recommendations(self, metrics_text: str) -> dict:
        prompt = f"""
You are a growth analyst for NovaMind.

Here is campaign performance data by persona:

{metrics_text}

Task:
Return a valid JSON object with these keys:
- next_blog_topics: array of 3 topic ideas
- best_persona_to_prioritize: string
- subject_line_tests: object with keys "Agency Founder", "Operations Manager", "Creative Lead", "Account / Client Services Lead", "Strategy / Marketing Lead"
- newsletter_improvements: object with keys "Agency Founder", "Operations Manager", "Creative Lead", "Account / Client Services Lead", "Strategy / Marketing Lead"

Rules:
- Base recommendations on the performance data
- Prioritize what is likely to improve click rate without increasing unsubscribe rate
- Be practical, not generic
- Keep each suggestion concise
- Return valid JSON only
"""

        response = self.client.responses.create(
            model=self.model,
            input=prompt
        )

        return json.loads(response.output_text)

    def generate_next_campaign_options(self, performance_summary: str) -> dict:
        prompt = f"""
You are planning the next NovaMind campaign.

Use this performance summary:
{performance_summary}

Return a valid JSON object with this structure:
{{
  "option_1": {{
    "topic": "...",
    "angle": "...",
    "why_this_now": "..."
  }},
  "option_2": {{
    "topic": "...",
    "angle": "...",
    "why_this_now": "..."
  }},
  "option_3": {{
    "topic": "...",
    "angle": "...",
    "why_this_now": "..."
  }}
}}

Rules:
- The 3 options should be meaningfully different
- Each option should feel like a realistic next campaign
- Keep each field concise
- Return valid JSON only
"""

        response = self.client.responses.create(
            model=self.model,
            input=prompt
        )

        return json.loads(response.output_text)
