# Configuration file for the Sphinx documentation builder.

from __future__ import annotations

project = "UR 조선소 시스템 통신 프로토콜"
author = "Shipyard"

extensions = [
    "myst_parser",
    "sphinx.ext.autosectionlabel",
]

# Make section labels unique across documents.
autosectionlabel_prefix_document = True

myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "tasklist",
    "substitution",
]

# Add anchors to headings for easy linking.
myst_heading_anchors = 3

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

master_doc = "index"

language = "ko"

exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
]

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
