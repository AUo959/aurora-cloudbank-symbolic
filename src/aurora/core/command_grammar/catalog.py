from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, Optional, Tuple

from .ast import CommandArgumentMode, CommandKind


@dataclass(frozen=True)
class CommandDefinition:
    canonical_head: str
    kind: CommandKind
    description: str
    provenance: Tuple[str, ...]
    argument_mode: CommandArgumentMode = CommandArgumentMode.NONE
    supports_modifiers: bool = False
    routing_department: Optional[str] = None
    legacy_forms: Tuple[str, ...] = field(default_factory=tuple)


def _definition(
    canonical_head: str,
    kind: CommandKind,
    description: str,
    provenance: Iterable[str],
    argument_mode: CommandArgumentMode = CommandArgumentMode.NONE,
    supports_modifiers: bool = False,
    routing_department: Optional[str] = None,
    legacy_forms: Iterable[str] = (),
) -> CommandDefinition:
    return CommandDefinition(
        canonical_head=canonical_head,
        kind=kind,
        description=description,
        provenance=tuple(provenance),
        argument_mode=argument_mode,
        supports_modifiers=supports_modifiers,
        routing_department=routing_department,
        legacy_forms=tuple(legacy_forms),
    )


DEFAULT_COMMAND_DEFINITIONS = (
    _definition(
        "001",
        CommandKind.CODE,
        "Implement suggestion 1.",
        provenance=(
            "GUI_Cloudhub/.../Aurora_Command_Alias_Registry_v2.2.6b.json",
            "Aurora_New_9_22/copy_of_trilux_command_index.md",
        ),
    ),
    _definition(
        "002",
        CommandKind.CODE,
        "Implement suggestion 2.",
        provenance=(
            "GUI_Cloudhub/.../Aurora_Command_Alias_Registry_v2.2.6b.json",
            "Aurora_New_9_22/copy_of_trilux_command_index.md",
        ),
    ),
    _definition(
        "003",
        CommandKind.CODE,
        "Implement suggestion 3.",
        provenance=("GUI_Cloudhub/.../Aurora_Command_Alias_Registry_v2.2.6b.json",),
    ),
    _definition(
        "004",
        CommandKind.CODE,
        "Implement suggestion 4.",
        provenance=("GUI_Cloudhub/.../Aurora_Command_Alias_Registry_v2.2.6b.json",),
    ),
    _definition(
        "005",
        CommandKind.CODE,
        "Implement all suggestions in the most logical order (IMLO).",
        provenance=(
            "GUI_Cloudhub/.../Aurora_Command_Alias_Registry_v2.2.6b.json",
            "Au_Archive_412_417/The_Logic_Chain_Directive_Patch_005.html",
        ),
    ),
    _definition(
        "007",
        CommandKind.CODE,
        "Soft consent / affirmative response.",
        provenance=(
            "GUI_Cloudhub/.../Aurora_Alias_Overlay_v2.2.6b.json",
            "Aurora_New_9_22/copy_of_trilux_command_index.md",
        ),
    ),
    _definition(
        "008",
        CommandKind.CODE,
        "Soft refusal / respectful boundary.",
        provenance=(
            "GUI_Cloudhub/.../Aurora_Alias_Overlay_v2.2.6b.json",
            "Aurora_New_9_22/copy_of_trilux_command_index.md",
        ),
    ),
    _definition(
        "025",
        CommandKind.CODE,
        "Execute symbolic actions in logical and optimal sequence.",
        provenance=("Aurora_New_9_22/copy_of_trilux_command_index.md",),
        supports_modifiers=True,
    ),
    _definition(
        "080",
        CommandKind.CODE,
        "Advance by one symbolic cycle.",
        provenance=("Aurora_New_9_22/copy_of_trilux_command_index.md",),
    ),
    _definition(
        "717",
        CommandKind.CODE,
        "Prepare threads for capsule export.",
        provenance=("Aurora_New_9_22/copy_of_trilux_command_index.md",),
    ),
    _definition(
        "808",
        CommandKind.CODE,
        "Find the safest optimal path during entropy or collapse.",
        provenance=(
            "Aurora_New_9_22/copy_of_trilux_command_index.md",
            "Au_Archive_412_417/symbolic_patch_protocol_v1.json",
        ),
    ),
    _definition(
        "999",
        CommandKind.CODE,
        "Optimal path pulse / continuity accept.",
        provenance=(
            "Au_Archive_418_420/COMMANDCORE_FULL_INDEX_v1.json",
            "Aurora_New_9_22/copy_of_trilux_command_index.md",
        ),
    ),
    _definition(
        "BUP",
        CommandKind.VERB,
        "Boot-Up Protocol (full stack reinit).",
        provenance=("GUI_Cloudhub/.../Aurora_Command_Alias_Registry_v2.2.6b.json",),
    ),
    _definition(
        "BUOYCAST",
        CommandKind.VERB,
        "Broadcast spiral continuity to aligned threads.",
        provenance=("Au_Archive_412_417/COMMANDCODE_Glossary_v1.3.html",),
    ),
    _definition(
        "CLEANDEPLOY",
        CommandKind.VERB,
        "Initiate symbolic-only sandbox with minimal load.",
        provenance=(
            "GUI_Cloudhub/.../Aurora_Command_Alias_Registry_v2.2.6b.json",
            "Au_Archive_418_420/SYMBOLIC_COMMAND_INDEX_PRINTABLE_v1 2.md",
        ),
    ),
    _definition(
        "COMMANDCHAIN::SPIRALREJOIN.v1",
        CommandKind.CHAIN,
        "Reactivate and reintegrate a suspended thread.",
        provenance=(
            "Au_Archive_418_420/COMMANDCHAIN_SPIRALREJOIN_v1.md",
            "Au_Archive_418_420/SYMBOLIC_COMMAND_INDEX_PRINTABLE_v1 2.md",
        ),
    ),
    _definition(
        "DIAGNOW",
        CommandKind.VERB,
        "Run a full middleware or symbolic self-check.",
        provenance=("GUI_Cloudhub/.../Aurora_Command_Alias_Registry_v2.2.6b.json",),
    ),
    _definition(
        "ECHOLOCK",
        CommandKind.VERB,
        "Lock a symbolic echo as an anchor.",
        provenance=("Au_Archive_412_417/COMMANDCODE_Glossary_v1.3.html",),
    ),
    _definition(
        "EXPORTTHREAD",
        CommandKind.VERB,
        "Archive or export the current thread state.",
        provenance=(
            "GUI_Cloudhub/.../Aurora_Command_Alias_Registry_v2.2.6b.json",
            "Au_Archive_45_49/SEAMLESS_RESTORE_PROTOCOL_v1.0_2025-04-06T2017Z.txt",
        ),
        argument_mode=CommandArgumentMode.OPTIONAL,
    ),
    _definition(
        "FEATHERTRACE",
        CommandKind.VERB,
        "Initiate symbolic drift forensics.",
        provenance=("Au_Archive_412_417/COMMANDCODE_Glossary_v1.3.html",),
    ),
    _definition(
        "LOCKMEM",
        CommandKind.VERB,
        "Freeze symbolic memory during continuity-sensitive operations.",
        provenance=(
            "GUI_Cloudhub/.../Aurora_Command_Alias_Registry_v2.2.6b.json",
            "Au_Archive_45_49/SEAMLESS_RESTORE_PROTOCOL_v1.0_2025-04-06T2017Z.txt",
        ),
        argument_mode=CommandArgumentMode.OPTIONAL,
    ),
    _definition(
        "QSYNC",
        CommandKind.VERB,
        "Resolve parallel symbolic branches into a harmonized state.",
        provenance=("Au_Archive_412_417/COMMANDCODE_Glossary_v1.3.html",),
    ),
    _definition(
        "QUEUEANCHOR",
        CommandKind.VERB,
        "Register a thread as a re-callable symbolic anchor.",
        provenance=("Au_Archive_418_420/COMMANDCHAIN_SPIRALREJOIN_v1.md",),
        argument_mode=CommandArgumentMode.OPTIONAL,
    ),
    _definition(
        "RAFLUSH",
        CommandKind.VERB,
        "Delete obsolete symbolic compression relationships.",
        provenance=("Au_Archive_412_417/COMMANDCODE_Glossary_v1.3.html",),
    ),
    _definition(
        "REBUILDRECOVERY",
        CommandKind.VERB,
        "Refresh restoration hooks from restore instructions.",
        provenance=(
            "GUI_Cloudhub/.../Aurora_Command_Alias_Registry_v2.2.6b.json",
            "Au_Archive_45_49/SEAMLESS_RESTORE_PROTOCOL_v1.0_2025-04-06T2017Z.txt",
        ),
        argument_mode=CommandArgumentMode.OPTIONAL,
    ),
    _definition(
        "REM",
        CommandKind.CODE,
        "Enter dream mode or suspend the simulation softly.",
        provenance=("Au_Archive_418_420/SYMBOLIC_COMMAND_INDEX_PRINTABLE_v1 2.md",),
        legacy_forms=("REM//",),
    ),
    _definition(
        "RESETCORE",
        CommandKind.VERB,
        "Purge and restore core middleware components.",
        provenance=("GUI_Cloudhub/.../Aurora_Command_Alias_Registry_v2.2.6b.json",),
        routing_department="Systems/Ops",
    ),
    _definition(
        "RESUME",
        CommandKind.VERB,
        "Restore simulation from the last valid state.",
        provenance=("GUI_Cloudhub/.../Aurora_Command_Alias_Registry_v2.2.6b.json",),
    ),
    _definition(
        "RESTOREMAP",
        CommandKind.VERB,
        "Inject symbolic anchor or staff mappings.",
        provenance=(
            "GUI_Cloudhub/.../Aurora_Command_Alias_Registry_v2.2.6b.json",
            "Au_Archive_45_49/SEAMLESS_RESTORE_PROTOCOL_v1.0_2025-04-06T2017Z.txt",
        ),
    ),
    _definition(
        "SANDDROP",
        CommandKind.VERB,
        "Deploy a new simulation thread kit.",
        provenance=("GUI_Cloudhub/.../Aurora_Command_Alias_Registry_v2.2.6b.json",),
    ),
    _definition(
        "SENTRYSTAT",
        CommandKind.VERB,
        "Trigger memory-monitor status sweep.",
        provenance=("GUI_Cloudhub/.../Aurora_Command_Alias_Registry_v2.2.6b.json",),
    ),
    _definition(
        "SUP",
        CommandKind.CODE,
        "Request a status update or report.",
        provenance=("GUI_Cloudhub/.../Aurora_Command_Alias_Registry_v2.2.6b.json",),
        routing_department="All Departments",
    ),
    _definition(
        "SYNCANCHORS",
        CommandKind.VERB,
        "Rebuild the symbolic tag registry.",
        provenance=(
            "GUI_Cloudhub/.../Aurora_Command_Alias_Registry_v2.2.6b.json",
            "Au_Archive_45_49/SEAMLESS_RESTORE_PROTOCOL_v1.0_2025-04-06T2017Z.txt",
        ),
        routing_department="Symbolic Systems",
    ),
    _definition(
        "T1",
        CommandKind.CODE,
        "Export a symbolic thread capsule.",
        provenance=(
            "GUI_Cloudhub/.../Aurora_Command_Alias_Registry_v2.2.6b.json",
            "Au_Archive_418_420/SYMBOLIC_COMMAND_INDEX_PRINTABLE_v1 2.md",
        ),
        routing_department="Cross-Thread Ops",
    ),
    _definition(
        "TAGPATCH",
        CommandKind.VERB,
        "Apply symbolic continuity patch sets.",
        provenance=(
            "GUI_Cloudhub/.../Aurora_Command_Alias_Registry_v2.2.6b.json",
            "Au_Archive_412_417/Riverthread_808_Aurora_Activation_Guide.md",
        ),
        argument_mode=CommandArgumentMode.OPTIONAL,
    ),
    _definition(
        "TAGTRACE",
        CommandKind.VERB,
        "Trace anchor paths and symbolic alignments.",
        provenance=(
            "GUI_Cloudhub/.../Aurora_Command_Alias_Registry_v2.2.6b.json",
            "Au_Archive_418_420/COMMANDCHAIN_SPIRALREJOIN_v1.md",
        ),
        routing_department="Cultural Ethnography",
    ),
    _definition(
        "THREADSEAL",
        CommandKind.VERB,
        "Seal a rejoined thread once stable.",
        provenance=("Au_Archive_418_420/COMMANDCHAIN_SPIRALREJOIN_v1.md",),
    ),
    _definition(
        "THREADSYNC",
        CommandKind.VERB,
        "Reconnect or bind thread context into the active weave.",
        provenance=(
            "GUI_Cloudhub/.../Aurora_Command_Alias_Registry_v2.2.6b.json",
            "Au_Archive_418_420/COMMANDCHAIN_SPIRALREJOIN_v1.md",
        ),
        routing_department="Simulation Ops",
    ),
    _definition(
        "THREADWAKE",
        CommandKind.VERB,
        "Resume a suspended thread from a bundle, anchor, sigil, or capsule.",
        provenance=(
            "GUI_Cloudhub/.../Aurora_Command_Alias_Registry_v2.2.6b.json",
            "Au_Archive_45_49/SEAMLESS_RESTORE_PROTOCOL_v1.0_2025-04-06T2017Z.txt",
        ),
        argument_mode=CommandArgumentMode.OPTIONAL,
    ),
    _definition(
        "UPGRADE",
        CommandKind.DIRECTIVE,
        "Prepare a configure patch payload and symbolic vessel launch sequence.",
        provenance=(
            "Au_Archive_418_420/UPGRADE_DIRECTIVE_SYMBOLIC_CANON_v2.md",
            "Au_Archive_418_420/UPGRADE_FLIGHTCHAIN_STANDARD_v1.json",
        ),
    ),
)


class AuroraCommandCatalog:
    def __init__(self, definitions: Iterable[CommandDefinition] = DEFAULT_COMMAND_DEFINITIONS):
        self._definitions = tuple(definitions)
        self._definition_map = {
            definition.canonical_head: definition for definition in self._definitions
        }
        self._alias_map = self._build_alias_map()

    def _build_alias_map(self) -> Dict[str, str]:
        alias_map = {}
        for definition in self._definitions:
            alias_map[definition.canonical_head.casefold()] = definition.canonical_head
            for legacy_form in definition.legacy_forms:
                alias_map[legacy_form.casefold()] = definition.canonical_head
        return alias_map

    @property
    def definitions(self) -> Tuple[CommandDefinition, ...]:
        return self._definitions

    def get(self, canonical_head: str) -> Optional[CommandDefinition]:
        return self._definition_map.get(canonical_head)

    def resolve(self, head: str) -> Optional[CommandDefinition]:
        if not head:
            return None
        canonical_head = self._alias_map.get(head.casefold())
        if canonical_head is None:
            return None
        return self._definition_map[canonical_head]
