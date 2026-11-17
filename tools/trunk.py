#!/usr/bin/env python3
"""Which commit of the system repository the docs describe.

Every generator and code-reading check here used `git show HEAD:<path>`. In
this project the system checkout is SHARED and its working tree is
pre-landing, so its HEAD sits behind `origin/main` for hours at a time: on
2026-11-17 the tree was at cd3922c while trunk was at cd5f2a8, and two checks
went red for pages that were right. The docs describe what has LANDED, so they
should be read against trunk.

The rule, and it is deliberately narrow:

    HEAD is an ancestor of origin/main   -> read origin/main (the checkout is
                                            simply behind; trunk is the truth)
    anything else                        -> read HEAD

So a checkout that is ahead of trunk, on a branch, or diverged keeps reading
its own HEAD, which is what somebody documenting a branch wants. With no
`origin/main` at all (a bare clone of one commit, a throwaway worktree), HEAD
is used as before.
"""
import subprocess


def _git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True)


def trunk_ref(repo, remote_branch="origin/main"):
    """The ref a tool should read for `repo`: "origin/main" or "HEAD"."""
    if _git(repo, "rev-parse", "--verify", "--quiet", remote_branch).returncode:
        return "HEAD"
    behind = _git(repo, "merge-base", "--is-ancestor", "HEAD", remote_branch)
    if behind.returncode != 0:
        return "HEAD"
    same = _git(repo, "rev-parse", "HEAD").stdout.strip()
    other = _git(repo, "rev-parse", remote_branch).stdout.strip()
    return "HEAD" if same == other else remote_branch


def short(repo, ref):
    r = _git(repo, "rev-parse", "--short", ref)
    return r.stdout.strip() or "?"


if __name__ == "__main__":
    import pathlib, tempfile
    with tempfile.TemporaryDirectory() as d:
        r = pathlib.Path(d) / "r"
        _git(".", "init", "-q", str(r))
        _git(r, "config", "user.email", "t@t"); _git(r, "config", "user.name", "t")
        (r / "f").write_text("1\n")
        _git(r, "add", "f"); _git(r, "commit", "-qm", "one")
        assert trunk_ref(r) == "HEAD", "no origin/main: HEAD"
        # fake a remote-tracking ref one commit ahead
        first = _git(r, "rev-parse", "HEAD").stdout.strip()
        (r / "f").write_text("2\n")
        _git(r, "add", "f"); _git(r, "commit", "-qm", "two")
        ahead = _git(r, "rev-parse", "HEAD").stdout.strip()
        _git(r, "update-ref", "refs/remotes/origin/main", ahead)
        _git(r, "checkout", "-q", first)
        assert trunk_ref(r) == "origin/main", "behind trunk: read trunk"
        _git(r, "checkout", "-q", ahead)
        assert trunk_ref(r) == "HEAD", "at trunk: HEAD (same commit)"
        (r / "f").write_text("3\n")
        _git(r, "add", "f"); _git(r, "commit", "-qm", "three")
        assert trunk_ref(r) == "HEAD", "ahead of trunk: HEAD"
        _git(r, "update-ref", "refs/remotes/origin/main", first)
        assert trunk_ref(r) == "HEAD", "diverged/ahead: HEAD"
    print("trunk.py self-check ok")
