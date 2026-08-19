from __future__ import annotations

from html import escape
from typing import Any


def render_website_html(result: dict[str, Any], prompt: str) -> str:
    title = escape(str(result.get("title") or "Generated Website"))
    safe_prompt = escape(prompt.strip() or "A focused David AI website brief.")
    sections = result.get("sections") if isinstance(result.get("sections"), list) else []
    rendered_sections: list[str] = []
    for index, section in enumerate(sections):
        if not isinstance(section, dict):
            continue
        component = escape(str(section.get("component_type") or "section"))
        heading = escape(str(section.get("title") or component.title()))
        subtitle = escape(str(section.get("subtitle") or ""))
        body = escape(str(section.get("body") or ""))
        buttons = section.get("buttons") if isinstance(section.get("buttons"), list) else []
        button_markup = "".join(
            f'<a class="button" href="#contact">{escape(str(button))}</a>'
            for button in buttons[:3]
            if str(button).strip()
        )
        rendered_sections.append(
            f'<section class="section section-{index % 2}">'
            f'<div class="section-kicker">{component.upper()}</div>'
            f'<h2>{heading}</h2><p class="section-subtitle">{subtitle}</p>'
            f'<p class="section-body">{body}</p>{button_markup}</section>'
        )
    if not rendered_sections:
        rendered_sections.append('<section class="section"><h2>David is ready to shape the next page.</h2><p class="section-body">Describe the audience, offer, and outcome you want to create.</p></section>')
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{ color-scheme: dark; font-family: Inter, ui-sans-serif, system-ui, sans-serif; background:#050912; color:#e9fbff; }}
    * {{ box-sizing:border-box; }} body {{ margin:0; background:radial-gradient(circle at 72% 8%, #123047 0%, #050912 42%, #020407 100%); }}
    .site {{ min-height:100vh; overflow:hidden; }} .nav {{ display:flex; justify-content:space-between; align-items:center; padding:28px 7vw; border-bottom:1px solid rgba(150,230,255,.12); }}
    .brand {{ letter-spacing:.28em; font-size:12px; color:#76efff; font-weight:700; }} .nav-links {{ display:flex; gap:22px; color:#8da6b4; font-size:12px; }}
    .hero {{ padding:13vh 7vw 10vh; max-width:1000px; }} .eyebrow,.section-kicker {{ color:#6deaff; letter-spacing:.28em; font-size:11px; font-weight:700; }} h1 {{ max-width:820px; font-size:clamp(44px,8vw,96px); line-height:.95; margin:18px 0 24px; letter-spacing:-.07em; }}
    .hero p {{ max-width:650px; color:#a7bdc7; font-size:18px; line-height:1.7; }} .hero .button {{ margin-top:18px; }} .section {{ padding:82px 7vw; border-top:1px solid rgba(150,230,255,.12); max-width:1100px; }}
    .section-1 {{ margin-left:auto; background:linear-gradient(90deg,transparent,rgba(23,90,113,.11)); }} h2 {{ font-size:clamp(28px,4vw,54px); margin:12px 0; letter-spacing:-.04em; }}
    .section-subtitle {{ color:#d5f4f7; font-size:18px; }} .section-body {{ color:#90aab5; line-height:1.8; max-width:720px; }} .button {{ display:inline-flex; align-items:center; justify-content:center; margin:10px 10px 0 0; padding:12px 18px; border-radius:999px; color:#031018; background:#76efff; text-decoration:none; font-weight:700; font-size:13px; }}
    .footer {{ padding:42px 7vw; color:#6d8791; font-size:12px; border-top:1px solid rgba(150,230,255,.12); }}
  </style>
</head>
<body><main class="site"><nav class="nav"><div class="brand">DAVID AI</div><div class="nav-links"><span>Product</span><span>Systems</span><span>Contact</span></div></nav>
<section class="hero"><div class="eyebrow">DAVID AI / GENERATED EXPERIENCE</div><h1>{title}</h1><p>{safe_prompt}</p><a class="button" href="#contact">Explore the system</a></section>
{''.join(rendered_sections)}<footer class="footer" id="contact">Generated with David AI. Review, refine, and publish when ready.</footer></main></body></html>'''
