"""Pluggable issue-block types.

freeletter itself only knows about one block type ("html", free-form
content) — it has no idea what any other kind of content might be. A
host project (or a separate integration package) can register further
block types here, each pointing at its own template and knowing how to
resolve its own `content_object`; freeletter's IssueBlock model just
stores a block_type slug plus a generic (content_type, object_id) pointer
and defers rendering to whatever's registered. This is what lets an issue
mix free content with, say, a blog post or a product card, without
freeletter needing to know what either of those is.

Registration happens in an AppConfig.ready() (see apps.py), the same
"import side effects happen at app-loading time" shape Django itself uses
for signal receivers — not at import time of this module, so app-loading
order doesn't matter.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.template.loader import render_to_string


@dataclass(frozen=True)
class BlockType:
    slug: str
    label: str
    template_name: str
    # Whether this block type needs a content_object resolved via the
    # generic (content_type, object_id) pair — False for "html", which
    # carries its own content directly on IssueBlock.
    requires_object: bool = True

    def render(self, block: Any, context: dict) -> str:
        ctx = {
            **context,
            "block": block,
            "object": block.content_object if self.requires_object else None,
        }
        return render_to_string(self.template_name, ctx)


_registry: dict[str, BlockType] = {}


def register_block_type(block_type: BlockType) -> None:
    _registry[block_type.slug] = block_type


def get_block_type(slug: str) -> BlockType:
    return _registry[slug]


def get_registered_block_types() -> list[BlockType]:
    return list(_registry.values())


def is_registered(slug: str) -> bool:
    return slug in _registry
