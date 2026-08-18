from __future__ import annotations

from dataclasses import dataclass, field

_SECTION_LIBRARY = {
    "hero": {
        "title": "A headline that says what you do",
        "subtitle": "One sentence explaining who it's for and why it matters.",
        "buttons": ["Get Started", "Learn More"],
    },
    "features": {
        "title": "Features",
        "subtitle": "What makes this worth using.",
        "buttons": [],
    },
    "pricing": {
        "title": "Pricing",
        "subtitle": "Simple, transparent plans.",
        "buttons": ["Choose Plan"],
    },
    "about": {
        "title": "About",
        "subtitle": "The story behind this project.",
        "buttons": [],
    },
    "services": {
        "title": "Services",
        "subtitle": "What we offer.",
        "buttons": ["Request a Quote"],
    },
    "portfolio": {
        "title": "Portfolio",
        "subtitle": "Recent work worth showing off.",
        "buttons": [],
    },
    "team": {
        "title": "Team",
        "subtitle": "The people behind the work.",
        "buttons": [],
    },
    "testimonials": {
        "title": "Testimonials",
        "subtitle": "What clients and users say.",
        "buttons": [],
    },
    "faq": {
        "title": "Frequently Asked Questions",
        "subtitle": "Answers to common questions.",
        "buttons": [],
    },
    "contact": {
        "title": "Contact",
        "subtitle": "Get in touch.",
        "buttons": ["Send Message"],
    },
    "footer": {
        "title": "Footer",
        "subtitle": "Links, legal, and social.",
        "buttons": [],
    },
}

_KEYWORD_TRIGGERS = {
    "restaurant": ["hero", "about", "services", "testimonials", "contact", "footer"],
    "portfolio": ["hero", "about", "portfolio", "testimonials", "contact", "footer"],
    "saas": ["hero", "features", "pricing", "faq", "contact", "footer"],
    "agency": ["hero", "services", "portfolio", "team", "testimonials", "contact", "footer"],
    "shop": ["hero", "features", "pricing", "testimonials", "faq", "contact", "footer"],
}

_DEFAULT_SECTIONS = ["hero", "features", "testimonials", "faq", "contact", "footer"]


@dataclass
class GeneratedSection:
    component_type: str
    title: str
    subtitle: str
    body: str
    buttons: list[str]
    image_placeholder: str
    layout: str = field(default="stacked")


class WebsiteEngine:
    """Produces structured page definitions from a natural-language prompt."""

    def generate(self, prompt: str) -> dict:
        prompt_lower = prompt.lower()
        section_keys = _DEFAULT_SECTIONS

        for keyword, sections in _KEYWORD_TRIGGERS.items():
            if keyword in prompt_lower:
                section_keys = sections
                break

        title = prompt.strip()[:40].strip().title() if prompt.strip() else "Generated Website"

        sections: list[GeneratedSection] = []
        for index, key in enumerate(section_keys):
            template = _SECTION_LIBRARY.get(key, _SECTION_LIBRARY["features"])
            sections.append(
                GeneratedSection(
                    component_type=key,
                    title=template["title"],
                    subtitle=template["subtitle"],
                    body=f"Auto-generated {key} content based on: {prompt.strip() or 'your prompt'}.",
                    buttons=list(template["buttons"]),
                    image_placeholder=f"/placeholders/{key}.png",
                    layout="alternating" if index % 2 else "stacked",
                )
            )

        notes = [
            "Use the David AI visual system (dark navy, cyan/blue accents, glass panels).",
            "Keep the layout responsive across mobile, tablet, and desktop.",
            "Sections are ordered top to bottom as generated.",
        ]

        return {
            "title": title,
            "sections": [s.__dict__ for s in sections],
            "notes": notes,
        }
