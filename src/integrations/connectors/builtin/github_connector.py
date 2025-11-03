"""
GitHub API Connector

Provides integration with GitHub API while maintaining Aurora's
symbolic governance and DLP tracking protocols.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from ..auth import AuthType, create_auth_provider
from ..base import BaseConnector, ConnectorConfig, ConnectorStatus
from ..circuit_breaker import CircuitBreaker
from ..pooling import RateLimiter
from ..retry import RetryPolicy

# Graceful import of httpx
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


class GitHubConnector(BaseConnector):
    """
    GitHub API connector for R-2 agents.

    Provides methods to interact with GitHub repositories, issues,
    pull requests, and other GitHub resources.
    """

    def __init__(self, config: ConnectorConfig):
        super().__init__(config)

        # Initialize GitHub-specific components
        self.base_url = config.metadata.get("base_url", "https://api.github.com")
        self.api_version = config.metadata.get("api_version", "2022-11-28")

        # Authentication
        auth_type = config.metadata.get("auth_type", "bearer_token")
        self._auth_provider = create_auth_provider(
            AuthType(auth_type),
            config.auth_config or {}
        )

        # Resilience components
        self._rate_limiter = RateLimiter(
            requests_per_minute=config.rate_limit_rpm,
            name=f"github_{config.name}"
        )
        self._retry_policy = RetryPolicy(
            max_attempts=config.retry_attempts,
            backoff_factor=config.retry_backoff_factor,
            name=f"github_{config.name}"
        )
        self._circuit_breaker = CircuitBreaker(
            failure_threshold=config.circuit_breaker_threshold,
            timeout_seconds=config.circuit_breaker_timeout,
            name=f"github_{config.name}"
        )

        # HTTP client (initialized on connect)
        self._client: Optional[Any] = None

    async def connect(self) -> bool:
        """Establish connection to GitHub API"""
        try:
            # Authenticate
            if not await self._auth_provider.authenticate():
                return False

            # Create HTTP client if httpx available
            if HTTPX_AVAILABLE:
                self._client = httpx.AsyncClient(
                    base_url=self.base_url,
                    timeout=self.config.timeout_seconds,
                    headers=self._get_default_headers()
                )

            self.status = ConnectorStatus.CONNECTED
            return True

        except Exception as e:
            self.status = ConnectorStatus.ERROR
            return False

    async def disconnect(self) -> bool:
        """Disconnect from GitHub API"""
        try:
            if self._client and HTTPX_AVAILABLE:
                await self._client.aclose()
                self._client = None

            self.status = ConnectorStatus.DISCONNECTED
            return True

        except Exception:
            return False

    async def execute(self, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute GitHub API operation.

        Args:
            operation: Operation name (e.g., 'get_repository', 'list_issues')
            parameters: Operation parameters

        Returns:
            Dict containing operation result with DLP metadata
        """
        # Validate operation
        if not await self.validate_operation(operation, parameters):
            return {
                "success": False,
                "error": "Operation validation failed",
                **self.get_dlp_metadata()
            }

        # Route to appropriate handler
        handlers = {
            "get_repository": self._get_repository,
            "list_issues": self._list_issues,
            "create_issue": self._create_issue,
            "get_pull_request": self._get_pull_request,
            "list_pull_requests": self._list_pull_requests,
        }

        handler = handlers.get(operation)
        if not handler:
            return {
                "success": False,
                "error": f"Unknown operation: {operation}",
                **self.get_dlp_metadata()
            }

        try:
            # Execute with resilience patterns
            result = await self._execute_with_resilience(handler, parameters)
            return {
                "success": True,
                "operation": operation,
                "result": result,
                **self.get_dlp_metadata()
            }

        except Exception as e:
            return {
                "success": False,
                "operation": operation,
                "error": str(e),
                **self.get_dlp_metadata()
            }

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on GitHub connection"""
        if not self._client and not HTTPX_AVAILABLE:
            return {
                "status": "degraded",
                "message": "httpx not available, using mock mode",
                "timestamp": datetime.utcnow().isoformat(),
            }

        try:
            # Simple API call to check connectivity
            if self._client:
                response = await self._client.get("/rate_limit")
                if response.status_code == 200:
                    return {
                        "status": "healthy",
                        "rate_limit": response.json(),
                        "timestamp": datetime.utcnow().isoformat(),
                    }

            return {
                "status": "healthy",
                "message": "Mock mode active",
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for GitHub API requests"""
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": self.api_version,
        }
        headers.update(self._auth_provider.get_auth_headers())
        return headers

    async def _execute_with_resilience(self, handler, parameters: Dict[str, Any]) -> Any:
        """Execute handler with rate limiting, retry, and circuit breaker"""
        # Rate limiting
        await self._rate_limiter.wait_for_token()

        # Circuit breaker and retry
        async def wrapped_call():
            return await self._retry_policy.execute(handler, parameters)

        return await self._circuit_breaker.call(wrapped_call)

    async def _get_repository(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get repository information"""
        owner = parameters.get("owner")
        repo = parameters.get("repo")

        if not owner or not repo:
            raise ValueError("Missing required parameters: owner, repo")

        if self._client:
            response = await self._client.get(f"/repos/{owner}/{repo}")
            response.raise_for_status()
            return response.json()

        # Mock response for testing
        return {
            "id": 12345,
            "name": repo,
            "full_name": f"{owner}/{repo}",
            "owner": {"login": owner},
            "mock": True,
        }

    async def _list_issues(self, parameters: Dict[str, Any]) -> list:
        """List repository issues"""
        owner = parameters.get("owner")
        repo = parameters.get("repo")
        state = parameters.get("state", "open")

        if not owner or not repo:
            raise ValueError("Missing required parameters: owner, repo")

        if self._client:
            response = await self._client.get(
                f"/repos/{owner}/{repo}/issues",
                params={"state": state}
            )
            response.raise_for_status()
            return response.json()

        # Mock response
        return [{"id": 1, "title": "Mock Issue", "state": state, "mock": True}]

    async def _create_issue(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new issue"""
        owner = parameters.get("owner")
        repo = parameters.get("repo")
        title = parameters.get("title")
        body = parameters.get("body", "")

        if not owner or not repo or not title:
            raise ValueError("Missing required parameters: owner, repo, title")

        if self._client:
            response = await self._client.post(
                f"/repos/{owner}/{repo}/issues",
                json={"title": title, "body": body}
            )
            response.raise_for_status()
            return response.json()

        # Mock response
        return {"id": 999, "title": title, "body": body, "mock": True}

    async def _get_pull_request(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get pull request information"""
        owner = parameters.get("owner")
        repo = parameters.get("repo")
        number = parameters.get("number")

        if not owner or not repo or not number:
            raise ValueError("Missing required parameters: owner, repo, number")

        if self._client:
            response = await self._client.get(f"/repos/{owner}/{repo}/pulls/{number}")
            response.raise_for_status()
            return response.json()

        # Mock response
        return {"id": number, "title": "Mock PR", "state": "open", "mock": True}

    async def _list_pull_requests(self, parameters: Dict[str, Any]) -> list:
        """List repository pull requests"""
        owner = parameters.get("owner")
        repo = parameters.get("repo")
        state = parameters.get("state", "open")

        if not owner or not repo:
            raise ValueError("Missing required parameters: owner, repo")

        if self._client:
            response = await self._client.get(
                f"/repos/{owner}/{repo}/pulls",
                params={"state": state}
            )
            response.raise_for_status()
            return response.json()

        # Mock response
        return [{"id": 1, "title": "Mock PR", "state": state, "mock": True}]
