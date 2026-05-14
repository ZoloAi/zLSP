"""
Generators for creating language tooling from zlsp SSOT.

This package contains generators that transform zlsp's Single Source of Truth
(SSOT) token patterns into tooling for various editors and syntax highlighters.

Current generators:
- Prism.js: Multi-language syntax highlighting for web (6 file types)

Usage:
    python3 -m zlsp.generators.generate_prism_zolo
"""

from .generate_prism_zolo import main as generate_prism

__all__ = ['generate_prism']
