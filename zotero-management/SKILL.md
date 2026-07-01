---
name: zotero-management
description: "Manage a Zotero library: classify papers, create/move collections, batch-organize items. MCP for item-level ops, REST API for collection ops."
version: 1.0.0
author: 十五
metadata:
  hermes:
    tags: [research, zotero, literature, library-management]
    related_skills: [literature-pipeline, obsidian]
---

# Zotero Library Management

Manage a Zotero library — collection CRUD, item classification, batch reorganization. The Zotero MCP covers item-level operations (search/metadata/fulltext). Everything else goes through the REST API.

## Two-Layer Access

| Layer | Tools | Scope |
|-------|-------|-------|
| **MCP** | `zotero_search_items`, `zotero_item_metadata`, `zotero_item_fulltext` | Item-level: search, read metadata, extract fulltext |
| **REST API** | Direct `curl` calls | Collection CRUD, item relocation, batch ops |

The MCP **cannot** list collections, create collections, or move items between collections. For those, use the REST API.

## Credentials

Located in `~/.hermes/config.yaml` under `mcp_servers.zotero.env`:

```python
import yaml
cfg = yaml.safe_load(open('~/.hermes/config.yaml'))
env = cfg['mcp_servers']['zotero']['env']
API_KEY = env['ZOTERO_API_KEY']      # your Zotero API key (Settings → Feeds/API)
USER_ID = env['ZOTERO_LIBRARY_ID']   # your Zotero user/group ID
```

Library type: `user`, name: `your-zotero-username`.

## REST API Patterns

### Base URL
```
https://api.zotero.org/users/{USER_ID}
```

### List Collections
```
GET /users/{USER_ID}/collections
```
Returns all top-level collections with `key`, `name`, `meta.numItems`.

### Create Collections
```
POST /users/{USER_ID}/collections
Content-Type: application/json
Body: [{"name": "Collection Name", "parentCollection": "PARENT_KEY"}]
```
Returns `{"success": {"0": "NEW_COLLECTION_KEY"}}`. Works for both top-level and subcollections.

### Get Items in Collection
```
GET /users/{USER_ID}/collections/{COLLECTION_KEY}/items?limit=100
```
Each item includes `key`, `version`, `data.collections`, `data.tags`, `data.itemType`, `data.title`, `data.date`. Use `limit=100` for pagination.

### ⚠️ Add Items to Collection — BROKEN PATTERN
```
POST /users/{USER_ID}/collections/{COLLECTION_KEY}/items
Body: ["ITEM_KEY_1", "ITEM_KEY_2"]
```
This does **NOT** work. The server treats the entire JSON array as a single item key string and returns 400: `Item '["ITEM_KEY"]' not found in library`.

### ✅ Move Items — CORRECT PATTERN
PATCH individual items to update their `collections` field:
```
PATCH /users/{USER_ID}/items/{ITEM_KEY}
Headers: If-Unmodified-Since-Version: {VERSION}
Body: {"collections": ["EXISTING_KEY_1", "NEW_KEY"]}
```
Returns HTTP 204 on success. The `collections` array must include ALL collections the item should belong to, not just the new one.

### Fetch Single Item (for version)
```
GET /users/{USER_ID}/items/{ITEM_KEY}
```
Returns `version` and `data.collections`.

## Pitfalls

1. **Zotero MCP fulltext is frequently empty**: Most Zotero items lack attached PDFs. `zotero_item_fulltext` will return "no suitable attachment found" for 80%+ of papers. Always have a fallback: `web_search` + `web_extract` for abstract/content retrieval. PDFs that exist locally may need `lit parse` (LiteParse) for extraction.
2. **MCP is read-only for items**: Zotero MCP only supports search/metadata/fulltext reads. It cannot add items, create collections, move items, or modify metadata. Collection operations require REST API curl calls.
3. **Zotero collection structure ≠ vault classification**: Your Zotero may use topic-based subcollections while the vault uses a different classification system (e.g., A-E tiers). These are independent — when migrating papers from Zotero to vault, re-classify based on content relevance, not collection name.
4. **Rate limiting on writes**: Minimum 0.5s delay between PATCH/POST calls. 429 → exponential backoff. 412 → re-fetch and retry.
5. **PDF downloads via curl may be blocked**: The Hermes approvals system may block curl-based PDF downloads from subagent contexts. Collect URLs during research and handle downloads separately.

