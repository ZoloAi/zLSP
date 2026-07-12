"""
Documentation Registry - Single Source of Truth

This is the ONLY place where documentation is defined.
All providers (hover, completion) use this registry.

Eliminates 249 lines of duplication between hover_provider.py and completion_provider.py!
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum
from .key_classifications import is_block_key as _is_block_key


class DocumentationType(Enum):
    """Type of documentation entry."""
    TYPE_HINT = "type_hint"
    SPECIAL_KEY = "special_key"
    UI_ELEMENT = "ui_element"
    ZOS_DATA = "zos_data"
    VALUE = "value"


@dataclass
class Documentation:
    """
    Unified documentation entry.
    
    Used for type hints, special keys, UI elements, etc.
    Supports both hover and completion generation.
    """
    label: str
    title: str
    description: str
    example: str
    doc_type: DocumentationType
    category: Optional[str] = None

    def to_hover_markdown(self) -> str:
        """Convert to Markdown for hover display."""
        return f"**{self.title}**\n\n{self.description}\n\nExample: `{self.example}`"

    def to_completion_detail(self) -> str:
        """Get short detail for completion item."""
        return self.title

    def to_completion_documentation(self) -> str:
        """Get full documentation for completion item."""
        return f"{self.description}\n\nExample: `{self.example}`"


class DocumentationRegistry:
    """
    Central registry for all documentation.
    
    Single Source of Truth (SSOT) - change once, affects all providers!
    """

    _registry: Dict[str, Documentation] = {}

    @classmethod
    def register(cls, key: str, doc: Documentation) -> None:
        """Register documentation entry."""
        cls._registry[key] = doc

    @classmethod
    def get(cls, key: str) -> Optional[Documentation]:
        """Get documentation by key."""
        return cls._registry.get(key)

    @classmethod
    def get_by_type(cls, doc_type: DocumentationType) -> List[Documentation]:
        """Get all documentation of a specific type."""
        return [
            doc for doc in cls._registry.values()
            if doc.doc_type == doc_type
        ]

    @classmethod
    def get_by_category(cls, category: str) -> List[Documentation]:
        """Get all documentation for a specific category."""
        return [
            doc for doc in cls._registry.values()
            if doc.category == category
        ]

    @classmethod
    def all(cls) -> List[Documentation]:
        """Get all registered documentation."""
        return list(cls._registry.values())

    @classmethod
    def clear(cls) -> None:
        """Clear registry (for testing)."""
        cls._registry.clear()

    @classmethod
    def is_block_key(cls, key: str) -> bool:
        """
        Check if a key is a block-level key (expects nested properties).
        
        Delegates to key_classifications module for centralized classification.
        
        Args:
            key: Key name to check
        
        Returns:
            True if key should not have inline value completions
        
        Examples:
            >>> DocumentationRegistry.is_block_key('zImage')
            True
            >>> DocumentationRegistry.is_block_key('title')
            False
        """
        return _is_block_key(key)


# ============================================================================
# SSOT: Type Hint Documentation (12 entries)
# ============================================================================

TYPE_HINTS = [
    Documentation(
        label="int",
        title="Integer Number",
        description="Convert value to integer.",
        example="port(int): 8080",
        doc_type=DocumentationType.TYPE_HINT
    ),
    Documentation(
        label="float",
        title="Floating Point Number",
        description="Convert value to float.",
        example="pi(float): 3.14159",
        doc_type=DocumentationType.TYPE_HINT
    ),
    Documentation(
        label="bool",
        title="Boolean",
        description="Convert value to boolean (true/false).",
        example="enabled(bool): true",
        doc_type=DocumentationType.TYPE_HINT
    ),
    Documentation(
        label="str",
        title="String",
        description="Explicitly mark value as string. Also enables multi-line YAML-style content collection.",
        example="description(str): My App",
        doc_type=DocumentationType.TYPE_HINT
    ),
    Documentation(
        label="list",
        title="List/Array",
        description="Ensure value is a list.",
        example="items(list): [1, 2, 3]",
        doc_type=DocumentationType.TYPE_HINT
    ),
    Documentation(
        label="dict",
        title="Dictionary/Object",
        description="Ensure value is a dictionary.",
        example="config(dict): {key: value}",
        doc_type=DocumentationType.TYPE_HINT
    ),
    Documentation(
        label="null",
        title="Null Value",
        description="Set value to null/None.",
        example="optional(null):",
        doc_type=DocumentationType.TYPE_HINT
    ),
    Documentation(
        label="raw",
        title="Raw String",
        description="String without escape sequence processing.",
        example="regex(raw): \\d+",
        doc_type=DocumentationType.TYPE_HINT
    ),
    Documentation(
        label="date",
        title="Date String",
        description="Date value (semantic hint).",
        example="created(date): 2024-01-06",
        doc_type=DocumentationType.TYPE_HINT
    ),
    Documentation(
        label="time",
        title="Time String",
        description="Time value (semantic hint).",
        example="starts(time): 14:30:00",
        doc_type=DocumentationType.TYPE_HINT
    ),
    Documentation(
        label="url",
        title="URL String",
        description="URL value (semantic hint).",
        example="homepage(url): https://example.com",
        doc_type=DocumentationType.TYPE_HINT
    ),
    Documentation(
        label="path",
        title="Path String",
        description="File path (semantic hint).",
        example="config(path): /etc/app/config.zolo",
        doc_type=DocumentationType.TYPE_HINT
    ),
]

# ============================================================================
# SSOT: Common Value Documentation
# ============================================================================

COMMON_VALUES = [
    Documentation(
        label="true",
        title="Boolean true",
        description="Use with (bool) type hint for boolean values.",
        example="enabled(bool): true",
        doc_type=DocumentationType.VALUE
    ),
    Documentation(
        label="false",
        title="Boolean false",
        description="Use with (bool) type hint for boolean values.",
        example="disabled(bool): false",
        doc_type=DocumentationType.VALUE
    ),
    # Note: "null" is registered as TYPE_HINT, not VALUE
]

# ============================================================================
# SSOT: Special Key Documentation (zSpark, zEnv, zUI, zSchema)
# ============================================================================

SPECIAL_KEYS = [
    Documentation(
        label="zMode",
        title="zMode (Execution Mode)",
        description="Sets execution mode: zCLI or zBifrost.",
        example="zMode: zCLI",
        doc_type=DocumentationType.SPECIAL_KEY,
        category="zSpark"
    ),
    Documentation(
        label="zEnv",
        title="Deployment Environment",
        description="Names the active environment — loads zEnv.<name>.zolo over zEnv.base.zolo. Modes: Production, Development, Testing, Debug (lowercase accepted).",
        example="zEnv: development",
        doc_type=DocumentationType.SPECIAL_KEY,
        category="zSpark"
    ),
    Documentation(
        label="zState",
        title="Deployment Environment (deprecated → zEnv)",
        description="Deprecated. Use zEnv instead.",
        example="zEnv: Production",
        doc_type=DocumentationType.SPECIAL_KEY,
        category="zSpark"
    ),
    Documentation(
        label="zLog",
        title="Logger Level",
        description="Logging level: DEBUG, SESSION, INFO, WARNING, ERROR, CRITICAL, PROD. z-prefix (zINFO…) adds engine trace.",
        example="zLog: INFO",
        doc_type=DocumentationType.SPECIAL_KEY,
        category="zSpark"
    ),
    Documentation(
        label="zLogPath",
        title="Log Path",
        description="Directory for log files (zPath syntax).",
        example="zLogPath: @.logs",
        doc_type=DocumentationType.SPECIAL_KEY,
        category="zSpark"
    ),
    Documentation(
        label="zScrapath",
        title="Log Path (deprecated → zLogPath)",
        description="Deprecated. Use zLogPath instead.",
        example="zLogPath: @.logs",
        doc_type=DocumentationType.SPECIAL_KEY,
        category="zSpark"
    ),
    Documentation(
        label="zScrap",
        title="Logger Level (deprecated → zLog)",
        description="Deprecated. Use zLog instead.",
        example="zLog: INFO",
        doc_type=DocumentationType.SPECIAL_KEY,
        category="zSpark"
    ),
    Documentation(
        label="zLogger",
        title="App Log Event",
        description="Emit an app-level log. Shorthand: zLogger: message (INFO). Nested: message/level/tag.",
        example="zLogger: Order saved\n# or:\nzLogger:\n    message: Order saved\n    level: WARNING\n    tag: crm.orders",
        doc_type=DocumentationType.SPECIAL_KEY,
        category="zUI"
    ),
    Documentation(
        label="zMeta",
        title="zMeta (Metadata Block)",
        description="Metadata block for zUI and zSchema files.",
        example="zMeta:\n  Data_Type: User",
        doc_type=DocumentationType.SPECIAL_KEY,
        category="zOS"
    ),
    Documentation(
        label="zGate",
        title="zGate (Access & Conditional Gate)",
        description=(
            "The one gate verb — a yes/no question asked before a block renders or "
            "an action runs. Auth: authed / role / require. Value: %token with "
            "zAbove/zBelow/zIN/zBetween/zNull/zSet. Combine with zAll/zAny/zNot."
        ),
        example="zGate:\n  authed: true",
        doc_type=DocumentationType.SPECIAL_KEY,
        category="zOS"
    ),
    Documentation(
        label="zRBAC",
        title="zRBAC (DEPRECATED → zGate)",
        description="Deprecated access-control block — folded into the zGate verb. Use zGate.",
        example="zGate:\n  authed: true",
        doc_type=DocumentationType.SPECIAL_KEY,
        category="zEnv"
    ),
    # ── Identity (doc 21) ────────────────────────────────────────────────
    Documentation(
        label="zLogin",
        title="zLogin (Sign-in front desk)",
        description=(
            "A zDialog whose submit runs the zAuth login action — renders the form, "
            "verifies against your user model (bcrypt), writes session['zVisitor']. "
            "Props: model (required), fields/inputs, title, zAPI, onSuccess, zApp."
        ),
        example="zLogin:\n  model: @.models.zSchema.users\n  fields: [email, password]",
        doc_type=DocumentationType.SPECIAL_KEY,
        category="zUI"
    ),
    Documentation(
        label="zLogout",
        title="zLogout (Sign-out)",
        description="Clears session['zVisitor'] + the durable token, then lands home. Gate the link with zGate: {authed: true}.",
        example="zLogout: myapp",
        doc_type=DocumentationType.SPECIAL_KEY,
        category="zUI"
    ),
    # ── Data (docs 16, 17) ───────────────────────────────────────────────
    Documentation(
        label="zData",
        title="zData (Declarative data action)",
        description=(
            "One block for the data lifecycle. action: insert|read|update|delete|upsert|"
            "aggregate|window|set|create|drop|truncate|index|refresh. Keys: model, data, "
            "fields, values, where, zFilters, order_by, limit, offset, joins, group_by, returning…"
        ),
        example="zData:\n  action: read\n  model:  @.models.zSchema.crm.contacts",
        doc_type=DocumentationType.SPECIAL_KEY,
        category="zUI"
    ),
    Documentation(
        label="zDialog",
        title="zDialog (Form / collect-then-submit)",
        description="Gathers inputs + controls and, onSubmit, hands zConv to an action. Props: title, fields, onSubmit, zReset, model.",
        example="zDialog:\n  fields: [name, email]\n  onSubmit:\n    zData: { action: insert }",
        doc_type=DocumentationType.SPECIAL_KEY,
        category="zUI"
    ),
    Documentation(
        label="zWizard",
        title="zWizard (Multi-step flow)",
        description="A block of named steps run in order. Each step's answer files under its name → zHat[Step]. zGate: skips a step (legacy if: is deprecated); a gate event (zBtn submit / zDialog) holds the walk. _transaction: true wraps zData steps.",
        example="zWizard:\n  Ask_Name:\n    zInput: Your name\n  Say_Hi:\n    zText: Hello",
        doc_type=DocumentationType.SPECIAL_KEY,
        category="zUI"
    ),
    Documentation(
        label="zFunc",
        title="zFunc (Function call)",
        description="Point at a function; zOS runs it on render. &.plugin.fn(args) searches plugins; @.path.file.fn is exact; builtins &zNow / &zUUID(). Return surfaces as a zSignal.",
        example="zFunc: &.calc.add(2, 3)",
        doc_type=DocumentationType.SPECIAL_KEY,
        category="zUI"
    ),
    # ── Navigation verbs (doc 14) ────────────────────────────────────────
    Documentation(
        label="zAlpha",
        title="zAlpha (Cross-file hop)",
        description="Hand it a zPath; zOS loads that file and runs from that block — the workhorse behind menu picks and page-changing buttons.",
        example="zAlpha: @.zViews.zUI.Home.Home",
        doc_type=DocumentationType.SPECIAL_KEY,
        category="zUI"
    ),
    Documentation(
        label="zDelta",
        title="zDelta (Same-file hop)",
        description="Run another block in THIS file with $Block — nothing loads, the route never moves, reversible with zBack.",
        example="zDelta: $Section_Two",
        doc_type=DocumentationType.SPECIAL_KEY,
        category="zUI"
    ),
    Documentation(
        label="zOmega",
        title="zOmega (Land on a zKey)",
        description="An adjective on a zAlpha/zDelta saying WHERE in the block to arrive — matches a block's direct key; scrolls (browser) / opens at that key (terminal). Also rides zURL href (#zKey) and zModal landings.",
        example="zOmega: Pricing",
        doc_type=DocumentationType.SPECIAL_KEY,
        category="zUI"
    ),
    Documentation(
        label="zModal",
        title="zModal (Detour with auto-return)",
        description=(
            "Run a block as a DETOUR and auto-return to the firing point on completion — a glance, not a move "
            "(no crumb, route never changes). Value forms: inline dict {zH2: ...}, $Block (same file), "
            "@.zViews… zPath (cross-file), or longhand {zUI: <target>, params: {...}}. "
            "Fires from a menu option's value or a zBtn action (action: zModal($Block))."
        ),
        example="zModal: $Details",
        doc_type=DocumentationType.SPECIAL_KEY,
        category="zUI"
    ),
    Documentation(
        label="zDelegate",
        title="zDelegate (In-place block swap)",
        description="A button rewires its click to run another block from the same file, right in place — same page, same route. $Block (routeless) / $Block.Sub (dotted → render in place).",
        example="zDelegate: $Editor.Form",
        doc_type=DocumentationType.SPECIAL_KEY,
        category="zUI"
    ),
    # ── zLoom dynamic content (doc 18) ───────────────────────────────────
    Documentation(
        label="zSpool",
        title="zSpool (Data reel binding)",
        description="Bind a block to a named reel (zLoom/spools/) so %data.<name>.<field> resolves. Also the reel key inside zShuttle.",
        example="zMeta:\n  zSpool: [contacts]",
        doc_type=DocumentationType.SPECIAL_KEY,
        category="zUI"
    ),
    Documentation(
        label="zShuttle",
        title="zShuttle (Loop one pattern over a list)",
        description="Weave one copy of a zPattern per row of a reel. { zSpool: <list reel>, zPattern: <name> } (+ optional per-row zGate). Lowers to zList {source, each}.",
        example="zShuttle:\n  zSpool:   products\n  zPattern: Card",
        doc_type=DocumentationType.SPECIAL_KEY,
        category="zUI"
    ),
    Documentation(
        label="zKnot",
        title="zKnot (Computed value)",
        description="Tie % threads + literals into one value. Ops: zAdd zSub zMul zDiv zJoin zIf. Nestable; ÷0/bad op → empty.",
        example="zKnot:\n  zJoin: [Total: $, {zMul: [%item.price, 2]}]",
        doc_type=DocumentationType.SPECIAL_KEY,
        category="zUI"
    ),
    Documentation(
        label="zVar",
        title="zVar (Durable session value)",
        description="Set a session value read as %var.<name> (or bare %name). Supports _navigate: <path> for immediate navigation after writing.",
        example="zVar: { contact_id: %zConv.id }",
        doc_type=DocumentationType.SPECIAL_KEY,
        category="zUI"
    ),
    # ── zUI zMeta config keys ────────────────────────────────────────────
    Documentation(
        label="zTitle",
        title="zTitle (Page title)",
        description="The page's display title, declared in zMeta.",
        example="zMeta:\n  zTitle: My Page",
        doc_type=DocumentationType.SPECIAL_KEY,
        category="zUI"
    ),
    Documentation(
        label="zBrush",
        title="zBrush (Page style classes)",
        description="Page-level style class list applied across the view, declared in zMeta.",
        example="zMeta:\n  zBrush: [page, hub]",
        doc_type=DocumentationType.SPECIAL_KEY,
        category="zUI"
    ),
]

# ============================================================================
# Auto-Register All Documentation
# ============================================================================

for doc_entry in TYPE_HINTS + COMMON_VALUES + SPECIAL_KEYS:
    DocumentationRegistry.register(doc_entry.label, doc_entry)
