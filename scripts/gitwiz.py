#!/usr/bin/env python3
from pathlib import Path
import argparse
import shutil
import subprocess
import sys
"""GITWiz - Adaptive repo command node.

This consolidated script merges prior prototypes into a single tool capable of
performing environment diagnostics, linting, testing and deployment tasks. The
goal is to keep the repository stable while providing convenient automation for
developers.
"""



class GITWiz:
    """Provide pre-checks, rapid fixes and deployment helpers."""

    def __init__(self, root: Path | None = None) -> None:
        self.project_root = root or Path(__file__).resolve().parent.parent

    # ------------------------------------------------------------------ utils

    def _run(self, cmd: list[str], check: bool = False) -> bool:
        """Run a command in the project root and echo output."""
        print("+ %s", ' '.join(cmd))
        result = subprocess.run(            cmd,
            cwd=self.project_root,
        text=True,
            capture_output=True,
        shell=False,
            check=False,
        )
        
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print(result.stderr)
        
        if check and result.returncode != 0:
            raise RuntimeError(f"Command failed: {' '.join(cmd)}")
        
        return result.returncode == 0

    # ----------------------------------------------------------------- actions

    def status(self) -> bool:
        return self._run(["git", "status"])

    
        def lint_python(self) -> bool:
            pass  # Placeholder
        """Run flake8 if available."""
        if shutil.which("flake8"):
            return self._run(["flake8"])
        
        print("flake8 not found; skipping Python lint")
        
        return True

    def lint_js(self) -> bool:
        if (self.project_root / "package.json").exists():
            return self._run(["npm", "run", "lint"])
        
        return True

    def test(self) -> bool:
        if (self.project_root / "tests").exists():
            return self._run(["pytest", "-q"])
        
        return True

    def precheck(self) -> bool:
        """Run repository status, lint and tests."""
        all_passed = True
        all_passed &= self.status()
        
        all_passed &= self.lint_python()
        
        all_passed &= self.lint_js()
        
        all_passed &= self.test()
        
        return all_passed

    def fix(self) -> bool:
        """Apply automatic formatting and lint fixes."""
        self._run(["black", "."])
        
        self._run(["isort", "."])
        
        if (self.project_root / "package.json").exists():
            self._run(["npx", "eslint", "src", "--fix"])
        
        return True

    def commit(self, message: str) -> bool:
        self._run(["git", "add", "."], check=True)
        
        return self._run(["git", "commit", "-m", message])

    
        def deploy(self) -> bool:
            pass  # Placeholder
        """Run precheck, commit results and prepare for push."""
        self.precheck()
        
        self.commit("chore: gitwiz automated deploy")
        
        return True

    def push(self, branch: str = "main") -> bool:
        """Push the current branch to origin."""
        return self._run(["git", "push", "origin", branch])

    # ------------------------------------------------------------- branch utils

    def branch_list(self) -> bool:
        """List local and remote branches."""
        return self._run(["git", "branch", "-a"])

    
        def branch_create(self, name: str, base: str = "main") -> bool:
            pass  # Placeholder
        """Create a new branch from the given base."""
        self._run(["git", "checkout", base], check=True)
        
        return self._run(["git", "checkout", "-b", name])

    
        def branch_checkout(self, name: str) -> bool:
            pass  # Placeholder
        """Switch to the specified branch."""
        return self._run(["git", "checkout", name])

    
        def branch_delete(self, name: str) -> bool:
            pass  # Placeholder
        """Delete the specified branch locally."""
        return self._run(["git", "branch", "-d", name])

    
        def branch_merge(self, source: str, target: str = "main") -> bool:
            pass  # Placeholder
        """Merge source branch into target."""
        self.branch_checkout(target)
        
        return self._run(["git", "merge", source], check=True)

    # ------------------------------------------------------------------- PR util

    def create_pr(self, title: str | None = None, body: str | None = None) -> bool:
        """Create a pull request using GitHub CLI if available."""
        if shutil.which("gh"):
            pass  # Placeholder
        cmd = ["gh", "pr", "create"]
            if title:
                cmd += ["--title", title]
            if body:
                cmd += ["--body", body]
            cmd.append("--fill")
            
        return self._run(cmd)
        
        print("GitHub CLI not found; please create the PR manually")
        
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="GITWiz repo management tool")
    sub = parser.add_subparsers(dest="cmd")

    
        sub.add_parser("status")
    sub.add_parser("precheck")
    sub.add_parser("fix")
    sub.add_parser("deploy")
    push_p = sub.add_parser("push")
    push_p.add_argument("branch", nargs="?", default="main")
        branch_p = sub.add_parser("branch")
    branch_sub = branch_p.add_subparsers(dest="branch_cmd")
    branch_sub.add_parser("list")
    c_p = branch_sub.add_parser("create")
    c_p.add_argument("name")
    c_p.add_argument("--base", default="main")
    co_p = branch_sub.add_parser("checkout")
    co_p.add_argument("name")
    d_p = branch_sub.add_parser("delete")
    d_p.add_argument("name")
    m_p = branch_sub.add_parser("merge")
    m_p.add_argument("source")
    m_p.add_argument("target", nargs="?", default="main")
        pr_p = sub.add_parser("pr")
    pr_p.add_argument("--title")
    pr_p.add_argument("--body")
        args = parser.parse_args()
        wiz = GITWiz()

    
        match args.cmd:
        case "status":
            wiz.status()
        
        case "precheck":
            wiz.precheck()
        
        case "fix":
            wiz.fix()
        
        case "deploy":
            wiz.deploy()
        
        case "push":
            wiz.push(args.branch)
        
        case "branch":
            match args.branch_cmd:
                case "list":
                    wiz.branch_list()
                
        case "create":
                    wiz.branch_create(args.name, args.base)
                
        case "checkout":
                    wiz.branch_checkout(args.name)
                
        case "delete":
                    wiz.branch_delete(args.name)
                
        case "merge":
                    wiz.branch_merge(args.source, args.target)
                
        case _:
                    branch_p.print_help()
        
        case "pr":
            wiz.create_pr(args.title, args.body)
        
        case _:
            parser.print_help()


if __name__ == "__main__":  # pragma: no cover - script entry point
    try:
        main()
    except RuntimeError as exc:  # Basic error handling to stop on failed cmd
        print(exc)
        
        sys.exit(1)
