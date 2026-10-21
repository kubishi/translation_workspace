"""Translate English sentences into a language pack's language with one or more translators.

Translators:
    pipeline      English to structured sentences to target text, constrained by the pack's grammar models.
    instructions  The LLM translates directly, guided by the pack's get_instructions() prompt (only some packs provide one).
    agentic       The LLM translates directly with no grammar or vocabulary help, as a baseline.

Every translation is back-translated to English. The pipeline translator does this itself; for the others the script uses an InstructionsBackTranslator built from the pack's source code.

Reads OPENAI_API_KEY (and optionally OPENAI_BASE_URL and OPENAI_MODEL) from the environment or a .env file.

Usage:
    uv run scripts/translate.py ovp "The dog saw the man."
    uv run scripts/translate.py grn "I am eating." "The bird is in the tree." -t pipeline -t agentic
    uv run scripts/translate.py yua -f sentences.txt --model gpt-4o
"""

import argparse
import os
import sys
import warnings

from dotenv import load_dotenv
from yaduha.agent.openai import OpenAIAgent
from yaduha.language.exceptions import LanguageNotFoundError
from yaduha.loader import LanguageLoader
from yaduha.translator import Translation, Translator
from yaduha.translator.agentic import AgenticTranslator
from yaduha.translator.instructions import InstructionsTranslator
from yaduha.translator.instructions_back import InstructionsBackTranslator
from yaduha.translator.pipeline import PipelineTranslator

TRANSLATORS = ["pipeline", "instructions", "agentic"]

# The OpenAI SDK's parsed-message type trips a harmless pydantic warning on every call.
warnings.filterwarnings("ignore", message="Pydantic serializer warnings")


def build_translator(name: str, code: str, agent: OpenAIAgent) -> Translator:
    if name == "pipeline":
        return PipelineTranslator.from_language(code, agent=agent)
    if name == "instructions":
        return InstructionsTranslator.from_language(code, agent=agent)
    language = LanguageLoader.load_language(code)
    return AgenticTranslator(
        agent=agent,
        system_prompt=f"You are a translator from English to {language.name}. Translate the user's text as accurately as you can.",
    )


def print_translation(name: str, translation: Translation) -> None:
    back = translation.back_translation.source if translation.back_translation else "(none)"
    # InstructionsBackTranslator returns no English for text the pack's grammar can't parse.
    back = back or "(not parseable with the pack's grammar)"
    tokens = translation.prompt_tokens + translation.completion_tokens
    print(f"  {name}")
    print(f"    target: {translation.target}")
    print(f"    back:   {back}")
    print(f"    {translation.translation_time:.1f}s, {tokens} tokens")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("language", help="language code, for example ovp")
    parser.add_argument("sentences", nargs="*", help="English sentences to translate")
    parser.add_argument("-f", "--file", help="read English sentences from a file, one per line")
    parser.add_argument("-t", "--translator", dest="translators", action="append", choices=TRANSLATORS, help="translator to run (repeatable; default: all)")
    parser.add_argument("--model", default=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), help="OpenAI model (default: $OPENAI_MODEL or gpt-4o-mini)")
    args = parser.parse_args()

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        sys.exit("OPENAI_API_KEY is not set. Put it in .env at the repo root.")

    sentences = list(args.sentences)
    if args.file:
        with open(args.file, encoding="utf-8") as f:
            sentences += [line.strip() for line in f if line.strip()]
    if not sentences:
        sys.exit("Give at least one English sentence, or a file with -f.")

    try:
        language = LanguageLoader.load_language(args.language)
    except LanguageNotFoundError as e:
        installed = ", ".join(sorted(lang.code for lang in LanguageLoader.list_installed_languages()))
        sys.exit(f"{e}. Installed languages: {installed}")

    agent = OpenAIAgent(model=args.model, api_key=api_key)
    back_translator = InstructionsBackTranslator.from_language(language.code, agent=agent)

    translators: dict[str, Translator] = {}
    for name in args.translators or TRANSLATORS:
        try:
            translators[name] = build_translator(name, language.code, agent)
        except ValueError as e:
            print(f"Skipping {name}: {e}\n")

    print(f"{language.name} ({language.code}), model {args.model}")
    for english in sentences:
        print(f"\n{english}")
        for name, translator in translators.items():
            try:
                translation = translator.translate(english)
                if translation.back_translation is None:
                    translation.back_translation = back_translator.back_translate(translation.target)
                print_translation(name, translation)
            except Exception as e:
                print(f"  {name}\n    failed: {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
