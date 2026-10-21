# Yaduha translation workspace

A development workspace for the [Yaduha](https://github.com/kubishi/yaduha) LLM-Assisted Rule-Based Machine Translation (LLM-RBMT) framework and its language packs. It also hosts the interactive tutorial that walks through the approach we used to build an English to Owens Valley Paiute translator.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=1242685188)

## Setup

Requires [uv](https://docs.astral.sh/uv/). From this directory:

```bash
git submodule update --init       # yaduha and yaduha-ovp
uv sync                           # install yaduha, every language pack, jupyter, etc.
uv run yaduha languages list      # confirm the language packs are registered
```

All packages are installed as editable, so changes to `yaduha/` or `languages/*` take effect without reinstalling.

## API key

Translators call an LLM. Put your key in a `.env` file at the repo root:

```
OPENAI_API_KEY=sk-...
```

`OPENAI_BASE_URL` and `OPENAI_MODEL` are also read by the tutorial if you want to point it at another OpenAI-compatible endpoint.

## Languages

| Code | Language | Source | Location |
|------|----------|--------|----------|
| `ovp` | Owens Valley Paiute | [kubishi/yaduha-ovp](https://github.com/kubishi/yaduha-ovp) | `languages/yaduha-ovp` (submodule) |
| `bzd` | Bribri | [AmericasNLP 2026 shared task](https://github.com/kubishi/americasnlp-2026-shared-task) | `languages/yaduha-bzd` |
| `grn` | Guaraní | AmericasNLP 2026 shared task | `languages/yaduha-grn` |
| `hch` | Wixárika | AmericasNLP 2026 shared task | `languages/yaduha-hch` |
| `nlv` | Orizaba Nahuatl | AmericasNLP 2026 shared task | `languages/yaduha-nlv` |
| `yua` | Yucatec Maya | AmericasNLP 2026 shared task | `languages/yaduha-yua` |

The five shared-task packs were copied in-tree from `kubishi/americasnlp-2026-shared-task` at commit `2849ac6`. They support the `PipelineTranslator` but do not yet provide `get_instructions`, so the `InstructionsTranslator` only works for `ovp`.

### Trying a language

```python
from yaduha.agent.openai import OpenAIAgent
from yaduha.translator.pipeline import PipelineTranslator

agent = OpenAIAgent(model="gpt-4o-mini", api_key="sk-...")
translation = PipelineTranslator.from_language("grn", agent=agent).translate("The dog saw the man.")
print(translation.target)                     # Jagua ohecha-kuri kuimba'e.
print(translation.back_translation.source)    # The dog saw a man.
```

### Adding a language

1. Create the pack. Copy the layout of an existing one (`languages/yaduha-ovp` is the most complete): a `pyproject.toml` that registers the language under `[project.entry-points."yaduha.languages"]`, a `vocab.py`, and `Sentence` subclasses in `__init__.py`.
2. Put it under `languages/`. A pack with its own GitHub repo goes in as a submodule (`git submodule add <url> languages/yaduha-xxx`); a pack still being prototyped can live in-tree.
3. Add it to `dependencies` and `[tool.uv.sources]` in `pyproject.toml`, then run `uv sync`.
4. Check it with `uv run yaduha languages validate xxx`.

## Tutorial

Open [tutorial.ipynb](tutorial.ipynb) with `uv run jupyter lab tutorial.ipynb`, or in VS Code pick the `.venv` kernel that `uv sync` created. The notebook is written for both linguists and language-community members (no programming background assumed) and ML researchers. Cells that need an API key are gated; the rest run without one.

`tutorial.ipynb` is edited directly. `build_notebook.py` generated the first version and is now out of date, so running it would overwrite later edits.

## Layout

- `yaduha/`: the framework (translators, agents, evaluators, language loader), as a submodule.
- `languages/`: language packs, one directory per language.
- `tutorial.ipynb`: the tutorial notebook. `tutorial_excercises.py` holds its exercises.
- `Dockerfile`, `docker-compose.yml`, `.devcontainer/`: containerized and Codespaces setups for running the tutorial.
- `local/`: papers and slides, not tracked in git.
