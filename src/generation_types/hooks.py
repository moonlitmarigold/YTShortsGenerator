"""Universal prompt-rendering hooks for generation-type templates.

Each hook takes a prompt template string and a context dict, performs one
substitution, and returns the updated string. They are intentionally simple
so generation types can compose them in any order.
"""


def hook_metadata(prompt_text: str, context: dict) -> str:
    """Substitute every `{{key}}` placeholder with its context value."""
    for key, value in context.items():
        prompt_text = prompt_text.replace("{{" + key + "}}", str(value))
    return prompt_text


def hook_fonts(prompt_text: str, context: dict) -> str:
    """Inject the list of available fonts as a Markdown bullet list."""
    fonts = context.get("fonts", [])
    if fonts:
        fonts_block = "\n".join(f"- {font}" for font in fonts)
    else:
        fonts_block = "(no fonts configured yet - pick any reasonable font name)"
    return prompt_text.replace("{{available_fonts}}", fonts_block)


def hook_material_table(prompt_text: str, context: dict) -> str:
    """Inject the rendered material table into planner prompts."""
    table = context.get("material_table")
    if not table:
        table = "(no material source wired up yet - treat every candidate below as unused)"
    return prompt_text.replace("{{material_table}}", str(table))
