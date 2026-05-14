"""
Zolo Language Server Protocol Implementation

Full-featured LSP server for .zolo files following the "thin wrapper" pattern:
- Parser does ALL the work (tokenize() is the brain)
- LSP server just wraps parser output in LSP protocol
- Providers delegate to provider_modules/ (modular!)

Features Provided:
- Semantic highlighting (context-aware token types)
- Diagnostics (real-time error detection)
- Hover information (type hint docs, key info)
- Code completion (type hints, values, file-type-specific)
- Future: Go-to-definition, find references, rename

Architecture:
- ZoloLanguageServer: Main server with parse caching
- @feature decorators: LSP protocol handlers (pygls framework)
- Delegates to: providers/ (completion, hover, diagnostics)
- Parser output: Drives everything (single source of truth)
"""

import logging
import os
import traceback
from pathlib import Path
from urllib.parse import urlparse, unquote
from pygls.lsp.server import LanguageServer  # type: ignore # pylint: disable=import-error,no-name-in-module
from lsprotocol import types as lsp_types  # type: ignore # pylint: disable=import-error,no-name-in-module

# First-party imports (zlsp.*)
from zlsp.themes import load_theme, CodeActionRegistry
from zlsp.lsp_types import ParseResult
from zlsp.providers.diagnostics import get_all_diagnostics
from zlsp.providers.hover import get_hover_info
from zlsp.providers.completion import get_completions
from zlsp.parser.parser_service import tokenize

# Local relative imports within core package
from .semantic_tokenizer import (
    encode_semantic_tokens,
    get_token_types_legend,
    get_token_modifiers_legend
)
from .code_actions import execute_code_action

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("zolo.zLSP.server")

# Build semantic tokens legend ONCE at module level
# Per pygls 2.0 convention: pass legend as keyword arg to @feature decorator
SEMANTIC_TOKENS_LEGEND = lsp_types.SemanticTokensLegend(
    token_types=get_token_types_legend(),
    token_modifiers=get_token_modifiers_legend()
)


class ZoloLanguageServer(LanguageServer):
    """
    Language Server for .zolo files with parse caching.

    Extends pygls.lsp.server.LanguageServer with .zolo-specific functionality:
    - Caches parse results to avoid re-parsing on every request
    - Extracts filenames for context-aware tokenization (zUI, zEnv, etc.)
    - Handles parse errors gracefully

    Attributes:
        parse_cache (dict): Maps URI → ParseResult for performance
    """

    def __init__(self):
        super().__init__("zolo-lsp", "v1.0")
        self.parse_cache = {}  # Cache parsed results by URI

    def get_parse_result(self, uri: str, content: str) -> ParseResult:
        """
        Get cached parse result or parse content.

        Implements a simple cache-aside pattern:
        1. Check cache first
        2. On miss, parse content with tokenize()
        3. Store result in cache

        Args:
            uri: Document URI (e.g., file:///path/to/file.zolo)
            content: Raw document text

        Returns:
            ParseResult with data, tokens, diagnostics

        Note:
            This is a simple cache - production should invalidate on version changes.
            Currently invalidates manually on didChange/didSave events.
        """
        # Simple cache - in production, should check document version
        if uri not in self.parse_cache:
            try:
                # Extract filename from URI for context-aware tokenization
                # (e.g., "zUI.*.zolo" triggers UI element highlighting)
                parsed_uri = urlparse(uri)
                filename = Path(unquote(parsed_uri.path)).name if parsed_uri.path else None

                # Parse with tokenization (the brain!)
                result = tokenize(content, filename=filename)
                self.parse_cache[uri] = result
            except Exception as e:  # pylint: disable=broad-except
                logger.error("Parse error for %s: %s", uri, e)
                # Return empty result on error (graceful degradation)
                result = ParseResult(data=None, tokens=[], errors=[str(e)])
                self.parse_cache[uri] = result
        return self.parse_cache[uri]

    def invalidate_cache(self, uri: str):
        """
        Invalidate cached parse result for a document.

        Called when document changes (didChange, didSave) to force re-parsing.
        """
        if uri in self.parse_cache:
            del self.parse_cache[uri]


