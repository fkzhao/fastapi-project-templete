"""
MCP (Model Context Protocol) SSE Server
Provides SSE-based MCP server for AI model context sharing
"""
import logging
import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, Request, HTTPException, Header
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel

from src.core.mcp_config import get_mcp_config

logger = logging.getLogger(__name__)


# ============ MCP Data Models ============

class MCPTool(BaseModel):
    """MCP Tool definition"""
    name: str
    description: str
    input_schema: Dict[str, Any]


class MCPResource(BaseModel):
    """MCP Resource definition"""
    uri: str
    name: str
    description: str
    mime_type: Optional[str] = None


class MCPPrompt(BaseModel):
    """MCP Prompt definition"""
    name: str
    description: str
    arguments: List[Dict[str, Any]] = []


class MCPServerInfo(BaseModel):
    """MCP Server information"""
    name: str
    version: str
    protocol_version: str = "2024-11-05"
    capabilities: Dict[str, Any]


# ============ MCP Server Implementation ============

class MCPSSEServer:
    """
    MCP SSE Server implementation.
    Handles MCP protocol over Server-Sent Events.
    """

    def __init__(self):
        self.config = get_mcp_config()
        self.router = APIRouter()
        self.tools: Dict[str, MCPTool] = {}
        self.resources: Dict[str, MCPResource] = {}
        self.prompts: Dict[str, MCPPrompt] = {}
        self._setup_routes()

    def _setup_routes(self):
        """Setup MCP SSE routes"""

        @self.router.get(self.config.mcp_endpoint)
        async def mcp_sse_endpoint(
            request: Request,
            authorization: Optional[str] = Header(None)
        ):
            """MCP SSE endpoint for streaming protocol messages"""

            # Authentication check
            if self.config.mcp_require_auth:
                if not authorization or not self._verify_auth(authorization):
                    raise HTTPException(status_code=401, detail="Unauthorized")

            logger.info(f"MCP SSE connection established from {request.client.host}")

            return EventSourceResponse(
                self._event_generator(request),
                headers={
                    "Cache-Control": "no-cache",
                    "X-Accel-Buffering": "no",
                }
            )

        @self.router.get(f"{self.config.mcp_endpoint}/info")
        async def mcp_info():
            """Get MCP server information"""
            return self.get_server_info()

        @self.router.get(f"{self.config.mcp_endpoint}/tools")
        async def mcp_list_tools():
            """List available MCP tools"""
            return {"tools": list(self.tools.values())}

        @self.router.get(f"{self.config.mcp_endpoint}/resources")
        async def mcp_list_resources():
            """List available MCP resources"""
            return {"resources": list(self.resources.values())}

        @self.router.get(f"{self.config.mcp_endpoint}/prompts")
        async def mcp_list_prompts():
            """List available MCP prompts"""
            return {"prompts": list(self.prompts.values())}

    def _verify_auth(self, authorization: str) -> bool:
        """Verify authentication token"""
        if not self.config.mcp_api_key:
            return True

        # Support both "Bearer <token>" and direct token
        token = authorization.replace("Bearer ", "").strip()
        return token == self.config.mcp_api_key

    async def _event_generator(self, request: Request):
        """
        Generate SSE events for MCP protocol.

        Args:
            request: FastAPI request object

        Yields:
            SSE event messages
        """
        try:
            # Send server info on connection
            yield {
                "event": "server_info",
                "data": json.dumps(self.get_server_info().model_dump()),
                "retry": self.config.mcp_sse_retry
            }

            # Keep connection alive with periodic pings
            while True:
                if await request.is_disconnected():
                    logger.info("MCP SSE client disconnected")
                    break

                # Send ping to keep connection alive
                yield {
                    "event": "ping",
                    "data": json.dumps({
                        "timestamp": datetime.now().isoformat()
                    })
                }

                await asyncio.sleep(self.config.mcp_sse_ping_interval)

        except asyncio.CancelledError:
            logger.info("MCP SSE connection cancelled")
        except Exception as e:
            logger.error(f"MCP SSE error: {e}")
            raise

    def get_server_info(self) -> MCPServerInfo:
        """Get MCP server information"""
        capabilities = {}

        if self.config.mcp_enable_tools:
            capabilities["tools"] = {"list": True, "call": True}

        if self.config.mcp_enable_resources:
            capabilities["resources"] = {"list": True, "read": True}

        if self.config.mcp_enable_prompts:
            capabilities["prompts"] = {"list": True, "get": True}

        return MCPServerInfo(
            name=self.config.mcp_server_name,
            version=self.config.mcp_server_version,
            capabilities=capabilities
        )

    def register_tool(self, tool: MCPTool):
        """Register an MCP tool"""
        self.tools[tool.name] = tool
        logger.info(f"Registered MCP tool: {tool.name}")

    def register_resource(self, resource: MCPResource):
        """Register an MCP resource"""
        self.resources[resource.uri] = resource
        logger.info(f"Registered MCP resource: {resource.uri}")

    def register_prompt(self, prompt: MCPPrompt):
        """Register an MCP prompt"""
        self.prompts[prompt.name] = prompt
        logger.info(f"Registered MCP prompt: {prompt.name}")

    def get_router(self) -> APIRouter:
        """Get the FastAPI router for MCP endpoints"""
        return self.router


