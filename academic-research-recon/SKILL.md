---
name: academic-research-recon
description: "Use when investigating academic researchers, supervisor lineages, institutional affiliations, publication networks, or research trajectories. Combines scholarly indexes such as OpenAlex/ORCID/DOI metadata with cautious identity disambiguation and source-grounded summaries."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [research, academia, openalex, orcid, scholarly-metadata, people-recon]
    related_skills: [arxiv, llm-wiki, obsidian]
---

# Academic Research Recon

## Overview

Use this skill to map an academic person or research lineage: researchers, supervisors, labs, institutes, coauthors, publication themes, and institutional transitions. The goal is not just to list papers, but to produce a careful, source-grounded narrative of how people, topics, and organizations connect.

Academic names are ambiguous, especially across Chinese/English transliterations and German characters. Treat identity resolution as a hypothesis until confirmed by multiple signals: ORCID, affiliation, coauthors, topic continuity, DOI pages, institutional profiles, and user-provided context.

## When to Use

Use when the user asks to:

- Search a researcher, professor, supervisor, PI, committee member, or lab.
- Verify whether a person came from an institution such as MIT, Stanford, CAS, Tsinghua, etc.
- Trace supervisor/advisor lineages or academic genealogy.
- Understand how a user's academic background connects to a broader research network.
- Build a concise research-person profile: affiliations, topics, key publications, collaborators.
- Work around search-engine bot challenges by using scholarly metadata APIs.

Don't use for:

- Pure paper discovery by topic only → prefer `arxiv` when the target corpus is arXiv.
- Reading/editing the user's note vault → use `obsidian` or `llm-wiki` first.
- Writing the final manuscript or proposal → use paper/proposal-specific skills if available.

## Core Workflow

1. **Clarify the target identity if needed, but start with obvious defaults.**
   - Record name variants: Chinese name, pinyin, initials, German spellings, umlaut/ß variants.
   - Example: `Andrea Thess` may actually be `Andreas Theß` / `Andreas Thess`.
   - Do not ask before searching if a likely spelling variant can be checked immediately.

2. **Search structured scholarly sources first.**
   - OpenAlex author search is often accessible even when Google/Bing/DuckDuckGo are blocked.
   - ORCID is strong identity evidence when present.
   - DOI metadata pages are strong evidence for paper-level affiliations and coauthor links.

3. **Disambiguate by evidence, not name match alone.**
   Check:
   - ORCID
   - last known institution
   - raw affiliation strings on works
   - coauthors already known from the user's context
   - topic continuity across publications
   - time period and geography

4. **Map the network.**
   Build a simple graph:

   ```text
   Person A
     ↕ coauthor / supervisor? / lab relation
   Person B
     ↕ institution / doctoral advisor? / coauthor
   Person C
   ```

   Label uncertain edges with `?` or phrases like "public metadata confirms coauthorship, not supervisor relationship".

5. **Separate confirmed facts from hypotheses.**
   Good wording:
   - "Public metadata confirms Researcher A and Researcher B coauthored a paper at Institution X."
- A casual mention by the user that they think a person was at Institution Y — treat as hypothesis to verify, not fact.
   - "The spelling may be Andreas Theß, but please confirm."

6. **Summarize as a research trajectory.**
   Explain how methods/topics/institutions connect, e.g.:

   ```text
   electrochemistry → electrocatalysis/fuel cells → storage materials/devices
   → molten salts / high-temperature storage → low-carbon energy systems
   ```

   Keep it useful for the user's planning: why this lineage matters, where it gives leverage, and what gaps still need verification.

## OpenAlex Recipes

OpenAlex works well in a browser context and returns JSON. For Chinese institutional researcher searches where pinyin names are ambiguous and mainstream search is blocked/noisy, see `references/chinese-institutional-search-playbook.md`. For tracing partnerships between Chinese research institutes and universities when the collaboration may not be publicly announced, see `references/chinese-institutional-collaboration-search.md`.

Useful endpoints:

```text
https://api.openalex.org/authors?search=<name>
https://api.openalex.org/works?filter=author.id:<OpenAlexAuthorId>&per-page=20&sort=publication_year:desc
https://api.openalex.org/works/https://doi.org/<doi>
```

Browser console parsing pattern:

```javascript
(() => {
  const data = JSON.parse(document.body.innerText);
  return data.results.map(a => ({
    name: a.display_name,
    id: a.id,
    orcid: a.orcid,
    works_count: a.works_count,
    cited_by_count: a.cited_by_count,
    last_known_institution: a.last_known_institution?.display_name,
    topics: (a.topics || []).slice(0, 5).map(t => t.display_name)
  }));
})()
```

For works:

```javascript
(() => {
  const data = JSON.parse(document.body.innerText);
  return data.results.map(w => ({
    year: w.publication_year,
    title: w.title,
    doi: w.doi,
    authors: w.authorships.map(a => a.author.display_name),
    affiliations: [...new Set(w.authorships.flatMap(a => a.raw_affiliation_strings || []))]
  }));
})()
```

## Handling Search Blocks

If mainstream search fails:

- Search engines may show bot challenges; do not waste turns trying to solve them.
- Terminal network may be blocked even if browser navigation works.
- Use OpenAlex, Crossref, ORCID, DOI pages, institutional pages, Semantic Scholar, PubMed, arXiv, Google Scholar snippets if accessible.
- For Chinese academics, try Chinese search engines such as 360 Search (`so.com`) when Google/Bing/Baidu/DuckDuckGo are blocked; it may surface official university profile pages with snippets even when scholarly indexes are ambiguous.
- Search by unique institutional email (e.g. `"name@university.edu.cn"`) and by exact paper titles from a CV/profile to disambiguate same-name OpenAlex authors.
- When one source is incomplete, say so and continue with a second source.
- When one source is incomplete, say so and continue with a second source.

## Output Format

For exploratory conversation, prefer a concise Chinese structure when the user is speaking Chinese:

```markdown
大哥，我先查到这些，先不下死结论：

## 已确认
- ...

## 高概率但需核实
- ...

## 这条线怎么串起来
```text
A → B → C
```

## 还需要你确认/我可以继续查
- ...
```

Avoid overclaiming advisor relationships unless a CV, thesis record, institutional bio, dissertation page, or user confirmation supports it.

## Common Pitfalls

1. **Confusing same-name scholars.** Pinyin names collide frequently. Require multiple identity signals before merging records. OpenAlex may merge or attach unrelated last-known institutions for Chinese pinyin names; anchor with official profile, exact email, representative papers, and DOI affiliations before drawing conclusions.

2. **Treating coauthorship as supervision.** Coauthorship confirms collaboration, not formal supervisor/advisor status.

3. **Ignoring transliteration and special characters.** Search `Thess`, `Theß`, `Thes`, initials, and German/English variants.

4. **Writing personal background into memory during exploratory interviews.** If the user is narrating a complex academic history and says to wait, only use conversation context. Save only when the user asks to consolidate.

5. **Overusing search engines when they are blocked.** Switch quickly to structured scholarly metadata sources.

6. **Presenting raw bibliographies without interpretation.** The value is the network/trajectory interpretation grounded in evidence.

7. **Over-interpreting the user's agency in career/academic decisions.** When the user describes their placement or path (e.g. which supervisor, which university), state the outcome and the rationale they gave. Do not reframe it as passive acceptance unless the user explicitly says so, and do not reframe it as active choice if the user says they simply accepted the arrangement. Let the user's own framing stand — don't add or subtract agency.

## Verification Checklist

- [ ] At least one source-backed identity signal per person: ORCID, OpenAlex ID, institutional page, DOI affiliation, or user confirmation.
- [ ] Confirmed facts and hypotheses are clearly separated.
- [ ] Advisor/supervisor claims are not asserted solely from coauthorship.
- [ ] Name variants and possible ambiguity are noted.
- [ ] Key publications include DOI/title/year when available.
- [ ] The final summary explains why the network matters for the user's research path.
