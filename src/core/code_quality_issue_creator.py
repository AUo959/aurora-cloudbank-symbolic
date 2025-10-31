"""
Automated GitHub Issue Creator for Code Quality Violations
Part of Issue #258: Automated code quality analysis
"""

import os
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass

try:
    import requests
except ImportError:
    requests = None


@dataclass
class GitHubIssue:
    """Represents a GitHub issue for a code quality violation."""
    title: str
    body: str
    labels: List[str]
    assignees: List[str]


class CodeQualityIssueCreator:
    """
    Creates GitHub issues for critical code quality violations.
    Integrates with Aurora's DLP tracking and reflection system.
    """
    
    ISSUE_LABEL_PREFIX = "code-quality"
    
    def __init__(
        self,
        repo_owner: str,
        repo_name: str,
        github_token: Optional[str] = None
    ):
        """
        Initialize issue creator.
        
        Args:
            repo_owner: GitHub repository owner
            repo_name: GitHub repository name
            github_token: GitHub API token (defaults to GITHUB_TOKEN env var)
        """
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        self.api_base = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
        
        if requests is None:
            raise ImportError(
                "requests library required for GitHub API. "
                "Install with: pip install requests"
            )
    
    def create_issue_from_violation(
        self,
        violation: Dict[str, Any],
        commit_sha: Optional[str] = None,
        pr_number: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a GitHub issue for a critical code quality violation.
        
        Args:
            violation: Violation dictionary from CodeQualityAnalyzer
            commit_sha: Optional commit SHA where violation was found
            pr_number: Optional PR number where violation was found
            
        Returns:
            Created issue data or None if creation failed
        """
        if not self.github_token:
            print("Warning: GITHUB_TOKEN not set, cannot create issues")
            return None
        
        # Build issue content
        issue = self._build_issue(violation, commit_sha, pr_number)
        
        # Create issue via GitHub API
        headers = {
            'Authorization': f'Bearer {self.github_token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Aurora-Code-Quality-Bot'
        }
        
        url = f"{self.api_base}/issues"
        payload = {
            'title': issue.title,
            'body': issue.body,
            'labels': issue.labels,
        }
        
        # Add assignees if specified
        if issue.assignees:
            payload['assignees'] = issue.assignees
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error creating issue: {e}")
            return None
    
    def _build_issue(
        self,
        violation: Dict[str, Any],
        commit_sha: Optional[str],
        pr_number: Optional[int]
    ) -> GitHubIssue:
        """
        Build GitHub issue from violation data.
        
        Args:
            violation: Violation dictionary
            commit_sha: Optional commit SHA
            pr_number: Optional PR number
            
        Returns:
            GitHubIssue object
        """
        # Extract violation details
        file_path = violation.get('file_path', 'unknown')
        line_number = violation.get('line_number', 0)
        code = violation.get('code', 'UNKNOWN')
        message = violation.get('message', 'No message')
        severity = violation.get('severity', 'unknown')
        
        # Build title
        title = f"[Code Quality] {code}: {file_path}:{line_number}"
        
        # Build body with Aurora DLP tracking
        body_parts = [
            "## Code Quality Violation",
            "",
            f"**Severity:** {severity.upper()}",
            f"**Error Code:** `{code}`",
            f"**Message:** {message}",
            "",
            "### Location",
            f"- **File:** `{file_path}`",
            f"- **Line:** {line_number}",
        ]
        
        if commit_sha:
            body_parts.extend([
                f"- **Commit:** {commit_sha[:8]}",
                f"- **View:** [{self.repo_owner}/{self.repo_name}@{commit_sha[:8]}]"
                f"(https://github.com/{self.repo_owner}/{self.repo_name}/blob/{commit_sha}/{file_path}#L{line_number})"
            ])
        
        if pr_number:
            body_parts.extend([
                f"- **Pull Request:** #{pr_number}",
            ])
        
        body_parts.extend([
            "",
            "### Recommended Action",
            self._get_fix_recommendation(code),
            "",
            "### Aurora Context",
            "- **Context Tag:** `code_quality_violation`",
            "- **Chain Notation:** `001//258//`",
            "- **DLP Protocol:** T1/SRB anchor with automated tracking",
            "",
            "---",
            "*This issue was automatically created by Aurora Code Quality Analyzer (Issue #258)*",
        ])
        
        body = "\n".join(body_parts)
        
        # Determine labels
        labels = [
            self.ISSUE_LABEL_PREFIX,
            f"{self.ISSUE_LABEL_PREFIX}-{severity}",
            "automated",
        ]
        
        # Critical violations get priority label
        if severity == 'critical':
            labels.append('critical')
        
        return GitHubIssue(
            title=title,
            body=body,
            labels=labels,
            assignees=[]
        )
    
    def _get_fix_recommendation(self, error_code: str) -> str:
        """
        Get recommended fix for an error code.
        
        Args:
            error_code: flake8 error code
            
        Returns:
            Markdown-formatted fix recommendation
        """
        recommendations = {
            'E9': 'Fix runtime/syntax error to ensure code can be executed.',
            'F63': 'Correct the syntax in type comments.',
            'F7': 'Fix syntax error in Python code.',
            'F82': 'Define the variable before using it, or remove unused reference.',
            'F401': 'Remove the unused import or use the imported module.',
            'F811': 'Remove the duplicate definition or rename to avoid conflict.',
            'F841': 'Use the local variable or remove the assignment.',
            'E501': 'Break long line into multiple lines (max 120 characters per project config).',
            'E402': 'Move module imports to the top of the file.',
            'W': 'Review warning and apply appropriate fix.',
            'C9': 'Simplify complex code or break into smaller functions.',
        }
        
        # Check exact match
        if error_code in recommendations:
            return recommendations[error_code]
        
        # Check prefix match
        for prefix, recommendation in recommendations.items():
            if error_code.startswith(prefix):
                return recommendation
        
        return 'Review the violation and apply appropriate fix according to flake8 documentation.'
    
    def batch_create_issues(
        self,
        violations: List[Dict[str, Any]],
        commit_sha: Optional[str] = None,
        pr_number: Optional[int] = None,
        max_issues: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Create multiple issues from a list of violations.
        
        Args:
            violations: List of violation dictionaries
            commit_sha: Optional commit SHA
            pr_number: Optional PR number
            max_issues: Maximum number of issues to create (prevents spam)
            
        Returns:
            List of created issue data
        """
        created_issues = []
        
        # Limit number of issues to prevent spam
        violations_to_process = violations[:max_issues]
        
        for violation in violations_to_process:
            issue = self.create_issue_from_violation(
                violation,
                commit_sha=commit_sha,
                pr_number=pr_number
            )
            if issue:
                created_issues.append(issue)
                print(f"Created issue #{issue['number']}: {issue['title']}")
        
        if len(violations) > max_issues:
            print(f"\nNote: {len(violations) - max_issues} additional violations not converted to issues (max limit: {max_issues})")
        
        return created_issues
    
    def generate_pr_comment(
        self,
        report: Dict[str, Any],
        created_issues: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Generate PR comment summarizing code quality analysis.
        
        Args:
            report: Code quality report dictionary
            created_issues: Optional list of created issues
            
        Returns:
            Markdown-formatted PR comment
        """
        summary = report.get('analysis_summary', {})
        passed = summary.get('passed', False)
        total = summary.get('total_violations', 0)
        severity = summary.get('severity_breakdown', {})
        
        status_emoji = "✅" if passed else "❌"
        
        lines = [
            f"## {status_emoji} Code Quality Analysis Results",
            "",
            f"**Status:** {'Passed' if passed else 'Failed'}",
            f"**Total Violations:** {total}",
            "",
            "### Severity Breakdown",
            f"- 🔴 Critical: {severity.get('critical', 0)}",
            f"- 🟠 High: {severity.get('high', 0)}",
            f"- 🟡 Medium: {severity.get('medium', 0)}",
            f"- 🟢 Low: {severity.get('low', 0)}",
        ]
        
        if created_issues:
            lines.extend([
                "",
                "### Automated Issues Created",
            ])
            for issue in created_issues:
                lines.append(f"- #{issue['number']}: {issue['title']}")
        
        lines.extend([
            "",
            "---",
            "*Analysis performed by Aurora Code Quality Analyzer (Issue #258)*",
        ])
        
        return "\n".join(lines)


def main():
    """CLI entry point for issue creation."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Create GitHub issues from code quality violations'
    )
    parser.add_argument(
        '--report',
        required=True,
        type=Path,
        help='Path to code quality report JSON'
    )
    parser.add_argument(
        '--owner',
        required=True,
        help='GitHub repository owner'
    )
    parser.add_argument(
        '--repo',
        required=True,
        help='GitHub repository name'
    )
    parser.add_argument(
        '--commit',
        help='Commit SHA where violations found'
    )
    parser.add_argument(
        '--pr',
        type=int,
        help='PR number where violations found'
    )
    parser.add_argument(
        '--max-issues',
        type=int,
        default=10,
        help='Maximum number of issues to create (default: 10)'
    )
    
    args = parser.parse_args()
    
    # Load report
    with open(args.report) as f:
        report = json.load(f)
    
    # Extract critical violations
    violations = report.get('violations', [])
    critical_violations = [
        v for v in violations
        if v.get('severity') == 'critical'
    ]
    
    if not critical_violations:
        print("No critical violations found - no issues will be created")
        return
    
    print(f"Found {len(critical_violations)} critical violations")
    
    # Create issue creator
    creator = CodeQualityIssueCreator(args.owner, args.repo)
    
    # Create issues
    created_issues = creator.batch_create_issues(
        critical_violations,
        commit_sha=args.commit,
        pr_number=args.pr,
        max_issues=args.max_issues
    )
    
    print(f"\nSuccessfully created {len(created_issues)} issues")


if __name__ == '__main__':
    main()
