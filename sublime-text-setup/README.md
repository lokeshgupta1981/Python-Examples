Files for the article https://howtodoinjava.com/python-basics/install-python-sublime-editor/

Versions: Sublime Text 4 (build 4197 or later for "interactive"), Python 3.14

- demo.py: a script to run with Ctrl+B
- Python venv.sublime-build: build system that runs .venv/bin/python (copy to the Packages/User folder)
- LSP.sublime-settings: format and fix on save with LSP-ruff (Preferences > Package Settings > LSP > Settings)
- Python.sublime-settings: syntax-specific settings for .py files (Preferences > Settings - Syntax Specific)
- pyrightconfig.json: tells LSP-pyright to use the project's .venv (place in the project root)
