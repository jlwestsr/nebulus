"""
title: Scheduler Dashboard
author: jlwestsr
author_url: https://github.com/jlwestsr/nebulus
funding_url: https://github.com/jlwestsr/nebulus
version: 0.1.0
"""

from pydantic import BaseModel, Field


class Tools:
    class Valves(BaseModel):
        dashboard_url: str = Field(
            default="http://host.docker.internal:8000/static/index.html",
            description="URL of the Scheduler Dashboard",
        )

    def __init__(self):
        pass

    async def open_scheduler_dashboard(
        self, __user__: dict, __event__: dict, __valves__: dict
    ) -> dict:
        """
        Opens the Scheduler Dashboard interface directly in the chat.
        :return: A dictionary containing the HTML response.
        """
        # Generate styles at runtime to avoid linter issues with literal semicolons
        d_styles = [
            "width: 100%",
            "height: 600px",
            "overflow: hidden",
            "border-radius: 10px",
            "border: 1px solid #333",
        ]
        d_style = "; ".join(d_styles)

        i_styles = ["width: 100%", "height: 100%", "border: none"]
        i_style = "; ".join(i_styles)

        html = (
            f'<div style="{d_style}">'
            f'<iframe src="{__valves__.dashboard_url}" '
            f'style="{i_style}" title="Scheduler Dashboard"></iframe>'
            f"</div>"
        )
        return {"type": "iframe", "content": html}

    async def get_dashboard_embed(self, __valves__: dict) -> str:
        """Helper to get raw HTML."""
        url = __valves__.dashboard_url
        return (
            f'<iframe src="{url}" width="100%" height="600px" frameborder="0"></iframe>'
        )