# ============ Global MCP Server Instance ============

_mcp_server: Optional[MCPSSEServer] = None


def get_mcp_server() -> MCPSSEServer:
    """Get or create the global MCP server instance"""
    global _mcp_server
    if _mcp_server is None:
        _mcp_server = MCPSSEServer()
    return _mcp_server


def init_mcp_server(app) -> Optional[MCPSSEServer]:
    """
    Initialize MCP SSE server if enabled.

    Args:
        app: FastAPI application instance

    Returns:
        MCPSSEServer instance if enabled, None otherwise
    """
    config = get_mcp_config()

    if not config.mcp_enabled:
        logger.info("MCP SSE server is disabled")
        return None

    logger.info("Initializing MCP SSE server...")
    logger.info(f"  Endpoint: {config.mcp_endpoint}")
    logger.info(f"  Server Name: {config.mcp_server_name}")
    logger.info(f"  Authentication: {'Enabled' if config.mcp_require_auth else 'Disabled'}")
    logger.info(f"  Tools: {'Enabled' if config.mcp_enable_tools else 'Disabled'}")
    logger.info(f"  Resources: {'Enabled' if config.mcp_enable_resources else 'Disabled'}")
    logger.info(f"  Prompts: {'Enabled' if config.mcp_enable_prompts else 'Disabled'}")

    mcp_server = get_mcp_server()

    # Register example tools, resources, and prompts
    _register_example_capabilities(mcp_server)

    # Include MCP router in the app
    app.include_router(
        mcp_server.get_router(),
        tags=["MCP SSE Server"]
    )

    logger.info("MCP SSE server initialized successfully")
    return mcp_server


def _register_example_capabilities(mcp_server: MCPSSEServer):
    """Register example MCP capabilities"""

    # Example Tool
    if mcp_server.config.mcp_enable_tools:
        mcp_server.register_tool(MCPTool(
            name="get_user_info",
            description="Get information about a user by ID",
            input_schema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "integer",
                        "description": "The user ID to query"
                    }
                },
                "required": ["user_id"]
            }
        ))

    # Example Resource
    if mcp_server.config.mcp_enable_resources:
        mcp_server.register_resource(MCPResource(
            uri="api://users/list",
            name="Users List",
            description="List of all users in the system",
            mime_type="application/json"
        ))

    # Example Prompt
    if mcp_server.config.mcp_enable_prompts:
        mcp_server.register_prompt(MCPPrompt(
            name="summarize_user",
            description="Generate a summary of user information",
            arguments=[
                {
                    "name": "user_id",
                    "description": "The user ID to summarize",
                    "required": True
                }
            ]
        ))


__all__ = [
    "MCPSSEServer",
    "MCPTool",
    "MCPResource",
    "MCPPrompt",
    "get_mcp_server",
    "init_mcp_server"
]