## Cross-Skill Workflows

### Zotero → Vault Bulk Classification

When the user asks to read and classify a large batch of Zotero papers (50-100) into the vault classification system: the full workflow is documented in the `literature-pipeline` skill's references. Key steps:

1. Multi-query Zotero MCP search + cross-reference with existing vault notes
2. Delegate batches of 5-9 papers to parallel subagents for reading + classification
3. Verify directory naming (subagents use short names: A/ → fix to A_核心主线/)
4. Post-processing: standardize frontmatter, normalize filenames per `literature-pipeline`'s `references/note-template.md`

### Note Frontmatter Standardization

The authoritative template is at `literature-pipeline` → `references/note-template.md` (v2, 2026-06-03). Covers:
- YAML frontmatter fields: title, authors, year, journal, doi, classification, tags, date_read
- File naming: `AuthorYear_中文关键词.md`
- Body structure: 核心主张 → 方法 → 关键发现 → 批判 → 与研究关联 → 下一步

- Minimum **0.5s delay** between PATCH/POST calls
- On HTTP 429: exponential backoff (2s, 4s, 8s)
- On HTTP 412 (version conflict): re-fetch item, update version, retry
- Batch scripts: use items already fetched from collection endpoint (they include `version` and `data.collections`) — do NOT re-fetch each item individually before patching
- Expect ~92 items to take 60-90 seconds at 0.5s/item

## Classification Workflow

When the user asks to classify/organize a Zotero collection:

1. **Fetch all items** from the collection via REST API, save to `/tmp/zotero_items.json`
2. **Analyze** titles + tags: extract natural clusters, propose classification scheme (5-10 categories)
3. **Get JL approval** on the scheme before creating collections
4. **Create subcollections** via REST API POST, save mapping to `/tmp/collections_map.json`
5. **Classify items** programmatically (keyword matching on title + tags, ordered by specificity), save to `/tmp/classification.json`
6. **Batch-move items** via PATCH on each item, reading `version` and `data.collections` from the already-fetched items.json

## Batch Move Script Template

See `scripts/batch-classify.py` for a reusable script. Key implementation notes:
- Read API key from config.yaml at runtime (never hardcode)
- Use items.json's `version` and `data.collections` fields — don't re-fetch
- Append target collection key to existing `collections` array
- 0.5s delay minimum, retry 429 with backoff, retry 412 with re-fetch

## PDF Extraction with LiteParse

When `zotero_item_fulltext` fails (no attachment or unsupported format), use `lit parse` for local PDF extraction:

```bash
lit parse paper.pdf --format json -o output.json
lit screenshot paper.pdf -o ./screenshots --target-pages "1-3"  # for charts/figures
```

Installed via `uv tool install liteparse` (v2.0.4). Supports PDF, DOCX, XLSX, PPTX, images. Has OCR via bundled Tesseract — works on scanned papers.

For visual content (figures, graphs, tables), pair with vision model: `lit screenshot` → `vision_analyze`.

## Your Library

| Field | Value |
|-------|-------|
| Library ID | numeric ID (found in Zotero Settings → Feeds/API) |
| Type | user or group |
| Username | your Zotero account username |
| Main collection | your primary research collection |

## Obsidian Integration

This skill works with the [Obsidian](https://obsidian.md) vault managed by `literature-pipeline`. After classifying papers through this skill, the literature pipeline's note template ensures consistent YAML frontmatter for Dataview queries.

The vault stores literature notes at `raw/literature/` with standardized formats that can be queried across your research knowledge base.
