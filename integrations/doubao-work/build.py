#!/usr/bin/env python3
"""Build an importable Doubao skill from an explicit, credential-free allowlist."""
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NAME = "cheat-on-content-doubao"
DIRECTORIES = ("skills", "shared-references", "starter-rubrics", "templates", "adapters", "hooks", "migrations", "tools", "examples", "docs")
TOP_FILES = ("SKILL.md", "README.md", "CHANGELOG.md", "LICENSE", "install.sh", "uninstall.sh", "integrations/doubao-work/README.md")
EXTENSIONS = {".md", ".py", ".sh", ".json", ".sql", ".txt", ".css", ".svg", ".template"}


def original_files():
    files = [ROOT / name for name in TOP_FILES]
    for directory in DIRECTORIES:
        for file in sorted((ROOT / directory).rglob("*")):
            relative = file.relative_to(ROOT)
            if file.is_file() and not any(part.startswith(".") or part == "__pycache__" for part in relative.parts):
                if file.suffix in EXTENSIONS:
                    if file.is_symlink():
                        raise ValueError("Source symlinks are not packaged")
                    files.append(file)
    return files


def build():
    dist = ROOT / "dist"
    destination = dist / NAME
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    for relative in ("SKILL.md", "README.md", "references/host-adapter.md", "references/model-config.example.json", "scripts/runtime.py"):
        output = destination / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(HERE / relative, output)
    manifest = {}
    for file in original_files():
        relative = file.relative_to(ROOT).as_posix()
        output = destination / "assets/cheat-on-content" / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file, output)
        manifest[relative] = hashlib.sha256(file.read_bytes()).hexdigest()
    skills = [name for name in manifest if name.startswith("skills/") and name.endswith("/SKILL.md")]
    if len(skills) != 15:
        raise ValueError("Expected all 15 original sub-skills")
    (destination / "source-manifest.json").write_text(json.dumps({"original_skills": 15, "files": manifest}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    bridge_manifest = {}
    for file in sorted(destination.rglob("*")):
        if file.is_file() and not file.relative_to(destination).as_posix().startswith("assets/"):
            bridge_manifest[file.relative_to(destination).as_posix()] = hashlib.sha256(file.read_bytes()).hexdigest()
    (destination / "bridge-manifest.json").write_text(json.dumps(bridge_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    archive = dist / (NAME + ".zip")
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
        for file in sorted(destination.rglob("*")):
            if file.is_file():
                bundle.write(file, file.relative_to(dist))
    print(json.dumps({"archive": str(archive), "source_files": len(manifest), "original_skills": len(skills), "bytes": archive.stat().st_size}, ensure_ascii=False))


if __name__ == "__main__":
    build()
