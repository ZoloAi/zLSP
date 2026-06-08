"""
Shared base installer for VS Code-based editors.

Since Cursor is a VS Code fork, they use identical extension formats.
This module provides shared functionality to avoid code duplication.

Usage:
    vscode_installer = VSCodeBasedInstaller(
        editor_name="VS Code",
        dir_name=".vscode",
        settings_name="Code"
    )
    vscode_installer.install()

    cursor_installer = VSCodeBasedInstaller(
        editor_name="Cursor",
        dir_name=".cursor",
        settings_name="Cursor",
        requires_registry=True
    )
    cursor_installer.install()
"""

import json
import os
import shutil
import sys
import uuid
from datetime import datetime
from pathlib import Path

# Import theme system and VS Code generator
try:
    from zlsp.themes import load_theme
    from zlsp.themes.generators.vscode import VSCodeGenerator
    from zlsp.version import __version__
except ImportError:
    # Fallback if running from different context
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from zlsp.themes import load_theme
    from zlsp.themes.generators.vscode import VSCodeGenerator
    from zlsp.version import __version__


class VSCodeBasedInstaller:
    """
    Base installer for VS Code-based editors (VS Code, Cursor, etc.).
    
    Provides all common installation logic with editor-specific configuration.
    """
    
    def __init__(self, editor_name, dir_name, settings_name, requires_registry=False):
        """
        Initialize the installer for a specific VS Code-based editor.
        
        Args:
            editor_name: Human-readable name (e.g., "VS Code", "Cursor")
            dir_name: Directory name in home folder (e.g., ".vscode", ".cursor")
            settings_name: Settings folder name (e.g., "Code", "Cursor")
            requires_registry: Whether editor requires extensions.json registry
        """
        self.editor_name = editor_name
        self.dir_name = dir_name
        self.settings_name = settings_name
        self.requires_registry = requires_registry
        
        self.theme = None
        self.generator = None
        self.extensions_dir = None
        self.settings_path = None
    
    def detect_extensions_dir(self):
        """Detect editor extensions directory."""
        ext_dir = Path.home() / self.dir_name / 'extensions'
        
        if not ext_dir.exists():
            ext_dir.mkdir(parents=True, exist_ok=True)
        
        return ext_dir
    
    def detect_user_settings(self):
        """
        Detect editor user settings.json location.
        
        Returns:
            Path to settings.json (may not exist yet)
        """
        system = os.uname().sysname if hasattr(os, 'uname') else os.name
        
        if system == 'Darwin':  # macOS
            settings_path = Path.home() / 'Library' / 'Application Support' / self.settings_name / 'User' / 'settings.json'
        elif system == 'Linux':
            settings_path = Path.home() / '.config' / self.settings_name / 'User' / 'settings.json'
        elif system in ('Windows', 'nt'):
            appdata = os.getenv('APPDATA')
            if appdata:
                settings_path = Path(appdata) / self.settings_name / 'User' / 'settings.json'
            else:
                settings_path = Path.home() / 'AppData' / 'Roaming' / self.settings_name / 'User' / 'settings.json'
        else:
            # Unknown system, try Linux-style path
            settings_path = Path.home() / '.config' / self.settings_name / 'User' / 'settings.json'
        
        return settings_path
    
    def generate_semantic_token_rules(self):
        """
        Generate semantic token color rules for settings.json.
        
        Returns:
            Dictionary mapping token types to color settings
        """
        rules = {}
        
        # All token types from our semantic token legend
        token_types = [
            'comment', 'rootKey', 'nestedKey', 'zmetaKey', 'zosDataKey',
            'zschemaPropertyKey', 'bifrostKey', 'controlFlowKey', 'uiElementKey', 'uiElementPropertyKey',
            'zconfigKey', 'zsparkKey', 'zenvConfigKey', 'znavbarNestedKey', 'zsubKey',
            'zsparkNestedKey', 'zsparkModeValue', 'zsparkVaFileValue',
            'zsparkSpecialValue', 'envConfigValue', 'zrbacKey', 'zrbacOptionKey',
            'typeHint', 'number', 'string', 'boolean', 'null',
            'bracketStructural', 'braceStructural', 'stringBracket', 'stringBrace',
            'colon', 'comma', 'escapeSequence', 'versionString', 'timestampString',
            'timeString', 'ratioString', 'zpathValue', 'zmachineEditableKey',
            'zmachineLockedKey', 'typeHintParen', 'zconfigNestedKey', 'dispatchKey'
        ]
        
        for token_type in token_types:
            token_style = self.generator.theme.get_token_style(token_type)
            if token_style:
                color = token_style.get('hex', '#ffffff')
                style = token_style.get('style', 'none')
                
                # Format for settings.json
                if style != 'none':
                    rules[token_type] = {
                        "foreground": color,
                        "fontStyle": style.replace(',', ' ')
                    }
                else:
                    rules[token_type] = color  # Simple format: just hex color
        
        return rules
    
    def inject_semantic_token_colors(self, rules):
        """
        Inject semantic token colors into editor's settings.json.
        
        Args:
            rules: Dictionary of token type -> color mappings
        
        Returns:
            True if successful, False otherwise
        """
        # Ensure parent directory exists
        self.settings_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Read existing settings or create empty
        if self.settings_path.exists():
            try:
                with open(self.settings_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Handle empty file or just comments
                    if content.strip():
                        settings = json.loads(content)
                    else:
                        settings = {}
            except json.JSONDecodeError:
                print(f"  ⚠ Existing settings.json is invalid JSON, creating backup")
                backup_path = self.settings_path.parent / 'settings.json.zlsp.backup'
                shutil.copy2(self.settings_path, backup_path)
                settings = {}
        else:
            settings = {}
        
        # Inject our semantic token colors
        if "editor.semanticTokenColorCustomizations" not in settings:
            settings["editor.semanticTokenColorCustomizations"] = {}
        
        # Clean up old theme-scoped "[zolo]" section from previous installations
        if "[zolo]" in settings["editor.semanticTokenColorCustomizations"]:
            del settings["editor.semanticTokenColorCustomizations"]["[zolo]"]
            print("  ℹ️  Cleaned up old '[zolo]' theme-scoped colors")
        
        # Apply to all themes using global rules
        semantic_customizations = settings["editor.semanticTokenColorCustomizations"]
        semantic_customizations["enabled"] = True
        
        # Merge rules into global "rules" key
        if "rules" not in semantic_customizations:
            semantic_customizations["rules"] = {}
        
        # Update with our zolo token colors
        semantic_customizations["rules"].update(rules)
        
        # Write back with nice formatting
        try:
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"  ✗ Failed to write settings: {e}")
            return False
    
    def check_editor_installed(self):
        """Check if editor is installed."""
        # Check if editor CLI is in PATH
        cli_name = 'code' if self.editor_name == 'VS Code' else 'cursor'
        if shutil.which(cli_name):
            return True, f"{self.editor_name} CLI found in PATH"
        
        # Check common installation locations (macOS)
        app_name = 'Visual Studio Code.app' if self.editor_name == 'VS Code' else 'Cursor.app'
        editor_locations = [
            Path(f'/Applications/{app_name}'),
            Path.home() / 'Applications' / app_name,
            Path(f'/usr/local/bin/{cli_name}'),
            Path(f'/usr/bin/{cli_name}'),
        ]
        
        for location in editor_locations:
            if location.exists():
                return True, f"{self.editor_name} found at {location}"
        
        return False, f"{self.editor_name} not found"
    
    def check_zolo_lsp_available(self):
        """Check if zolo-lsp command is available."""
        if shutil.which('zolo-lsp'):
            return True, "zolo-lsp command available in PATH"
        
        return False, "zolo-lsp not found (run: pip install zlsp)"
    
    def create_extension_structure(self, base_dir):
        """Create editor extension directory structure."""
        dirs = [
            base_dir,
            base_dir / 'syntaxes',
            base_dir / 'themes',
            base_dir / 'out',
            base_dir / 'icons',
        ]
        
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
        
        return dirs
    
    # Per-role file icons. Each role is a SIBLING language id that shares the
    # source.zolo grammar + LSP (documentSelector below), so it highlights
    # identically but gets its own explorer icon by filename glob. zSpark and any
    # other .zolo fall through to the base `zolo` language (green base icon).
    # role -> (language id, filename globs, icon suffix, alias)
    ROLE_LANGUAGES = [
        ('zolo-ui',     ['zUI.*.zolo'],                          'ui',     'Zolo UI'),
        ('zolo-env',    ['zEnv.*.zolo'],                         'env',    'Zolo Env'),
        ('zolo-server', ['zServer.*.zolo'],                      'server', 'Zolo Server'),
        ('zolo-raven',  ['zRaven.*.zolo', '**/zRaven/*.zolo'],   'raven',  'Zolo Raven'),
    ]

    # Editor defaults applied to every zolo language id (base + siblings).
    _ZOLO_EDITOR_DEFAULTS = {
        "editor.bracketPairColorization.enabled": False,
        "editor.guides.bracketPairs": False,
        "editor.semanticHighlighting.enabled": True,
    }

    def generate_package_json(self, base_dir):
        """Generate package.json from theme and generator."""
        semantic_legend = self.generator.generate_semantic_tokens_legend()

        # Base language (extension match) — green icon, the catch-all for .zolo.
        languages_contrib = [
            {
                "id": "zolo",
                "aliases": ["Zolo", "zolo"],
                "extensions": [".zolo"],
                "configuration": "./language-configuration.json",
                "icon": {
                    "light": "./icons/zolo_filetype.png",
                    "dark": "./icons/zolo_filetype.png",
                },
            }
        ]
        grammars_contrib = [
            {"language": "zolo", "scopeName": "source.zolo",
             "path": "./syntaxes/zolo.tmLanguage.json"}
        ]
        config_defaults = {"[zolo]": dict(self._ZOLO_EDITOR_DEFAULTS)}

        # Sibling languages — filename-glob match wins over the base extension, so
        # zUI.*/zEnv.*/zServer.*/zRaven.* get their tinted icon while keeping the
        # shared grammar, LSP, and editor defaults.
        for lang_id, globs, suffix, alias in self.ROLE_LANGUAGES:
            languages_contrib.append({
                "id": lang_id,
                "aliases": [alias],
                "filenamePatterns": globs,
                "configuration": "./language-configuration.json",
                "icon": {
                    "light": f"./icons/zolo_filetype.{suffix}.png",
                    "dark": f"./icons/zolo_filetype.{suffix}.png",
                },
            })
            grammars_contrib.append({
                "language": lang_id,
                "scopeName": "source.zolo",
                "path": "./syntaxes/zolo.tmLanguage.json",
            })
            config_defaults[f"[{lang_id}]"] = dict(self._ZOLO_EDITOR_DEFAULTS)

        package_json = {
            "name": "zolo-lsp",
            "displayName": "Zolo LSP",
            "description": "Language Server Protocol support for .zolo files with semantic highlighting",
            "version": __version__,
            "publisher": "ZoloAi",
            "icon": "icons/zolo_filetype.png",
            "license": "MIT",
            "homepage": "https://zolo.media",
            "author": {
                "name": "Zolo Media"
            },
            "bugs": {
                "url": "https://zolo.media/support"
            },
            "qna": "marketplace",
            "engines": {
                "vscode": "^1.75.0"
            },
            "categories": [
                "Programming Languages",
                "Formatters",
                "Linters"
            ],
            "keywords": [
                "zolo",
                "zlsp",
                "language-server",
                "lsp",
                "semantic-highlighting"
            ],
            "main": "./out/extension.js",
            "contributes": {
                "languages": languages_contrib,
                "grammars": grammars_contrib,
                "semanticTokenTypes": [
                    {"id": token_type, "description": f"Zolo {token_type}"}
                    for token_type in semantic_legend['tokenTypes']
                ],
                "semanticTokenModifiers": [
                    {"id": modifier, "description": f"Zolo {modifier}"}
                    for modifier in semantic_legend['tokenModifiers']
                ],
                "configuration": {
                    "title": "Zolo",
                    "properties": {
                        "zolo.trace.server": {
                            "type": "string",
                            "enum": ["off", "messages", "verbose"],
                            "default": "messages",
                            "description": f"Traces the communication between {self.editor_name} and the Zolo language server"
                        },
                        "zolo.lsp.debug": {
                            "type": "boolean",
                            "default": True,
                            "description": "Enable debug logging in the output channel"
                        }
                    }
                },
                "configurationDefaults": config_defaults
            },
            "dependencies": {},
            "devDependencies": {}
        }
        
        dest_path = base_dir / 'package.json'
        with open(dest_path, 'w') as f:
            json.dump(package_json, f, indent=2)
        
        return dest_path
    
    def generate_language_configuration(self, base_dir):
        """Generate language-configuration.json."""
        config = {
            "comments": {
                "lineComment": "#"
            },
            # DO NOT define brackets/autoClosingPairs for structural braces/brackets!
            # Our semantic tokens handle these, and editor's built-in bracket
            # colorization interferes with our custom token colors.
            # Only auto-close quotes for convenience.
            "autoClosingPairs": [
                {"open": "\"", "close": "\""},
                {"open": "'", "close": "'"}
            ],
            "surroundingPairs": [
                ["\"", "\""],
                ["'", "'"]
            ],
            "folding": {
                "markers": {
                    "start": "^\\s*#\\s*region",
                    "end": "^\\s*#\\s*endregion"
                }
            }
        }
        
        dest_path = base_dir / 'language-configuration.json'
        with open(dest_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return dest_path
    
    def resolve_server_command(self):
        """
        Resolve the LSP server location AT INSTALL TIME.

        GUI-launched editors (Dock/Finder) do NOT inherit the shell PATH, so the
        extension cannot rely on `which zolo-lsp` at runtime. We capture the
        absolute path here — in the same interpreter that has zlsp installed —
        and bake it into extension.js. The runtime keeps `which` + `python -m`
        as fallbacks for portability.
        """
        exe = shutil.which('zolo-lsp')
        if not exe:
            candidate = Path(sys.executable).parent / 'zolo-lsp'
            if candidate.exists():
                exe = str(candidate)

        bin_dir = str(Path(exe).parent) if exe else str(Path(sys.executable).parent)
        return {
            'exe': exe or '',
            'python': sys.executable,
            'module': 'zlsp.server.lsp_server',
            'bin_dir': bin_dir,
        }

    def generate_extension_js(self, base_dir):
        """Generate extension.js with LSP client."""
        srv = self.resolve_server_command()
        baked_exe = json.dumps(srv['exe'])
        baked_python = json.dumps(srv['python'])
        baked_module = json.dumps(srv['module'])
        baked_bin = json.dumps(srv['bin_dir'])

        code = f"""// Generated by zlsp installer - DO NOT EDIT
// This file activates the Zolo LSP client for {self.editor_name}

const vscode = require('vscode');
const path = require('path');
const fs = require('fs');
const {{ LanguageClient }} = require('vscode-languageclient/node');

let client;
let outputChannel;

// ── Baked at install time (absolute) — activation never depends on editor PATH ──
const BAKED_SERVER_PATH = {baked_exe};
const BAKED_PYTHON      = {baked_python};
const BAKED_MODULE      = {baked_module};
const BAKED_BIN_DIR     = {baked_bin};

/**
 * Resolve how to launch the LSP server, in priority order:
 *   1. Baked absolute path to the zolo-lsp console script (set by installer)
 *   2. PATH lookup via `which` (works when the editor is launched from a shell)
 *   3. Module form via the baked Python interpreter (`python -m zlsp.server...`)
 * Returns {{ command, args }} or null when nothing is usable.
 */
function resolveServer() {{
    if (BAKED_SERVER_PATH && fs.existsSync(BAKED_SERVER_PATH)) {{
        return {{ command: BAKED_SERVER_PATH, args: [], how: 'baked path' }};
    }}
    try {{
        const {{ execSync }} = require('child_process');
        const p = execSync('which zolo-lsp || where zolo-lsp', {{
            encoding: 'utf8',
            stdio: ['pipe', 'pipe', 'ignore']
        }}).trim();
        if (p) return {{ command: p.split(/\\r?\\n/)[0], args: [], how: 'PATH lookup' }};
    }} catch (err) {{ /* not on PATH — fall through */ }}
    if (BAKED_PYTHON && fs.existsSync(BAKED_PYTHON)) {{
        return {{ command: BAKED_PYTHON, args: ['-m', BAKED_MODULE], how: 'python -m' }};
    }}
    return null;
}}

/**
 * Show setup instructions when LSP server is missing
 */
async function showSetupInstructions() {{
    const choice = await vscode.window.showWarningMessage(
        'Zolo LSP server not found. Install it to enable semantic highlighting and LSP features.',
        'Open Terminal',
        'View Instructions',
        'Dismiss'
    );
    
    if (choice === 'Open Terminal') {{
        const terminal = vscode.window.createTerminal('Zolo LSP Setup');
        terminal.show();
        terminal.sendText('# Install Zolo LSP server:');
        terminal.sendText('pip install zlsp');
        terminal.sendText('# Then reload {self.editor_name}');
    }} else if (choice === 'View Instructions') {{
        vscode.env.openExternal(vscode.Uri.parse('https://github.com/zolomedia/zlsp#installation'));
    }}
}}

function activate(context) {{
    // Create output channel for debugging.
    // Must be a LogOutputChannel ({{ log: true }}) — vscode-languageclient v9+
    // calls .error()/.warn()/.info() on it; a plain OutputChannel lacks those
    // and throws "this.outputChannel.error is not a function" on client.start().
    outputChannel = vscode.window.createOutputChannel('Zolo LSP', {{ log: true }});
    outputChannel.appendLine('=== Zolo LSP Extension Activating ===');
    outputChannel.appendLine('Editor: {self.editor_name}');
    outputChannel.appendLine('Timestamp: ' + new Date().toISOString());
    
    // Resolve the server (PATH-independent: baked path → which → python -m)
    const resolved = resolveServer();
    
    if (!resolved) {{
        outputChannel.appendLine('✗ ERROR: zolo-lsp could not be located!');
        outputChannel.appendLine('  Baked path: ' + (BAKED_SERVER_PATH || '(none)'));
        outputChannel.appendLine('  Install with: pip install zlsp, then re-run zlsp-install-all');
        
        // Show user-friendly setup instructions
        showSetupInstructions();
        return;
    }}
    
    outputChannel.appendLine('[ok] Server resolved via ' + resolved.how + ': ' + resolved.command +
        (resolved.args.length ? ' ' + resolved.args.join(' ') : ''));
    
    // Augment PATH so the spawned server (and any child it needs) resolves tools
    // even when the editor was launched from the Dock with a minimal PATH.
    const augmentedEnv = Object.assign({{}}, process.env);
    const extraPaths = [BAKED_BIN_DIR, '/usr/local/bin', '/opt/homebrew/bin'].filter(Boolean);
    augmentedEnv.PATH = (augmentedEnv.PATH ? augmentedEnv.PATH + path.delimiter : '') +
        extraPaths.join(path.delimiter);
    
    // LSP server options (absolute command — independent of editor PATH)
    const serverOptions = {{
        command: resolved.command,
        args: resolved.args,
        options: {{
            env: augmentedEnv
        }}
    }};
    
    outputChannel.appendLine('Server command: ' + resolved.command);
    
    // Get trace setting from configuration
    const config = vscode.workspace.getConfiguration('zolo');
    const traceLevel = config.get('trace.server', 'messages');
    outputChannel.appendLine('Trace level: ' + traceLevel);
    
    // Client options (file patterns, synchronization, output channel)
    const clientOptions = {{
        documentSelector: [
            {{ scheme: 'file', language: 'zolo' }},
            {{ scheme: 'file', language: 'zolo-ui' }},
            {{ scheme: 'file', language: 'zolo-env' }},
            {{ scheme: 'file', language: 'zolo-server' }},
            {{ scheme: 'file', language: 'zolo-raven' }}
        ],
        synchronize: {{
            fileEvents: vscode.workspace.createFileSystemWatcher('**/*.zolo')
        }},
        outputChannel: outputChannel,
        traceOutputChannel: outputChannel,
        revealOutputChannelOn: 1, // RevealOutputChannelOn.Info (show on any message)
        initializationOptions: {{
            trace: traceLevel
        }},
        middleware: {{
            // Log semantic token requests/responses
            provideDocumentSemanticTokens: async (document, token, next) => {{
                outputChannel.appendLine('→ Requesting semantic tokens for: ' + document.fileName);
                const result = await next(document, token);
                if (result) {{
                    outputChannel.appendLine('[ok] Received semantic tokens (data length: ' + (result.data ? result.data.length : 0) + ')');
                }} else {{
                    outputChannel.appendLine('✗ No semantic tokens received');
                }}
                return result;
            }}
        }}
    }};
    
    outputChannel.appendLine('Creating LSP client...');
    
    // Create and start the LSP client
    client = new LanguageClient(
        'zoloLsp',
        'Zolo Language Server',
        serverOptions,
        clientOptions
    );
    
    // Log client state changes
    client.onDidChangeState((event) => {{
        outputChannel.appendLine('LSP State changed: ' + JSON.stringify({{
            oldState: event.oldState,
            newState: event.newState
        }}));
    }});
    
    outputChannel.appendLine('Starting LSP client...');
    
    client.start().then(() => {{
        outputChannel.appendLine('[ok] LSP client started successfully');
        outputChannel.appendLine('');
        outputChannel.appendLine('Semantic Token Legend:');
        client.initializeResult?.capabilities?.semanticTokensProvider?.legend?.tokenTypes?.forEach((type, i) => {{
            outputChannel.appendLine('  ' + i + ': ' + type);
        }});
    }}).catch((err) => {{
        outputChannel.appendLine('✗ Failed to start LSP client: ' + err);
        vscode.window.showErrorMessage('Zolo LSP failed to start: ' + err.message);
    }});
    
    // Register command to show output
    context.subscriptions.push(
        vscode.commands.registerCommand('zolo.showOutput', () => {{
            outputChannel.show();
        }})
    );
}}

function deactivate() {{
    if (outputChannel) {{
        outputChannel.appendLine('=== Zolo LSP Extension Deactivating ===');
    }}
    if (!client) {{
        return undefined;
    }}
    return client.stop();
}}

module.exports = {{
    activate,
    deactivate
}};
"""
        
        dest_path = base_dir / 'out' / 'extension.js'
        dest_path.write_text(code)
        
        return dest_path
    
    def install_npm_dependencies(self, base_dir):
        """Install required npm dependencies for the extension."""
        import subprocess
        
        print("  → Installing npm dependencies...")
        try:
            # Install vscode-languageclient (required for LSP)
            result = subprocess.run(
                ['npm', 'install', '--silent', 'vscode-languageclient'],
                cwd=base_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return True
            else:
                print(f"  ⚠ npm install warning: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print(f"  ⚠ npm install timed out")
            return False
        except FileNotFoundError:
            print(f"  ⚠ npm not found - install Node.js")
            return False
        except Exception as e:
            print(f"  ⚠ npm install failed: {e}")
            return False
    
    def install_extension_files(self, base_dir):
        """Generate and install all extension files."""
        installed = []
        
        # 1. Generate package.json
        try:
            self.generate_package_json(base_dir)
            installed.append("package.json (generated from theme)")
        except Exception as e:
            print(f"  ⚠ Failed to generate package.json: {e}")
        
        # 2. Generate language-configuration.json
        try:
            self.generate_language_configuration(base_dir)
            installed.append("language-configuration.json")
        except Exception as e:
            print(f"  ⚠ Failed to generate language-configuration.json: {e}")
        
        # 3. Generate TextMate grammar
        try:
            grammar = self.generator.generate_textmate_grammar()
            grammar_path = base_dir / 'syntaxes' / 'zolo.tmLanguage.json'
            with open(grammar_path, 'w') as f:
                json.dump(grammar, f, indent=2)
            installed.append(f"syntaxes/zolo.tmLanguage.json ({len(json.dumps(grammar))} bytes)")
        except Exception as e:
            print(f"  ⚠ Failed to generate TextMate grammar: {e}")
        
        # 4. Generate extension.js (LSP client)
        try:
            self.generate_extension_js(base_dir)
            installed.append("out/extension.js (LSP client)")
        except Exception as e:
            print(f"  ⚠ Failed to generate extension.js: {e}")
        
        # 5. Create README.md
        try:
            readme_content = f"""# Zolo Language Support for {self.editor_name}

LSP support for `.zolo` files with semantic highlighting.

## Features

- Semantic Highlighting: Context-aware syntax coloring
- Real-time Diagnostics: Instant error detection
- Hover Information: Documentation on hover
- Code Completion: Smart suggestions
- 5 Special File Types: zUI, zEnv, zSpark, zConfig, zSchema

## Installation

This extension was installed via:
```bash
pip install zlsp
zlsp-install-{self.dir_name.replace('.', '')}
```

## Requirements

- {self.editor_name} 1.75.0 or higher
- Python 3.8 or higher
- `zolo-lsp` command (included with zlsp)

## Usage

Open any `.zolo` file - the extension activates automatically!

## Theme

Generated from: {self.theme.name} v{self.theme.version}

## Version

{__version__}
"""
            readme_path = base_dir / 'README.md'
            readme_path.write_text(readme_content)
            installed.append("README.md")
        except Exception as e:
            print(f"  ⚠ Failed to generate README.md: {e}")
        
        # 6. Copy file type icons (base green + per-role tinted variants)
        try:
            assets_dir = Path(__file__).parent.parent.parent / 'assets'
            icons_dir = base_dir / 'icons'
            icons_dir.mkdir(exist_ok=True)
            icon_names = ['zolo_filetype.png'] + [
                f'zolo_filetype.{suffix}.png'
                for _, _, suffix, _ in self.ROLE_LANGUAGES
            ]
            copied = 0
            for name in icon_names:
                src = assets_dir / name
                if src.exists():
                    shutil.copy2(src, icons_dir / name)
                    copied += 1
                else:
                    print(f"  ⚠ Missing icon asset: {name}")
            installed.append(f"icons/ ({copied} file type icons)")
        except Exception as e:
            print(f"  ⚠ Failed to copy icons: {e}")
        
        return installed
    
    def register_extension_in_registry(self, ext_dir):
        """
        Register the extension in editor's extensions.json registry.
        
        Only used for Cursor IDE (VS Code doesn't need this).
        """
        if not self.requires_registry:
            return True
        
        cursor_extensions_dir = ext_dir.parent
        extensions_json_path = cursor_extensions_dir / 'extensions.json'
        
        # Generate UUIDs for the extension
        ext_uuid = str(uuid.uuid4())
        publisher_uuid = str(uuid.uuid4())
        
        # Create the extension entry.
        # CRITICAL: this MUST equal Cursor's canonical id = "<publisher>.<name>"
        # lowercased, derived from package.json (publisher "ZoloAi", name "zolo-lsp"
        # -> "zoloai.zolo-lsp"). A hyphenated "zolo-ai.zolo-lsp" here drifts from the
        # real id: on launch Cursor reads package.json, computes "zoloai.zolo-lsp",
        # finds it flagged in .obsolete, and garbage-collects the extension — the
        # "zLSP disappears after reboot" bug.
        ext_id = "zoloai.zolo-lsp"
        ext_entry = {
            "identifier": {
                "id": ext_id,
                "uuid": ext_uuid
            },
            "version": __version__,
            "location": {
                "$mid": 1,
                "path": str(ext_dir),
                "scheme": "file"
            },
            "relativeLocation": ext_dir.name,
            "metadata": {
                "installedTimestamp": int(datetime.now().timestamp() * 1000),
                "pinned": False,
                "source": "local",
                "id": ext_uuid,
                "publisherId": publisher_uuid,
                "publisherDisplayName": "Zolo Language Support",
                "targetPlatform": "undefined",
                "updated": False,
                "isPreReleaseVersion": False,
                "hasPreReleaseVersion": False
            }
        }
        
        # Read existing extensions.json
        if extensions_json_path.exists():
            with open(extensions_json_path, 'r', encoding='utf-8') as f:
                extensions_list = json.load(f)
        else:
            extensions_list = []
        
        # Remove any existing zolo-lsp entries (covers both the legacy hyphenated
        # "zolo-ai.*" id and the correct "zoloai.*" id)
        extensions_list = [ext for ext in extensions_list if not ext.get('identifier', {}).get('id', '').startswith('zolo')]
        
        # Add our extension
        extensions_list.append(ext_entry)
        
        # Write back
        with open(extensions_json_path, 'w', encoding='utf-8') as f:
            json.dump(extensions_list, f, indent=4)
        
        # Un-obsolete ourselves so the fresh install survives reboots.
        self._clear_obsolete_flags(cursor_extensions_dir)
        
        print(f"  [ok] Registered extension in {self.editor_name} registry")
        return True
    
    def _clear_obsolete_flags(self, cursor_extensions_dir):
        """Strip any zolo* entries from Cursor's `.obsolete` map.
        
        Cursor records uninstalled extensions in `.obsolete` and garbage-collects
        the matching folders on launch. A prior id drift left our *current* version
        flagged obsolete, so Cursor wiped the extension on every reboot. Clearing
        these on (re)install guarantees a fresh install is never treated as stale.
        """
        obsolete_path = cursor_extensions_dir / '.obsolete'
        if not obsolete_path.exists():
            return
        try:
            with open(obsolete_path, 'r', encoding='utf-8') as f:
                obsolete = json.load(f)
        except Exception:
            return
        if not isinstance(obsolete, dict):
            return
        pruned = {k: v for k, v in obsolete.items() if not k.lower().startswith('zolo')}
        if pruned != obsolete:
            with open(obsolete_path, 'w', encoding='utf-8') as f:
                json.dump(pruned, f, indent=4)
            print(f"  [ok] Cleared stale .obsolete entries in {self.editor_name}")
    
    def print_installation_instructions(self):
        """Print instructions for reloading the editor."""
        print()
        print("  ╔═══════════════════════════════════════════════════════════╗")
        print(f"  ║  Reload {self.editor_name} to Activate                              ║")
        print("  ╚═══════════════════════════════════════════════════════════╝")
        print()
        print(f"  Simply reload {self.editor_name}:")
        print("     Cmd+Shift+P → 'Reload Window'")
        print()
        print("  [ok] Extension activates automatically for .zolo files")
        print("  [ok] Semantic token colors injected into your settings")
        print(f"  [ok] Works with ANY {self.editor_name} theme!")
        print("  [ok] LSP provides diagnostics, hover, and completion")
        print()
    
    def install(self):
        """
        Main installation function - fully automated.
        
        Returns:
            0 on success, 1 on failure
        """
        print("═" * 70)
        print(f"  zlsp {self.editor_name} Integration Installer")
        print("  (Auto-loading, Non-Destructive, Theme-Driven)")
        print("═" * 70)
        print()
        
        # Step 1: Load theme
        print("[1/6] Loading color theme...")
        try:
            self.theme = load_theme('zolo_default')
            print(f"  [ok] Loaded theme: {self.theme.name} v{self.theme.version}")
        except Exception as e:
            print(f"  ✗ Failed to load theme: {e}")
            return 1
        
        print()
        
        # Step 2: Create generator
        print("[2/6] Creating extension generator...")
        try:
            self.generator = VSCodeGenerator(self.theme)
            print(f"  [ok] Generator ready")
        except Exception as e:
            print(f"  ✗ Failed to create generator: {e}")
            return 1
        
        print()
        
        # Step 3: Detect editor installation
        print(f"[3/6] Detecting {self.editor_name}...")
        editor_found, editor_status = self.check_editor_installed()
        self.extensions_dir = self.detect_extensions_dir()
        
        if editor_found:
            print(f"  [ok] {editor_status}")
        else:
            print(f"  ⚠ {editor_status}")
            print(f"    Extension will still be installed, but {self.editor_name}")
            print(f"    must be installed to use it.")
        
        print(f"  → Extensions: {self.extensions_dir}")
        print()
        
        # Step 4: Create extension directory
        print("[4/6] Installing extension files...")
        extension_dir = self.extensions_dir / f'zolo-lsp-{__version__}'
        
        # Remove ALL old zolo-lsp versions (not just current version)
        for old_ext in self.extensions_dir.glob('zolo-lsp-*'):
            if old_ext.is_dir():
                print(f"  → Removing old version: {old_ext.name}")
                shutil.rmtree(old_ext)
        
        try:
            self.create_extension_structure(extension_dir)
            installed = self.install_extension_files(extension_dir)
            
            for f in installed:
                print(f"  [ok] {f}")
            
            # Install npm dependencies (required for LSP client)
            if self.install_npm_dependencies(extension_dir):
                print(f"  [ok] npm dependencies installed")
            else:
                print(f"  ⚠ npm dependencies failed (extension may not work)")
            
            # Register in registry if needed (Cursor only)
            self.register_extension_in_registry(extension_dir)
        except Exception as e:
            print(f"  ✗ Failed to install files: {e}")
            return 1
        
        print()
        
        # Step 5: Inject semantic token colors into user settings
        print("[5/6] Configuring semantic token colors...")
        try:
            self.settings_path = self.detect_user_settings()
            print(f"  → Settings: {self.settings_path}")
            
            # Generate color rules from theme
            rules = self.generate_semantic_token_rules()
            
            # Inject into settings.json
            if self.inject_semantic_token_colors(rules):
                print(f"  [ok] Injected {len(rules)} token color rules")
                print(f"  [ok] Colors persist across all {self.editor_name} sessions")
            else:
                print(f"  ⚠ Failed to inject colors (extension still works)")
        except Exception as e:
            print(f"  ⚠ Failed to configure colors: {e}")
            print(f"    Extension will still work with TextMate grammar")
        
        print()
        
        # Step 6: Verify requirements
        print("[6/6] Verifying installation...")
        
        # Check if zolo-lsp is available
        lsp_found, lsp_status = self.check_zolo_lsp_available()
        if lsp_found:
            print(f"  [ok] {lsp_status}")
        else:
            print(f"  ⚠ {lsp_status}")
            print(f"    Run: pip install zlsp")
        
        print()
        print("═" * 70)
        
        if lsp_found:
            print("  [ok] Installation Complete!")
        else:
            print("  ⚠ Installation Complete (zolo-lsp setup needed)")
        
        print("═" * 70)
        print()
        
        # Print usage
        if lsp_found:
            print("Ready to use!")
            print()
            print("Next steps:")
            self.print_installation_instructions()
            
            print("Features:")
            print("  • Semantic highlighting (context-aware colors)")
            print("  • Real-time diagnostics")
            print("  • Hover info (documentation)")
            print("  • Auto-completion")
            print("  • All 5 special file types (zUI, zEnv, zSpark, zConfig, zSchema)")
            print()
        else:
            print("Extension installed, but LSP server not available")
            print()
            print("To enable full LSP features:")
            print("  1. Install zlsp: pip install zlsp")
            print("  2. Verify: which zolo-lsp")
            print(f"  3. Reload {self.editor_name}")
        
        print()
        return 0 if lsp_found else 1
