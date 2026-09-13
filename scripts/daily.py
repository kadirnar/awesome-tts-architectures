"""Validate and render the pinned TTS-arxiv-daily screening record, offline."""

from collections import Counter, defaultdict
from datetime import date
import re
from urllib.parse import urlsplit


REASONS = {
    "distinct-tts-system": "TTS model, synthesis architecture or named synthesis system",
    "data-or-evaluation": "Dataset, benchmark, evaluation or analysis without a distinct TTS system",
    "component-or-training-method": "Component, training or inference method without a distinct synthesis system",
    "outside-tts": "Speech understanding, conversion, audio generation or application outside the TTS scope",
    "no-distinct-tts-system": "No distinct text-to-speech system identified in the reviewed source",
    "before-2025": "First paper submission predates January 1, 2025",
}


def validate_daily(ledger, catalog, figures):
    if ledger.get("schema_version") != 1:
        raise ValueError("Unsupported daily screening schema")
    source = ledger["source"]
    if not re.fullmatch(r"[0-9a-f]{40}", source["commit"]):
        raise ValueError("Daily source requires a pinned commit")
    if not re.fullmatch(r"[0-9a-f]{64}", source["readme_sha256"]):
        raise ValueError("Daily source requires a snapshot checksum")
    expected = f'https://github.com/liutaocode/TTS-arxiv-daily/blob/{source["commit"]}/README.md'
    if source["readme_url"] != expected:
        raise ValueError("Daily source README must match its pinned commit")
    start = date.fromisoformat(ledger["min_first_submission_date"])
    reviewed = date.fromisoformat(ledger["reviewed_on"])
    if start != date(2025, 1, 1) or reviewed > date.fromisoformat(catalog["as_of"]):
        raise ValueError("Invalid daily review dates")
    records = ledger["records"]
    if len(records) != ledger["eligible_row_count"] or len(records) > ledger["source_row_count"]:
        raise ValueError("Daily screening row count does not match the snapshot")
    models = {m["id"]: m for m in catalog["models"]}
    seen = set()
    for row in records:
        aid = row["arxiv_id"]
        if not re.fullmatch(r"\d{4}\.\d{4,5}", aid) or aid in seen:
            raise ValueError(f"Daily record has an invalid or repeated paper: {aid}")
        seen.add(aid)
        if not row["title"].strip() or row["paper_url"] != f"https://arxiv.org/abs/{aid}":
            raise ValueError(f"{aid}: invalid daily paper metadata")
        if not start <= date.fromisoformat(row["listed_on"]) <= reviewed:
            raise ValueError(f"{aid}: listed date outside the daily snapshot window")
        if row["review_level"] not in {"title", "abstract", "paper"} or row["reason"] not in REASONS:
            raise ValueError(f"{aid}: unknown screening evidence or reason")
        if row["decision"] == "excluded":
            if row["reason"] == "distinct-tts-system" or "model_id" in row:
                raise ValueError(f"{aid}: inconsistent exclusion")
            continue
        if row["decision"] != "included" or row["reason"] != "distinct-tts-system":
            raise ValueError(f"{aid}: invalid screening decision")
        if row["review_level"] == "title" or row["catalog_action"] not in {"added", "existing"}:
            raise ValueError(f"{aid}: included systems need primary-source review")
        first = date.fromisoformat(row["first_submitted"])
        if not start <= first <= reviewed:
            raise ValueError(f"{aid}: first submission outside the requested date window")
        mid = row["model_id"]
        if mid not in models or mid not in figures:
            raise ValueError(f"{aid}: missing model or image")
        model = models[mid]
        if not model.get("description") or "github_status" not in model:
            raise ValueError(f"{mid}: daily models need a description and GitHub review status")
        if row["catalog_action"] == "added" and (not model["source_date"] or date.fromisoformat(model["source_date"]) < start):
            raise ValueError(f"{mid}: new imports must be from 2025 onward")
        paper_urls = {s["url"] for s in model["sources"] if s["kind"] == "paper"}
        if row["paper_url"] not in paper_urls:
            raise ValueError(f"{mid}: screened paper missing from model sources")
        for evidence in row.get("repository_evidence", []):
            if evidence["url"] not in {s["url"] for s in model["sources"] if s["kind"] == "repository"}:
                raise ValueError(f"{mid}: repository evidence does not match the card")
            parsed = urlsplit(evidence["evidence_url"])
            if parsed.scheme != "https" or not parsed.netloc or evidence["verification"] not in {"paper-link", "project-link", "readme-paper-link", "readme-paper-match", "existing-reviewed-source"}:
                raise ValueError(f"{mid}: invalid repository verification evidence")


