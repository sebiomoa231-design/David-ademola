from __future__ import annotations


class ContentEngine:
    """
    Reusable text-generation helpers for common content types. Each
    method returns a structured, ready-to-render draft. These are
    template-driven placeholders wired for a later swap to a real
    AI provider call via AIRouter, without changing method signatures.
    """

    def landing_page_copy(self, product_name: str, audience: str = "") -> dict:
        audience_line = f" for {audience}" if audience else ""
        return {
            "headline": f"{product_name}: built{audience_line}",
            "subheadline": f"Everything you need to get started with {product_name}, in one place.",
            "cta_primary": "Get Started",
            "cta_secondary": "Learn More",
        }

    def blog_post(self, topic: str) -> dict:
        return {
            "title": f"A guide to {topic}",
            "intro": f"Here's a practical look at {topic} and why it matters.",
            "sections": [
                f"What {topic} is",
                f"Why {topic} matters",
                f"How to get started with {topic}",
                "Common mistakes to avoid",
                "Summary",
            ],
        }

    def social_caption(self, topic: str, platform: str = "general") -> dict:
        return {
            "platform": platform,
            "caption": f"Exploring {topic} today — here's what stood out.",
            "hashtags": [f"#{topic.replace(' ', '')}", "#DavidAI"],
        }

    def marketing_email(self, subject_topic: str, offer: str = "") -> dict:
        offer_line = f" {offer}" if offer else ""
        return {
            "subject": f"{subject_topic} — you don't want to miss this",
            "preview_text": f"Quick update on {subject_topic}.{offer_line}",
            "body": (
                f"Hi there,\n\nWe wanted to share an update on {subject_topic}."
                f"{offer_line}\n\nTalk soon,\nThe team"
            ),
        }

    def product_description(self, product_name: str, key_benefit: str = "") -> dict:
        benefit_line = key_benefit or "solves a real problem for its users"
        return {
            "name": product_name,
            "short_description": f"{product_name} {benefit_line}.",
            "long_description": (
                f"{product_name} is designed to help you get more done with less "
                f"friction. It focuses on {benefit_line}, and is built to be simple, "
                "fast, and reliable."
            ),
        }

    def documentation_page(self, feature_name: str) -> dict:
        return {
            "title": feature_name,
            "sections": [
                {"heading": "Overview", "body": f"What {feature_name} does and when to use it."},
                {"heading": "Usage", "body": f"How to use {feature_name} step by step."},
                {"heading": "Examples", "body": f"Common examples using {feature_name}."},
                {"heading": "Troubleshooting", "body": "Common issues and how to resolve them."},
            ],
        }
