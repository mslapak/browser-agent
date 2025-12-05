# pyright: reportMissingImports=false
import asyncio
import os
import sys
from dataclasses import dataclass

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv

load_dotenv()

# Third-party imports
import gradio as gr  # type: ignore
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Local module imports
from browser_use import Agent, ChatOpenAI


@dataclass
class ActionResult:
    is_done: bool
    extracted_content: str | None
    error: str | None
    include_in_memory: bool


@dataclass
class AgentHistoryList:
    all_results: list[ActionResult]
    all_model_outputs: list[dict]


def parse_agent_history(history_str: str) -> None:
    console = Console()

    # Split the content into sections based on ActionResult entries
    sections = history_str.split("ActionResult(")

    for i, section in enumerate(sections[1:], 1):  # Skip first empty section
        # Extract relevant information
        content = ""
        if "extracted_content=" in section:
            content = section.split("extracted_content=")[1].split(",")[0].strip("'")

        if content:
            header = Text(f"Step {i}", style="bold blue")
            panel = Panel(content, title=header, border_style="blue")
            console.print(panel)
            console.print()

    return None


async def run_browser_task(
    task: str,
    api_key: str,
    model: str = "gpt-4.1-mini",
    headless: bool = True,
) -> str:
    if not api_key.strip():
        return "Please provide an API key"

    os.environ["OPENAI_API_KEY"] = api_key

    try:
        agent = Agent(
            task=task,
            llm=ChatOpenAI(model=model),
            # pokud budeš chtít používat headless, můžeš ho tady přidat,
            # když to Agent v této verzi podporuje, např.: headless=headless
        )
        result = await agent.run()
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"


def create_ui():
    with gr.Blocks(title="Browser Use GUI") as interface:
        gr.Markdown("# Browser Use Task Automation")

        with gr.Row():
            with gr.Column():
                api_key = gr.Textbox(
                    label="OpenAI API Key",
                    placeholder="sk-...",
                    type="password",
                )
                task = gr.Textbox(
                    label="Task Description",
                    placeholder="E.g., Find flights from New York to London for next week",
                    lines=3,
                )
                model = gr.Dropdown(
                    choices=["gpt-4.1-mini", "gpt-5", "o3", "gpt-5-mini"],
                    label="Model",
                    value="gpt-4.1-mini",
                )
                headless = gr.Checkbox(label="Run Headless", value=False)
                submit_btn = gr.Button("Run Task")

            with gr.Column():
                output = gr.Textbox(
                    label="Output",
                    lines=10,
                    interactive=False,
                )

        # přímo async funkce – Gradio si s ní poradí
        submit_btn.click(
            fn=run_browser_task,
            inputs=[task, api_key, model, headless],
            outputs=output,
        )

        return interface


if __name__ == "__main__":
    demo = create_ui()
    # Render (a podobné služby) nastaví PORT jako env proměnnou
    port = int(os.getenv("PORT", "7860"))
    demo.queue().launch(
        server_name="0.0.0.0",
        server_port=port,
    )