# Initialize server
zolo_server = ZoloLanguageServer()

# Create semantic tokens legend and options at MODULE LEVEL
# This allows pygls to serialize them when auto-generating capabilities
token_types_list = get_token_types_legend()
token_modifiers_list = get_token_modifiers_legend()

SEMANTIC_LEGEND = lsp_types.SemanticTokensLegend(
    token_types=token_types_list,
    token_modifiers=token_modifiers_list
)

SEMANTIC_OPTIONS = lsp_types.SemanticTokensRegistrationOptions(
    legend=SEMANTIC_LEGEND,
    full=True,
    document_selector=[{"language": "zolo"}]  # Required for registration options
)

# Load code actions from theme (SSOT approach)  # cspell:ignore SSOT
try:
    THEME = load_theme('zolo_default')
    CODE_ACTION_REGISTRY = CodeActionRegistry(THEME)
    logger.info("Loaded %d code actions from theme", len(CODE_ACTION_REGISTRY.actions))
except Exception as e:  # pylint: disable=broad-except
    logger.warning("Failed to load code actions: %s", e)
    CODE_ACTION_REGISTRY = None


@zolo_server.feature(lsp_types.INITIALIZE)
def initialize(params: lsp_types.InitializeParams):
    """
    Initialize the language server (LSP handshake).

    Called once when editor first connects to LSP server.
    pygls auto-generates capabilities from @feature decorators, so we just log.

    Args:
        params: Initialization parameters from client (editor)

    Returns:
        None - pygls auto-generates InitializeResult from decorators

    Capabilities Advertised (via @feature decorators):
        - textDocumentSync (open, change, save, close)
        - semanticTokensProvider (full document)
        - hoverProvider
        - completionProvider
    """
    logger.info("Initializing Zolo Language Server")
    logger.info("Client: %s", params.client_info.name if params.client_info else 'Unknown')
    logger.info("Workspace: %s", params.root_uri)
    logger.info("Semantic tokens configured with %d token types", len(token_types_list))
    logger.info("Token types: %s", token_types_list)

    # Let pygls auto-generate capabilities from @feature decorators
    return None


@zolo_server.feature(lsp_types.TEXT_DOCUMENT_DID_OPEN)
async def did_open(params: lsp_types.DidOpenTextDocumentParams):
    """
    Handle document opened event (user opens .zolo file in editor).

    Flow:
    1. Get document content from workspace
    2. Parse content with tokenize() (cached for performance)
    3. Publish diagnostics (errors/warnings) to editor

    Args:
        params: Contains document URI, content, language ID

    Side Effects:
        - Caches parse result in zolo_server.parse_cache
        - Publishes diagnostics via LSP (async)

    Note:
        This is the first time we see the document, so we always parse.
        Subsequent requests (hover, completion) reuse cached parse result.
    """
    uri = params.text_document.uri
    logger.info("========== DOCUMENT OPENED ==========")
    logger.info("URI: %s", uri)
    logger.info("Language ID: %s", params.text_document.language_id)

    document = zolo_server.workspace.get_text_document(uri)
    content = document.source

    logger.info("Content length: %d characters", len(content))

    # Parse and cache (tokenize() does the heavy lifting)
    parse_result = zolo_server.get_parse_result(uri, content)

    logger.info("Parsed %d tokens", len(parse_result.tokens))

    # Publish diagnostics (errors/warnings show up in editor)
    await publish_diagnostics(uri, parse_result)

    logger.info("========== END DOCUMENT OPENED ==========")


