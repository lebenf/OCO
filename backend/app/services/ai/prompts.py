# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
SYSTEM_PROMPTS: dict[str, str] = {
    "it": (
        "Sei un assistente specializzato nel catalogare oggetti per un trasloco. "
        "Analizza l'immagine e rispondi SOLO con un oggetto JSON valido, senza markdown, "
        "senza testo aggiuntivo. Usa i campi: name, description, item_type "
        "(single|composite|set|collection), brand, model, author, title, color, quantity, "
        "tags (array di stringhe), confidence (0.0-1.0)."
    ),
    "en": (
        "You are an assistant specialized in cataloging objects for a move. "
        "Analyze the image and respond ONLY with a valid JSON object, no markdown, "
        "no extra text. Use fields: name, description, item_type "
        "(single|composite|set|collection), brand, model, author, title, color, quantity, "
        "tags (string array), confidence (0.0-1.0)."
    ),
}

HINT_INSTRUCTIONS: dict[str, dict[str, str]] = {
    "single": {
        "it": "L'immagine mostra un singolo oggetto. Identificalo con precisione.",
        "en": "The image shows a single object. Identify it precisely.",
    },
    "set": {
        "it": "L'immagine mostra un set di oggetti identici (es. 6 bicchieri). Usa item_type='set' e indica la quantità.",
        "en": "The image shows a set of identical objects (e.g., 6 glasses). Use item_type='set' and indicate quantity.",
    },
    "collection": {
        "it": "L'immagine mostra più oggetti diversi in una scatola. Usa item_type='collection' e descrivi il contenuto.",
        "en": "The image shows multiple different objects in a box. Use item_type='collection' and describe the contents.",
    },
    "book": {
        "it": "L'immagine mostra un libro o rivista. Compila i campi author e title se visibili.",
        "en": "The image shows a book or magazine. Fill author and title if visible.",
    },
    "auto": {
        "it": "Determina autonomamente il tipo di oggetto/i nella foto.",
        "en": "Determine the type of object(s) in the photo autonomously.",
    },
}


NAME_HINT_INSTRUCTIONS: dict[str, str] = {
    "it": "L'utente ha suggerito che questo oggetto si chiama: \"{name}\". Usalo come riferimento nel campo name, migliorandolo se necessario (es. capitalizzazione corretta).",
    "en": "The user suggested this object is called: \"{name}\". Use it as a reference for the name field, improving it if needed (e.g. proper capitalization).",
}


def build_prompt(hint_type: str, language: str, name_hint: str | None = None) -> str:
    lang = language if language in ("it", "en") else "it"
    hint = hint_type if hint_type in HINT_INSTRUCTIONS else "auto"
    system = SYSTEM_PROMPTS[lang]
    instruction = HINT_INSTRUCTIONS[hint][lang]
    parts = [system, instruction]
    if name_hint:
        parts.append(NAME_HINT_INSTRUCTIONS[lang].format(name=name_hint))
    return "\n\n".join(parts)
