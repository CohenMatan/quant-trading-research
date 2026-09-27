"""Git helpers for provenance: clean-tree check, commit hash, reading files at a commit."""
from __future__ import annotations

import subprocess
from pathlib import Path

from . import config


class DirtyTreeError(RuntimeError):
    pass


def _git(*args: str, cwd: Path | None = None) -> str:
    out = subprocess.run(
        ["git", *args], cwd=cwd or config.REPO_ROOT, check=True, capture_output=True, text=True
    )
    return out.stdout


def head_commit(cwd: Path | None = None) -> str:
    return _git("rev-parse", "HEAD", cwd=cwd).strip()


def dirty_paths(cwd: Path | None = None) -> list[str]:
    """Tracked or untracked (non-ignored) changes. Any entry means the tree is not clean."""
    lines = _git("status", "--porcelain", "--untracked-files=all", cwd=cwd).splitlines()
    return [ln[3:] for ln in lines if ln.strip()]


def require_clean_tree(cwd: Path | None = None) -> str:
    """Return HEAD if the working tree is clean, else raise DirtyTreeError."""
    dirty = dirty_paths(cwd)
    if dirty:
        shown = ", ".join(dirty[:10]) + (" …" if len(dirty) > 10 else "")
        raise DirtyTreeError(f"Working tree is not clean ({len(dirty)} paths: {shown}). Commit first.")
    return head_commit(cwd)


def show_file(commit: str, path: str, cwd: Path | None = None) -> str:
    """Contents of `path` (repo-relative, POSIX) exactly as committed in `commit`."""
    return _git("show", f"{commit}:{path}", cwd=cwd)


def list_files(commit: str, directory: str, cwd: Path | None = None) -> list[str]:
    out = _git("ls-tree", "-r", "--name-only", commit, "--", directory, cwd=cwd)
    return [p for p in out.splitlines() if p]