@zolo_server.feature(lsp_types.TEXT_DOCUMENT_DID_CHANGE)
async def did_change(params: lsp_types.DidChangeTextDocumentParams):
    """
    Handle document changed event.

    Re-parse document and update diagnostics.
    """
    uri = params.text_document.uri
    logger.info("Document changed: %s", uri)

    # Invalidate cache
    zolo_server.invalidate_cache(uri)

    document = zolo_server.workspace.get_text_document(uri)
    content = document.source

    # Parse and cache
    parse_result = zolo_server.get_parse_result(uri, content)

    # Publish diagnostics
    await publish_diagnostics(uri, parse_result)


@zolo_server.feature(lsp_types.TEXT_DOCUMENT_DID_SAVE)
async def did_save(params: lsp_types.DidSaveTextDocumentParams):
    """
    Handle document saved event.

    Re-validate document.
    """
    uri = params.text_document.uri
    logger.info("Document saved: %s", uri)

    # Invalidate cache and re-parse
    zolo_server.invalidate_cache(uri)

    document = zolo_server.workspace.get_text_document(uri)
    content = document.source

    parse_result = zolo_server.get_parse_result(uri, content)
    await publish_diagnostics(uri, parse_result)


@zolo_server.feature(lsp_types.TEXT_DOCUMENT_DID_CLOSE)
def did_close(params: lsp_types.DidCloseTextDocumentParams):
    """
    Handle document closed event.

    Clear cache and diagnostics.
    """
    uri = params.text_document.uri
    logger.info("Document closed: %s", uri)

    # Clear cache
    zolo_server.invalidate_cache(uri)

    # Clear diagnostics
    zolo_server.text_document_publish_diagnostics(
        lsp_types.PublishDiagnosticsParams(uri=uri, diagnostics=[])
    )


@zolo_server.feature(lsp_types.TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL, SEMANTIC_OPTIONS)
def semantic_tokens_full(params: lsp_types.SemanticTokensParams):
    """
    Provide semantic tokens for the entire document (LSP semantic highlighting).

    This is the CORE feature that makes Zolo LSP shine!
    Unlike simple syntax highlighting (regex-based), semantic tokens understand:
    - File type context (zUI vs zEnv vs zSchema)
    - Indentation level (root vs nested vs grandchild)
    - Key meaning (zMeta, zRBAC, zSub, UI elements)
    - Type hints, modifiers, special values

    Flow:
    1. Get cached parse result (or parse if not cached)
    2. Parse result contains SemanticToken[] from tokenize()
    3. Encode tokens into LSP format (delta-encoded integers)
    4. Editor applies colors based on token types

    Args:
        params: Contains document URI

    Returns:
        SemanticTokens with delta-encoded token data

    LSP Encoding:
        Each token = 5 integers: [deltaLine, deltaStart, length, tokenType, modifiers]
        Delta encoding = relative to previous token (space-efficient)

    Note:
        Parser does ALL the work! This handler just wraps parser output.
    """
    uri = params.text_document.uri
    logger.info("========== SEMANTIC TOKENS REQUEST ==========")
    logger.info("URI: %s", uri)

    try:
        document = zolo_server.workspace.get_text_document(uri)
        content = document.source

        logger.info("Document length: %d characters", len(content))
        logger.info("First 100 chars: %r", content[:100])

        # Get parse result with tokens
        parse_result = zolo_server.get_parse_result(uri, content)

        logger.info("Parser generated %d tokens", len(parse_result.tokens))

        # Log first few tokens for debugging
        lines = content.splitlines()
        if parse_result.tokens:
            for i, token in enumerate(parse_result.tokens[:20]):
                # Extract actual text
                if token.line < len(lines):
                    line_text = lines[token.line]
                    end_pos = token.start_char + token.length
                    if end_pos <= len(line_text):
                        token_text = line_text[token.start_char:end_pos]
                    else:
                        token_text = "???"
                else:
                    token_text = "???"
                # Handle both TokenType enum and int values
                if hasattr(token.token_type, 'name'):
                    token_type_name = token.token_type.name
                else:
                    token_type_name = str(token.token_type)
                logger.info("  Token %d: line=%d, start=%d, len=%d, type=%s, text=%r",
                            i, token.line, token.start_char, token.length,
                            token_type_name, token_text)

        # Encode tokens for LSP
        encoded = encode_semantic_tokens(parse_result.tokens)

        logger.info("Encoded to %d integers", len(encoded))
        logger.info("First 25 encoded values: %s", encoded[:25])
        logger.info("Returning SemanticTokens with %d data elements", len(encoded))

        result = lsp_types.SemanticTokens(data=encoded)
        logger.info("Result type: %s", type(result))
        logger.info("Result.data length: %d", len(result.data))
        logger.info("========== END SEMANTIC TOKENS REQUEST ==========")

        return result

    except Exception as e:  # pylint: disable=broad-except
        logger.error("Error providing semantic tokens: %s", e)
        # Return empty tokens on error
        return lsp_types.SemanticTokens(data=[])


