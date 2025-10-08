"""Utilities to transform PACO parse trees into RegionModule structures.

This module re-implements the small subset of functionality that the
simulator expects when converting the parse tree dictionary returned by
PACO into an internal *RegionModule* representation.  We vendor this file
inside the repository so the simulator code is available even when the
original git submodule cannot be fetched (for example, when developing in
an offline or firewalled environment).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

__all__ = [
    "RegionModule",
    "RegionModuleNode",
    "RegionModuleError",
    "build_region_module",
    "region_module_to_dict",
]


class RegionModuleError(ValueError):
    """Raised when the parse-tree dictionary cannot be converted."""


@dataclass(slots=True)
class RegionModuleNode:
    """Single node contained inside a :class:`RegionModule`.

    Parameters
    ----------
    id:
        Identifier taken from the original parse tree.
    type:
        Node type (``task``, ``sequential``, ``parallel``, ``choice``,
        ``nature`` or ``loop``).
    label:
        Optional display label (tasks and gateways with names expose this
        field).
    index_in_parent:
        Position of the node inside the parent's ``children`` collection.
    metadata:
        Extra attributes preserved from the parse tree (e.g. ``impacts`` or
        ``max_delay``).
    children:
        Nested :class:`RegionModuleNode` objects.
    """

    id: int
    type: str
    label: Optional[str] = None
    index_in_parent: Optional[int] = None
    metadata: MutableMapping[str, Any] = field(default_factory=dict)
    children: List["RegionModuleNode"] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Serialise the node into a JSON-compatible dictionary."""

        payload: dict[str, Any] = {
            "id": self.id,
            "type": self.type,
        }
        if self.label is not None:
            payload["label"] = self.label
        if self.index_in_parent is not None:
            payload["index_in_parent"] = self.index_in_parent
        payload.update(self.metadata)
        if self.children:
            payload["children"] = [child.to_dict() for child in self.children]
        return payload


@dataclass(slots=True)
class RegionModule:
    """Container object returned to the simulator runtime."""

    root: RegionModuleNode

    def to_dict(self) -> dict:
        return self.root.to_dict()

    def iter_nodes(self) -> Iterable[RegionModuleNode]:
        """Depth-first iteration over nodes."""

        stack: List[RegionModuleNode] = [self.root]
        while stack:
            node = stack.pop()
            yield node
            stack.extend(reversed(node.children))

    def find(self, node_id: int) -> Optional[RegionModuleNode]:
        """Locate a node by ``id``."""

        return next((node for node in self.iter_nodes() if node.id == node_id), None)

    def __getattr__(self, name: str) -> Any:
        """Expose ``RegionModuleNode`` attributes for compatibility."""

        return getattr(self.root, name)


_TASK_TYPES = {"task"}


def _normalise_children(children: Optional[Any]) -> List[Mapping[str, Any]]:
    if children is None:
        return []
    if not isinstance(children, list):
        raise RegionModuleError("'children' must be a list when present")
    result: List[Mapping[str, Any]] = []
    for child in children:
        if not isinstance(child, Mapping):
            raise RegionModuleError("Each child must be a mapping")
        result.append(child)
    return result


def _extract_metadata(node_type: str, source: Mapping[str, Any]) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    if node_type in _TASK_TYPES:
        impacts = source.get("impacts")
        if impacts is None or not isinstance(impacts, list):
            raise RegionModuleError("Task nodes require an 'impacts' list")
        duration = source.get("duration")
        if duration is None:
            raise RegionModuleError("Task nodes require a 'duration'")
        metadata["impacts"] = impacts
        metadata["duration"] = duration
    elif node_type == "choice":
        max_delay = source.get("max_delay")
        if max_delay is None:
            raise RegionModuleError("Choice nodes require 'max_delay'")
        metadata["max_delay"] = max_delay
    elif node_type == "nature":
        distribution = source.get("distribution")
        if distribution is None or not isinstance(distribution, list):
            raise RegionModuleError("Nature nodes require a 'distribution' list")
        metadata["distribution"] = distribution
    elif node_type == "loop":
        probability = source.get("distribution")
        bound = source.get("bound")
        if probability is None:
            raise RegionModuleError("Loop nodes require a 'distribution' probability")
        metadata["distribution"] = probability
        if bound is not None:
            metadata["bound"] = bound
    # Sequential / parallel gateways have no additional metadata to copy.
    return metadata


def _validate_children(node_type: str, children: List[Mapping[str, Any]]) -> None:
    if node_type in {"sequential", "parallel"} and not children:
        raise RegionModuleError(f"{node_type} nodes must contain at least one child")
    if node_type in {"choice", "nature"} and len(children) < 2:
        raise RegionModuleError(f"{node_type} nodes must contain at least two children")
    if node_type == "loop" and len(children) != 1:
        raise RegionModuleError("Loop nodes must contain exactly one child")
    if node_type in _TASK_TYPES and children:
        raise RegionModuleError("Task nodes cannot have children")


def _build_node(source: Mapping[str, Any]) -> RegionModuleNode:
    try:
        node_type = str(source["type"]).lower()
    except KeyError as exc:
        raise RegionModuleError("Parse tree node missing 'type'") from exc
    try:
        node_id = int(source["id"])
    except KeyError as exc:
        raise RegionModuleError("Parse tree node missing 'id'") from exc
    except (TypeError, ValueError) as exc:
        raise RegionModuleError("Node 'id' must be an integer") from exc

    label = source.get("label")
    index_in_parent = source.get("index_in_parent")

    children_dicts = _normalise_children(source.get("children"))
    _validate_children(node_type, children_dicts)

    metadata = _extract_metadata(node_type, source)

    children = [_build_node(child) for child in sorted(children_dicts, key=lambda item: item.get("index_in_parent", 0))]

    return RegionModuleNode(
        id=node_id,
        type=node_type,
        label=label,
        index_in_parent=index_in_parent,
        metadata=metadata,
        children=children,
    )


def build_region_module(parse_tree: Mapping[str, Any]) -> RegionModule:
    """Convert a PACO parse-tree dictionary into a :class:`RegionModule`.

    Parameters
    ----------
    parse_tree:
        The dictionary produced by :meth:`ParseTree.to_dict`.
    """

    if not isinstance(parse_tree, Mapping):
        raise RegionModuleError("Parse tree payload must be a mapping")
    root = _build_node(parse_tree)
    return RegionModule(root=root)


def region_module_to_dict(parse_tree: Mapping[str, Any]) -> dict:
    """Helper returning the JSON payload expected by the simulator."""

    return build_region_module(parse_tree).to_dict()
