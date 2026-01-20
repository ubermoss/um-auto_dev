"""Git tools for version control operations."""

import subprocess
import os
from pathlib import Path
from typing import Dict, Any, Optional, List


class GitTools:
    """Handles git operations for version control."""

    def __init__(self, repo_path: str = "."):
        """Initialize git tools with repository path."""
        self.repo_path = Path(repo_path).resolve()

    def _run_git_command(self, args: List[str]) -> Dict[str, Any]:
        """Run a git command and return results."""
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip()
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": "Git command timed out"
            }
        except Exception as e:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": str(e)
            }

    def init_repo(self) -> Dict[str, Any]:
        """Initialize a new git repository."""
        return self._run_git_command(["init"])

    def is_repo(self) -> bool:
        """Check if current directory is a git repository."""
        result = self._run_git_command(["rev-parse", "--git-dir"])
        return result["success"]

    def get_status(self) -> Dict[str, Any]:
        """Get git status."""
        return self._run_git_command(["status", "--porcelain"])

    def create_branch(self, branch_name: str) -> Dict[str, Any]:
        """Create a new branch."""
        return self._run_git_command(["checkout", "-b", branch_name])

    def checkout_branch(self, branch_name: str) -> Dict[str, Any]:
        """Checkout an existing branch."""
        return self._run_git_command(["checkout", branch_name])

    def get_current_branch(self) -> Optional[str]:
        """Get the name of the current branch."""
        result = self._run_git_command(["branch", "--show-current"])
        if result["success"]:
            return result["stdout"]
        return None

    def add_files(self, files: List[str]) -> Dict[str, Any]:
        """Add files to staging area."""
        return self._run_git_command(["add"] + files)

    def commit(self, message: str) -> Dict[str, Any]:
        """Create a commit with the given message."""
        return self._run_git_command(["commit", "-m", message])

    def get_diff(self, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Get diff of changes."""
        args = ["diff"]
        if file_path:
            args.append(file_path)
        return self._run_git_command(args)

    def get_log(self, max_count: int = 10) -> Dict[str, Any]:
        """Get commit log."""
        return self._run_git_command([
            "log",
            f"--max-count={max_count}",
            "--pretty=format:%h - %s (%an, %ar)"
        ])

    def list_branches(self) -> Dict[str, Any]:
        """List all branches."""
        return self._run_git_command(["branch", "-a"])

    def stash_changes(self, message: Optional[str] = None) -> Dict[str, Any]:
        """Stash current changes."""
        args = ["stash", "push"]
        if message:
            args.extend(["-m", message])
        return self._run_git_command(args)

    def apply_stash(self, stash_ref: str = "stash@{0}") -> Dict[str, Any]:
        """Apply a stashed change."""
        return self._run_git_command(["stash", "apply", stash_ref])

    def reset_hard(self, commit: str = "HEAD") -> Dict[str, Any]:
        """Hard reset to a commit. WARNING: Destructive operation."""
        return self._run_git_command(["reset", "--hard", commit])

    def tag(self, tag_name: str, message: Optional[str] = None) -> Dict[str, Any]:
        """Create a tag."""
        args = ["tag", tag_name]
        if message:
            args.extend(["-m", message])
        return self._run_git_command(args)

    def get_tags(self) -> Dict[str, Any]:
        """List all tags."""
        return self._run_git_command(["tag", "-l"])
