"""
MCP (Model Context Protocol) SSE Server Configuration
"""
from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Optional


class MCPConfig(BaseSettings):
    """
    MCP SSE Server configuration.
    All settings can be overridden via environment variables.
    """

    # MCP Server Configuration
    mcp_enabled: bool = Field(default=False, description="Enable MCP SSE server")
    mcp_endpoint: str = Field(default="/mcp/sse", description="MCP SSE endpoint path")
    mcp_server_name: str = Field(default="FastAPI MCP Server", description="MCP server name")
    mcp_server_version: str = Field(default="0.1.0", description="MCP server version")

    # SSE Configuration
    mcp_sse_retry: int = Field(default=15000, description="SSE retry interval in milliseconds")
    mcp_sse_ping_interval: int = Field(default=30, description="SSE ping interval in seconds")

    # Security
    mcp_require_auth: bool = Field(default=False, description="Require authentication for MCP")
    mcp_api_key: Optional[str] = Field(default=None, description="API key for MCP authentication")

    # Features
    mcp_enable_tools: bool = Field(default=True, description="Enable MCP tools")
    mcp_enable_resources: bool = Field(default=True, description="Enable MCP resources")
    mcp_enable_prompts: bool = Field(default=True, description="Enable MCP prompts")

    class Config:
        env_prefix = "MCP_"
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global MCP configuration instance
mcp_config = MCPConfig()
mcp_config.mcp_enabled = True

def get_mcp_config() -> MCPConfig:
    """Get the global MCP configuration instance"""
    return mcp_config

