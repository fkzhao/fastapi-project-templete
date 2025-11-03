"""
Base Repository Class
Provides common HTTP request methods with timeout and retry mechanism.
"""
import logging
import time
from typing import Any, Dict, Optional, Literal
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import (
    RequestException,
    Timeout,
    ConnectionError,
    HTTPError
)
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class RalRepositoryException(Exception):
    """Base exception for repository operations"""
    pass


class RequestTimeoutException(RalRepositoryException):
    """Request timeout exception"""
    pass


class RequestRetryExhaustedException(RalRepositoryException):
    """All retry attempts exhausted"""
    pass


class RalRepository:
    """
    Base repository class with HTTP request capabilities.
    Supports GET, POST, PUT, PATCH, DELETE methods with automatic retry and timeout handling.
    """

    def __init__(
            self,
            base_url: str = "",
            timeout: int = 30,
            max_retries: int = 3,
            backoff_factor: float = 0.5,
            retry_on_status: tuple[int, ...] = (500, 502, 503, 504),
            default_headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize base repository.

        Args:
            base_url: Base URL for all requests
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum number of retry attempts (default: 3)
            backoff_factor: Backoff factor for retry delays (default: 0.5)
                           {backoff factor} * (2 ** ({number of total retries} - 1))
            retry_on_status: HTTP status codes to retry on (default: 500, 502, 503, 504)
            default_headers: Default headers for all requests
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.retry_on_status = retry_on_status
        self.default_headers = default_headers or {}

        # Create session with retry strategy
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """
        Create requests session with retry strategy.

        Returns:
            Configured requests.Session
        """
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=self.backoff_factor,
            status_forcelist=self.retry_on_status,
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST", "PATCH"],
            raise_on_status=False
        )

        # Mount adapter with retry strategy
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Set default headers
        session.headers.update(self.default_headers)

        return session

    def _build_url(self, endpoint: str) -> str:
        """
        Build full URL from base_url and endpoint.

        Args:
            endpoint: API endpoint

        Returns:
            Full URL
        """
        if endpoint.startswith(("http://", "https://")):
            return endpoint
        return urljoin(self.base_url + "/", endpoint.lstrip("/"))

    def _log_request(
            self,
            method: str,
            url: str,
            params: Optional[Dict] = None,
            data: Any = None,
            headers: Optional[Dict] = None
    ):
        """Log request details"""
        logger.debug(f"Base Url: {self.base_url} {url}")
        logger.debug(f"Request: {method} {url}")
        if params:
            logger.debug(f"  Params: {params}")
        if data:
            logger.debug(f"  Data: {data}")
        if headers:
            logger.debug(f"  Headers: {headers}")

    def _log_response(
            self,
            response: requests.Response,
            duration: float
    ):
        """Log response details"""
        logger.debug(f"Base Url: {self.base_url}")
        logger.info(
            f"Repositories: {response.status_code} - "
            f"{response.request.method} {response.url} - "
            f"{round(duration * 1000, 2)}ms"
        )

    def _request(
            self,
            method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"],
            endpoint: str,
            params: Optional[Dict[str, Any]] = None,
            data: Optional[Any] = None,
            json: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            timeout: Optional[int] = None,
            **kwargs
    ) -> requests.Response:
        """
        Internal method to make HTTP requests with retry and timeout handling.

        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)
            endpoint: API endpoint (will be joined with base_url)
            params: URL query parameters
            data: Request body data (form data)
            json: Request body as JSON
            headers: Additional headers for this request
            timeout: Request timeout (overrides default)
            **kwargs: Additional arguments passed to requests

        Returns:
            requests.Response object

        Raises:
            RequestTimeoutException: If request times out
            RequestRetryExhaustedException: If all retry attempts fail
            RepositoryException: For other request errors
        """
        url = self._build_url(endpoint)
        request_timeout = timeout or self.timeout
        request_headers = {**self.default_headers, **(headers or {})}

        self._log_request(method, url, params, data or json, request_headers)

        start_time = time.time()

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json,
                headers=request_headers,
                timeout=request_timeout,
                **kwargs
            )

            duration = time.time() - start_time
            self._log_response(response, duration)

            # Raise HTTPError for bad status codes (4xx, 5xx)
            response.raise_for_status()

            return response

        except Timeout as e:
            duration = time.time() - start_time
            logger.error(f"Request timeout after {duration:.2f}s: {method} {url}")
            raise RequestTimeoutException(
                f"Request timeout after {request_timeout}s: {method} {url}"
            ) from e

        except ConnectionError as e:
            logger.error(f"Connection error: {method} {url} - {str(e)}")
            raise RequestRetryExhaustedException(
                f"Connection failed after {self.max_retries} retries: {method} {url}"
            ) from e

        except HTTPError as e:
            logger.error(
                f"HTTP error {e.response.status_code}: {method} {url} - {e.response.text[:200]}"
            )
            raise RalRepositoryException(
                f"HTTP {e.response.status_code}: {e.response.text[:200]}"
            ) from e

        except RequestException as e:
            logger.error(f"Request failed: {method} {url} - {str(e)}")
            raise RalRepositoryException(f"Request failed: {str(e)}") from e

    def get(
            self,
            endpoint: str,
            params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            timeout: Optional[int] = None,
            **kwargs
    ) -> requests.Response:
        """
        Send GET request.

        Args:
            endpoint: API endpoint
            params: URL query parameters
            headers: Additional headers
            timeout: Request timeout
            **kwargs: Additional arguments

        Returns:
            requests.Response object
        """
        return self._request("GET", endpoint, params=params, headers=headers, timeout=timeout, **kwargs)

    def post(
            self,
            endpoint: str,
            data: Optional[Any] = None,
            json: Optional[Dict[str, Any]] = None,
            params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            timeout: Optional[int] = None,
            **kwargs
    ) -> requests.Response:
        """
        Send POST request.

        Args:
            endpoint: API endpoint
            data: Request body data (form data)
            json: Request body as JSON
            params: URL query parameters
            headers: Additional headers
            timeout: Request timeout
            **kwargs: Additional arguments

        Returns:
            requests.Response object
        """
        return self._request("POST", endpoint, params=params, data=data, json=json, headers=headers, timeout=timeout,
                             **kwargs)

    def put(
            self,
            endpoint: str,
            data: Optional[Any] = None,
            json: Optional[Dict[str, Any]] = None,
            params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            timeout: Optional[int] = None,
            **kwargs
    ) -> requests.Response:
        """
        Send PUT request.

        Args:
            endpoint: API endpoint
            data: Request body data (form data)
            json: Request body as JSON
            params: URL query parameters
            headers: Additional headers
            timeout: Request timeout
            **kwargs: Additional arguments

        Returns:
            requests.Response object
        """
        return self._request("PUT", endpoint, params=params, data=data, json=json, headers=headers, timeout=timeout,
                             **kwargs)

    def patch(
            self,
            endpoint: str,
            data: Optional[Any] = None,
            json: Optional[Dict[str, Any]] = None,
            params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            timeout: Optional[int] = None,
            **kwargs
    ) -> requests.Response:
        """
        Send PATCH request.

        Args:
            endpoint: API endpoint
            data: Request body data (form data)
            json: Request body as JSON
            params: URL query parameters
            headers: Additional headers
            timeout: Request timeout
            **kwargs: Additional arguments

        Returns:
            requests.Response object
        """
        return self._request("PATCH", endpoint, params=params, data=data, json=json, headers=headers, timeout=timeout,
                             **kwargs)

    def delete(
            self,
            endpoint: str,
            params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            timeout: Optional[int] = None,
            **kwargs
    ) -> requests.Response:
        """
        Send DELETE request.

        Args:
            endpoint: API endpoint
            params: URL query parameters
            headers: Additional headers
            timeout: Request timeout
            **kwargs: Additional arguments

        Returns:
            requests.Response object
        """
        return self._request("DELETE", endpoint, params=params, headers=headers, timeout=timeout, **kwargs)

    def close(self):
        """Close the session and release resources"""
        if self.session:
            self.session.close()
            logger.debug("Session closed")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