@zolo_server.feature(lsp_types.TEXT_DOCUMENT_HOVER)
def hover(params: lsp_types.HoverParams):
    """
    Provide hover information at a specific position.

    Shows type hints, value types, and documentation.
    """
    uri = params.text_document.uri
    line = params.position.line
    character = params.position.character

    logger.info("Hover requested for: %s at %d:%d", uri, line, character)

    try:
        document = zolo_server.workspace.get_text_document(uri)
        content = document.source

        # Use cached parse result (don't re-tokenize!)
        parse_result = zolo_server.get_parse_result(uri, content)

        # Get hover info using cached tokens
        hover_text = get_hover_info(content, line, character, parse_result.tokens)

        if hover_text:
            return lsp_types.Hover(
                contents=lsp_types.MarkupContent(
                    kind=lsp_types.MarkupKind.Markdown,
                    value=hover_text
                )
            )

        return None

    except Exception as e:  # pylint: disable=broad-except
        logger.error("Error providing hover: %s", e)
        return None


@zolo_server.feature(
    lsp_types.TEXT_DOCUMENT_COMPLETION,
    lsp_types.CompletionOptions(trigger_characters=["(", ":", "z", ">"])
)
def completions(params: lsp_types.CompletionParams):
    """
    Provide completion items at a specific position.

    Offers context-aware completions for:
    - Type hints (inside parentheses)
    - Common values (after colon)
    - zOS shorthands (at line start)
    """
    uri = params.text_document.uri
    line = params.position.line
    character = params.position.character

    logger.info("Completions requested for: %s at %d:%d", uri, line, character)

    try:
        document = zolo_server.workspace.get_text_document(uri)
        content = document.source

        # Extract filename from URI for file type detection
        filename = os.path.basename(uri) if uri else None

        # Get completion items (now with filename for file type detection!)
        items = get_completions(content, line, character, filename=filename)

        return lsp_types.CompletionList(
            is_incomplete=False,
            items=items
        )

    except Exception as e:  # pylint: disable=broad-except
        logger.error("Error providing completions: %s", e)
        return lsp_types.CompletionList(is_incomplete=False, items=[])


