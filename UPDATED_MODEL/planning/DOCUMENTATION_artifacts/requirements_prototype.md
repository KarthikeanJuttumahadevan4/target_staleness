# Requirements for Knowledge Graph Prototype

## Existing extraction stack
pdfplumber
openpyxl
python-dotenv
openai
anthropic

## Prototype graph stack
networkx
pyvis

## Future migration stack
dspy==3.4.0
docling==2.132.0
python-dotenv

Notes:
- Current pyproject.toml already pins dspy==3.4.0 and docling==2.132.0 for future migration.
- Add networkx and pyvis to pyproject.toml dependencies for graph prototype.
- Keep requires-python >=3.14 and setuptools build backend without module discovery.
