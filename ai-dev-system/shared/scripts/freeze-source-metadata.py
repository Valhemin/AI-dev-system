#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


FROZEN_ROOT = Path("shared/sources/upstream/repos")


def read_json(path: Path, fallback):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback


def copy_source(root: Path, src: str) -> str:
    src_path = Path(src)
    if not src_path.exists():
        return src
    try:
        rel = src_path.relative_to(root.parent)
    except ValueError:
        rel = src_path
    if len(rel.parts) < 3 or rel.parts[0] != "ai-repos":
        return src
    dest_rel = FROZEN_ROOT / rel.parts[1] / Path(*rel.parts[2:])
    dest = root / dest_rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_path, dest)
    return dest_rel.as_posix()


def freeze_imported_skills(root: Path) -> dict[str, str]:
    path = root / "shared/registry/imported-skills.tsv"
    lines = path.read_text(encoding="utf-8").splitlines()
    mapping: dict[str, str] = {}
    out = []
    for line in lines:
        if not line.strip():
            out.append(line)
            continue
        cols = line.split("|")
        if len(cols) < 4:
            out.append(line)
            continue
        skill_id, dest, status, src = cols[:4]
        upstream = cols[4] if len(cols) >= 5 else ""
        source_to_freeze = ""
        if src.startswith("ai-repos/"):
            source_to_freeze = src
            upstream = src
        elif upstream.startswith("ai-repos/"):
            source_to_freeze = upstream
        if source_to_freeze:
            frozen = copy_source(root, source_to_freeze)
            cols = [skill_id, dest, status, frozen, upstream]
            mapping[upstream] = frozen
        out.append("|".join(cols))
    path.write_text("\n".join(out) + "\n", encoding="utf-8")
    return mapping


def freeze_skills_json(root: Path, mapping: dict[str, str]) -> None:
    path = root / "shared/registry/skills.json"
    data = read_json(path, [])
    changed = False
    for item in data:
        src = item.get("source_detail", "")
        if src in mapping:
            item["source_upstream"] = src
            item["source_detail"] = mapping[src]
            changed = True
    if changed:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def freeze_source_catalog(root: Path, mapping: dict[str, str]) -> None:
    repos = {}
    for frozen in mapping.values():
        parts = Path(frozen).parts
        if len(parts) >= 5 and tuple(parts[:4]) == ("shared", "sources", "upstream", "repos"):
            repos[parts[4]] = {
                "repo": parts[4],
                "local_path": f"shared/sources/upstream/repos/{parts[4]}",
            }
    path = root / "shared/registry/source-catalog.json"
    current = read_json(path, [])
    current_by_repo = {entry.get("repo"): entry for entry in current if isinstance(entry, dict)}
    out = []
    for repo, entry in sorted(repos.items()):
        merged = dict(current_by_repo.get(repo, {}))
        merged.update(entry)
        out.append(merged)
    if out:
        path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")


def freeze_source_headers(root: Path, mapping: dict[str, str]) -> int:
    updated = 0
    for path in root.rglob("*.md"):
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        original = text
        for upstream, frozen in mapping.items():
            text = text.replace(f"Source: {upstream}", f"Source: {frozen} (upstream: {upstream})")
        if text != original:
            path.write_text(text, encoding="utf-8")
            updated += 1
    return updated


def write_manifest(root: Path, mapping: dict[str, str]) -> None:
    manifest = []
    for upstream, frozen in sorted(mapping.items()):
        manifest.append({"upstream": upstream, "frozen": frozen})
    path = root / "shared/sources/upstream/manifest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"entries": manifest}, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--system-root", default="ai-dev-system")
    args = parser.parse_args()

    root = Path(args.system_root)
    mapping = freeze_imported_skills(root)
    freeze_skills_json(root, mapping)
    freeze_source_catalog(root, mapping)
    header_updates = freeze_source_headers(root, mapping)
    write_manifest(root, mapping)

    print(f"frozen_sources\t{len(mapping)}")
    print(f"updated_headers\t{header_updates}")
    print(f"manifest\t{(root / 'shared/sources/upstream/manifest.json').as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
