def hook_metadata(prompt_text: str, context: dict) -> str:
    for key, value in context.items():
        prompt_text = prompt_text.replace('{{' + key + '}}', str(value))
    return prompt_text

def hook_fonts(prompt_text: str, context: dict) -> str:
    fonts = context.get('fonts', [])
    if fonts:
        fonts_block = '\n'.join(f'- {font}' for font in fonts)
    else:
        fonts_block = '(no fonts configured yet - pick any reasonable font name)'
    return prompt_text.replace('{{available_fonts}}', fonts_block)
