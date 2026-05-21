import os
import json


class OpenAIService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.client = None
        self._init_client()

    def _init_client(self):
        if not self.api_key:
            return
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        except Exception:
            self.client = None

    def is_configured(self) -> bool:
        return bool(self.api_key and self.client)

    def _call(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return response.choices[0].message.content

    def _parse_json(self, raw: str) -> dict:
        text = raw.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            return {
                "error": f"JSON parse error: {e}",
                "raw_output": raw[:500],
                "suggested_next_step": "Try re-running generation. The model may have returned malformed output.",
            }

    def generate_campaign_content(self, topic: str, campaign_name: str = "",
                                   product_desc: str = "", target_audience: str = "",
                                   goal: str = "", tone: str = "professional",
                                   channels: list = None, cta: str = "",
                                   constraints: str = "") -> dict:
        if not self.is_configured():
            return {"error": "OpenAI API key not configured"}

        channels_str = ", ".join(channels) if channels else "Email, Newsletter, Blog"
        include_linkedin = "LinkedIn" in (channels or [])
        include_email = "Email" in (channels or [])

        context_parts = []
        if campaign_name:
            context_parts.append(f"Campaign name: {campaign_name}")
        if product_desc:
            context_parts.append(f"Product/company: {product_desc}")
        if target_audience:
            context_parts.append(f"Target audience: {target_audience}")
        if goal:
            context_parts.append(f"Goal: {goal}")
        if tone:
            context_parts.append(f"Tone: {tone}")
        if cta:
            context_parts.append(f"CTA: {cta}")
        if constraints:
            context_parts.append(f"Constraints: {constraints}")
        context_str = "\n".join(context_parts)

        linkedin_instruction = ""
        email_instruction = ""
        linkedin_key = ""
        email_key = ""

        if include_linkedin:
            linkedin_key = '- "linkedin_posts": object with persona keys — each a 150-200 word LinkedIn post (professional, insight-led, ends with a question or hook)'
            linkedin_instruction = "LinkedIn posts: professional, first-person, insight-led, no hashtag spam, end with an open question."
        if include_email:
            email_key = '- "email_bodies": object with persona keys — each a 100-150 word outbound cold email body (direct, specific, one CTA at end, use [First Name] placeholder)'
            email_instruction = "Email bodies: concise, direct, one pain point, one offer, one CTA. No fluff."

        prompt = f"""You are writing marketing content for NovaMind, an AI startup helping small creative agencies automate daily workflows.

Topic: {topic}
Channels: {channels_str}
{context_str}

Target personas:
1. Agency Founder
2. Operations Manager
3. Creative Lead
4. Account / Client Services Lead
5. Strategy / Marketing Lead

Generate a JSON object with these keys:
- "blog_title": string
- "blog_outline": array of 5 concise bullet strings
- "blog_draft": string (400-600 words, practical, grounded in real agency workflow problems)
- "newsletters": object with persona keys — each a 220-300 word newsletter (cohesive mini-essay: pain point, how AI helps, why it matters, one takeaway)
- "subject_lines": object with persona keys — each a compelling subject line
- "ab_test_ideas": array of 2 A/B test suggestions
- "persona_rationale": object with persona keys — each a 1-sentence rationale
{linkedin_key}
{email_key}

Newsletter persona focus:
- Founder: growth, margins, scalability
- Ops Manager: workflows, approvals, efficiency
- Creative Lead: protecting creative time, reducing admin drag
- Account Lead: client communication, responsiveness, delivery visibility
- Strategy Lead: planning leverage, campaign execution, strategic time

{linkedin_instruction}
{email_instruction}

Return valid JSON only. Do not include markdown fences."""

        try:
            raw = self._call(prompt)
            return self._parse_json(raw)
        except Exception as e:
            return {
                "error": _safe_error(e),
                "raw_output": "",
                "suggested_next_step": "Check your API key and model name, then try again.",
            }

    def regenerate_section(self, section_type: str, topic: str, persona: str = "",
                           tone: str = "professional", cta: str = "", context: str = "") -> str:
        if not self.is_configured():
            return ""

        prompts = {
            "newsletter": f"""Write a 220-300 word newsletter for the {persona} persona about: {topic}
Tone: {tone}
{f'CTA hint: {cta}' if cta else ''}
{context}
Structure: pain point → how AI helps → why it matters → one practical takeaway.
Write as a cohesive mini-essay (3-4 paragraphs). Return only the newsletter text.""",

            "linkedin_post": f"""Write a 150-200 word LinkedIn post for the {persona} persona about: {topic}
Tone: {tone}
Rules: professional, first-person, insight-led, no hashtag spam, end with an open question.
Return only the post text.""",

            "email_body": f"""Write a 100-150 word outbound cold email body for the {persona} persona about: {topic}
Tone: {tone}
{f'CTA: {cta}' if cta else 'End with a clear next-step CTA.'}
Rules: direct, one pain point, one offer, [First Name] placeholder at start. No fluff.
Return only the email body text.""",

            "blog_draft": f"""Write a 400-600 word blog post about: {topic}
Tone: {tone}
{context}
Rules: practical, modern, specific to creative agency workflow problems.
Return only the blog text.""",
        }

        prompt = prompts.get(section_type, prompts["newsletter"])
        try:
            return self._call(prompt)
        except Exception as e:
            return f"Regeneration failed: {_safe_error(e)}"

    def ideate_campaign_topics(self, business_context: str = "") -> dict:
        if not self.is_configured():
            return {"error": "OpenAI API key not configured"}

        prompt = f"""You are a growth content strategist for NovaMind, an AI startup helping small creative agencies automate workflows.
{f'Business context: {business_context}' if business_context else ''}

Return a valid JSON object:
{{
  "topic_options": [
    {{"topic": "...", "target_persona": "...", "angle": "...", "why_this_is_promising": "..."}},
    {{"topic": "...", "target_persona": "...", "angle": "...", "why_this_is_promising": "..."}},
    {{"topic": "...", "target_persona": "...", "angle": "...", "why_this_is_promising": "..."}}
  ]
}}

Give exactly 3 meaningfully different options. Return valid JSON only."""

        try:
            raw = self._call(prompt)
            return self._parse_json(raw)
        except Exception as e:
            return {"error": _safe_error(e)}

    def generate_performance_summary(self, metrics_text: str) -> str:
        if not self.is_configured():
            return "OpenAI not configured — cannot generate AI summary."
        prompt = f"""You are a growth analyst for NovaMind.

Newsletter performance by persona:
{metrics_text}

Write a short performance summary in 5-7 sentences. Be specific: identify the strongest persona, explain what worked, what underperformed, and recommend one improvement. Keep it concise and practical."""
        try:
            return self._call(prompt)
        except Exception as e:
            return f"Could not generate summary: {_safe_error(e)}"

    def generate_optimization_recommendations(self, metrics_text: str) -> dict:
        if not self.is_configured():
            return {"error": "OpenAI not configured"}
        prompt = f"""You are a growth analyst for NovaMind.

Campaign performance data by persona:
{metrics_text}

Return a valid JSON object with:
- "next_blog_topics": array of 3 topic ideas
- "best_persona_to_prioritize": string
- "subject_line_tests": object with persona keys, each an array of 2-3 subject line variants
- "newsletter_improvements": object with persona keys, each a 1-2 sentence improvement suggestion

Base all recommendations on the data. Be practical. Return valid JSON only."""
        try:
            raw = self._call(prompt)
            return self._parse_json(raw)
        except Exception as e:
            return {"error": _safe_error(e)}


def _safe_error(e: Exception) -> str:
    msg = str(e)
    for kw in ["key", "token", "secret", "auth", "bearer", "sk-"]:
        if kw in msg.lower():
            return "Authentication failed. Check that your API key is valid and has not expired."
    error_map = {
        "RateLimitError": "Rate limit reached. Please wait a moment and try again.",
        "AuthenticationError": "Invalid API key. Check your OPENAI_API_KEY secret.",
        "APIConnectionError": "Could not connect to OpenAI. Check your internet connection.",
        "InvalidRequestError": "Invalid request. Try a different model name.",
    }
    for key, friendly in error_map.items():
        if key in type(e).__name__:
            return friendly
    return "An unexpected error occurred. Please try again."
