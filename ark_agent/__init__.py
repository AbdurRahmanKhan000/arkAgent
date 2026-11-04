"""arkAgent: a small, fast, fixed-command laptop agent. No LLM.

Voice and typed text share one parser. Only phrases in commands.json
can execute, and only through allowlisted handlers in actions.py.
"""

__version__ = "1.1.0"
__all__ = ["__version__"]
