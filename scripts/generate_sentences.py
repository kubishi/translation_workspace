"""Sample random sentences from a language pack's sentence generators.

Calls each sentence type's sample_iter(n) and prints the rendered sentences. No LLM is involved, so this runs offline and is the quickest check that a pack's vocabulary and rendering rules produce sensible output.

Usage:
    uv run scripts/generate_sentences.py ovp
    uv run scripts/generate_sentences.py grn -n 10 --type SubjectVerbSentence --seed 0
    uv run scripts/generate_sentences.py yua --structure
"""

import argparse
import random
import sys

from yaduha.language.exceptions import LanguageNotFoundError
from yaduha.loader import LanguageLoader


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("language", help="language code, for example ovp")
    parser.add_argument("-n", type=int, default=5, help="sentences per sentence type (default: 5)")
    parser.add_argument("--type", dest="types", action="append", metavar="NAME", help="only sample this sentence type (repeatable)")
    parser.add_argument("--structure", action="store_true", help="also print each sentence's structured form as JSON")
    parser.add_argument("--seed", type=int, help="random seed, for reproducible samples")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    try:
        language = LanguageLoader.load_language(args.language)
    except LanguageNotFoundError as e:
        installed = ", ".join(sorted(lang.code for lang in LanguageLoader.list_installed_languages()))
        sys.exit(f"{e}. Installed languages: {installed}")

    sentence_types = language.sentence_types
    if args.types:
        names = {t.__name__ for t in sentence_types}
        unknown = set(args.types) - names
        if unknown:
            sys.exit(f"Unknown sentence type(s): {', '.join(sorted(unknown))}. Available: {', '.join(sorted(names))}")
        sentence_types = tuple(t for t in sentence_types if t.__name__ in args.types)

    print(f"{language.name} ({language.code})")
    for sentence_type in sentence_types:
        print(f"\n{sentence_type.__name__}")
        # sample_iter is a convention in the language packs, not part of the Sentence base class.
        sample_iter = getattr(sentence_type, "sample_iter", None)
        if sample_iter is None:
            print("  (no sample_iter defined)")
            continue
        for sentence in sample_iter(args.n):
            print(f"  {sentence}")
            if args.structure:
                print(f"    {sentence.model_dump_json(exclude_none=True)}")


if __name__ == "__main__":
    main()