def render_daily(ledger, catalog, figures, model_link, source_links):
    by_model = defaultdict(list)
    excluded = Counter()
    for row in ledger["records"]:
        if row["decision"] == "included":
            by_model[row["model_id"]].append(row)
        else:
            excluded[row["reason"]] += 1
    models = [m for m in catalog["models"] if m["id"] in by_model]
    models.sort(key=lambda m: (min(r["first_submitted"] for r in by_model[m["id"]]), m["name"].casefold()), reverse=True)
    added = sum(any(r["catalog_action"] == "added" for r in by_model[m["id"]]) for m in models)
    github = sum(m["github_status"] == "author-linked" for m in models)
    primary_figures = sum(figures[m["id"]]["kind"] == "source-figure" for m in models)
    included_papers = sum(len(rows) for rows in by_model.values())
    lines = [
        "# TTS-arxiv-daily · Models from 2025 onward", "",
        "<!-- Generated by scripts/catalog.py from data/tts-arxiv-daily.json, data/models.json and data/figures.json. -->", "",
        "[← Complete catalog](../README.md#models)", "",
        f'**{len(models)} model families · {included_papers} papers · {added} new catalog entries · Reviewed {ledger["reviewed_on"]}**', "",
        f'Screened all **{ledger["eligible_row_count"]} rows dated 2025 onward** in the [pinned TTS-arxiv-daily snapshot]({ledger["source"]["readme_url"]}). Inclusion requires a text-to-speech model, distinct synthesis architecture or named synthesis system whose paper was first submitted on or after **January 1, 2025**. A later revision of a 2024 paper does not qualify. Earlier entries in the complete catalog remain available.', "",
        "Datasets, benchmarks, standalone codecs and vocoders, speech understanding, and methods without a distinct synthesis system are excluded. Closely related releases and renamed papers share a card. Descriptive names are used when a paper does not give its system a brand name.", "",
        f'Every family below has a description, a local image and paper links. **{github}** have author-linked GitHub sources; **{len(models) - github}** have no author-linked repository found in the reviewed sources. A missing link is a review result, not a claim that no repository exists. Data or evaluation repositories are identified in the card notes. **{primary_figures}** images come from primary sources; **{len(models) - primary_figures}** are labeled editorial input/output diagrams.', "",
        "Dates are first paper submission dates, not verified software release dates. Withdrawals and renamed papers are noted on the affected cards. [Full screening and repository evidence](../data/tts-arxiv-daily.json) · [Figure credits](../assets/architectures/CREDITS.md).", "",
        "<details>", "<summary>Screening counts</summary>", "",
        "| Decision | Papers |", "| --- | ---: |", f"| Included | {included_papers} |",
    ]
    lines += [f"| {REASONS[reason]} | {count} |" for reason, count in sorted(excluded.items())]
    lines += ["", "</details>", "", "<details>", "<summary>Model index</summary>", ""]
    lines += [f'- [{m["name"]}](#{m["id"]})' for m in models]
    lines += ["", "</details>", "", "## Models", ""]
    for model in models:
        mid = model["id"]
        figure = figures[mid]
        first = min(r["first_submitted"] for r in by_model[mid])
        visual = "Editorial input/output diagram" if figure["kind"] == "io-diagram" else figure["locator"]
        lines += [
            f'<a id="{mid}"></a>', "", f'### {model["name"]}', "",
            f'**First paper submission:** {first} · [Architecture card]({model_link(model, "../")})', "",
            model["description"], "", source_links(model), "",
            f'![{model["name"]} — {visual}](../{figure["path"]})', "",
            f'*{visual} · [Image source]({figure["source_url"]})*', "",
        ]
    return "\n".join(lines).rstrip() + "\n"