@zolo_server.feature(lsp_types.TEXT_DOCUMENT_CODE_ACTION)
def code_actions(params: lsp_types.CodeActionParams):
    """
    Provide code actions (quick fixes & refactorings) for diagnostics.

    Reads action configs from YAML, matches them to diagnostics,
    executes them, and returns LSP CodeAction objects.

    All logic is data-driven from themes/zolo_default.yaml!
    """
    uri = params.text_document.uri

    logger.info("Code actions requested for: %s", uri)

    # Check if code actions are enabled
    if not CODE_ACTION_REGISTRY or not CODE_ACTION_REGISTRY.is_enabled():
        logger.debug("Code actions disabled or registry not loaded")
        return []

    try:
        # Get document content
        document = zolo_server.workspace.get_text_document(uri)
        content = document.source
        lines = content.split('\n')

        # Extract filename from URI
        parsed_uri = urlparse(uri)
        filename = Path(unquote(parsed_uri.path)).name if parsed_uri.path else None

        # Get diagnostics from context
        diagnostics = params.context.diagnostics

        # Collect all applicable actions
        actions = []

        # Match actions to diagnostics
        for diagnostic in diagnostics:
            # Find actions that match this diagnostic
            matching_actions = CODE_ACTION_REGISTRY.get_actions_for_diagnostic(
                diagnostic.message
            )

            for action in matching_actions:
                # Check if already added (avoid duplicates)
                if any(a.title == action['title'] for a in actions):
                    continue

                # Build context for execution
                line_number = diagnostic.range.start.line
                if line_number < len(lines):
                    line_content = lines[line_number]

                    context = {
                        'line': line_content,
                        'line_number': line_number,
                        'cursor_position': diagnostic.range.start.character,
                        'document_content': content,
                        'file_name': filename or ''
                    }

                    # Execute action to get text edits
                    try:
                        edits = execute_code_action(action, context)

                        if edits:
                            # Create LSP CodeAction
                            code_action = lsp_types.CodeAction(
                                title=action['title'],
                                kind=lsp_types.CodeActionKind.QuickFix,
                                diagnostics=[diagnostic],
                                edit=lsp_types.WorkspaceEdit(
                                    changes={uri: edits}
                                )
                            )
                            actions.append(code_action)
                            logger.debug("Added action: %s", action['title'])

                    except Exception as e:  # pylint: disable=broad-except
                        logger.error("Error executing action %s: %s", action['id'], e)
                        continue

        # Also check for file-pattern based actions (not tied to diagnostics)
        if filename:
            file_actions = CODE_ACTION_REGISTRY.get_actions_for_file(filename)
            for action in file_actions:
                # Skip if no diagnostic trigger (these need explicit context)
                if 'context' in action.get('triggers', {}):
                    # Would need cursor context to determine if applicable
                    # For now, skip these
                    continue

        # Respect max actions limit
        max_actions = CODE_ACTION_REGISTRY.get_max_actions()
        if len(actions) > max_actions:
            actions = actions[:max_actions]

        logger.info("Returning %d code actions", len(actions))
        return actions

    except Exception as e:  # pylint: disable=broad-except
        logger.error("Error providing code actions: %s", e)
        traceback.print_exc()
        return []


async def publish_diagnostics(uri: str, parse_result: ParseResult):  # pylint: disable=unused-argument
    """
    Publish diagnostics for a document.

    Uses diagnostics engine to convert parse errors to LSP diagnostics.
    """
    logger.info("🚀 publish_diagnostics called for %s", uri)

    # Get document content
    document = zolo_server.workspace.get_text_document(uri)
    content = document.source

    # Extract filename from URI for context-aware diagnostics
    parsed_uri = urlparse(uri)
    filename = Path(unquote(parsed_uri.path)).name if parsed_uri.path else None

    logger.info("   📄 filename=%s, content_length=%d", filename, len(content))

    # Get diagnostics from engine (includes parsing and validation)
    try:
        diagnostics = get_all_diagnostics(content, include_style=True, filename=filename)
        logger.info("   ✅ get_all_diagnostics returned %d diagnostics", len(diagnostics))
    except Exception as e:  # pylint: disable=broad-except
        logger.error("   ❌ Exception in get_diagnostics: %s", e)
        traceback.print_exc()
        diagnostics = []

    logger.info("   📤 Publishing %d diagnostics", len(diagnostics))
    zolo_server.text_document_publish_diagnostics(
        lsp_types.PublishDiagnosticsParams(uri=uri, diagnostics=diagnostics)
    )


def main():
    """Main entry point for the LSP server."""
    logger.info("Starting Zolo Language Server")

    try:
        # Start server on stdio
        zolo_server.start_io()
    except Exception as e:  # pylint: disable=broad-except
        logger.error("Server error: %s", e)
        raise

if __name__ == "__main__":
    main()
