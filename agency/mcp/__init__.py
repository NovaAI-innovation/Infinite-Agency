"""
MCP (Model Context Protocol) integration for the agency system.
Enables integration with external tools and services through standardized protocols.
"""
import asyncio
import json
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod
import aiohttp
from ..utils.logger import get_logger


class MCPTransportType(Enum):
    """Types of transports supported by MCP"""
    HTTP = "http"
    SSE = "sse"
    STDIO = "stdio"
    WEBSOCKET = "websocket"


@dataclass
class MCPCapability:
    """Represents an MCP capability"""
    name: str
    description: str
    parameters: Dict[str, Any]
    result_schema: Dict[str, Any]


@dataclass
class MCPToolCall:
    """Represents a call to an MCP tool"""
    tool_name: str
    parameters: Dict[str, Any]
    call_id: str


@dataclass
class MCPToolResult:
    """Represents the result of an MCP tool call"""
    call_id: str
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class MCPClient(ABC):
    """Abstract base class for MCP clients"""

    @abstractmethod
    async def connect(self):
        """Connect to the MCP server"""
        pass

    @abstractmethod
    async def disconnect(self):
        """Disconnect from the MCP server"""
        pass

    @abstractmethod
    async def list_capabilities(self) -> List[MCPCapability]:
        """List available capabilities from the MCP server"""
        pass

    @abstractmethod
    async def call_tool(self, tool_call: MCPToolCall) -> MCPToolResult:
        """Call a tool on the MCP server"""
        pass


class HTTPMCPClient(MCPClient):
    """HTTP-based MCP client implementation"""

    def __init__(self, server_url: str, api_key: Optional[str] = None):
        self.server_url = server_url
        self.api_key = api_key
        self.session: Optional[aiohttp.ClientSession] = None
        self._logger = get_logger(__name__)

    async def connect(self):
        """Connect to the MCP server"""
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        self.session = aiohttp.ClientSession(headers=headers)
        self._logger.info(f"Connected to MCP server at {self.server_url}")

    async def disconnect(self):
        """Disconnect from the MCP server"""
        if self.session:
            await self.session.close()
            self._logger.info(f"Disconnected from MCP server at {self.server_url}")

    async def list_capabilities(self) -> List[MCPCapability]:
        """List available capabilities from the MCP server"""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")

        try:
            async with self.session.get(f"{self.server_url}/capabilities") as response:
                response.raise_for_status()
                data = await response.json()

                capabilities = []
                for cap_data in data.get("capabilities", []):
                    capability = MCPCapability(
                        name=cap_data["name"],
                        description=cap_data["description"],
                        parameters=cap_data.get("parameters", {}),
                        result_schema=cap_data.get("result_schema", {})
                    )
                    capabilities.append(capability)

                return capabilities
        except Exception as e:
            self._logger.error(f"Error listing capabilities: {e}")
            return []

    async def call_tool(self, tool_call: MCPToolCall) -> MCPToolResult:
        """Call a tool on the MCP server"""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")

        try:
            payload = {
                "tool_name": tool_call.tool_name,
                "parameters": tool_call.parameters,
                "call_id": tool_call.call_id
            }

            async with self.session.post(f"{self.server_url}/tools/call", json=payload) as response:
                response.raise_for_status()
                result_data = await response.json()

                return MCPToolResult(
                    call_id=tool_call.call_id,
                    success=result_data.get("success", False),
                    result=result_data.get("result"),
                    error=result_data.get("error")
                )
        except Exception as e:
            self._logger.error(f"Error calling tool {tool_call.tool_name}: {e}")
            return MCPToolResult(
                call_id=tool_call.call_id,
                success=False,
                error=str(e)
            )


class MCPServerManager:
    """Manages connections to multiple MCP servers"""

    def __init__(self):
        self.clients: Dict[str, MCPClient] = {}
        self.capabilities_cache: Dict[str, List[MCPCapability]] = {}
        self._logger = get_logger(__name__)

    async def register_server(self, name: str, client: MCPClient):
        """Register an MCP server with the manager"""
        await client.connect()
        self.clients[name] = client
        self.capabilities_cache[name] = await client.list_capabilities()
        self._logger.info(f"Registered MCP server: {name}")

    async def unregister_server(self, name: str):
        """Unregister an MCP server"""
        if name in self.clients:
            await self.clients[name].disconnect()
            del self.clients[name]
            if name in self.capabilities_cache:
                del self.capabilities_cache[name]
            self._logger.info(f"Unregistered MCP server: {name}")

    async def call_tool(self, server_name: str, tool_name: str, parameters: Dict[str, Any]) -> MCPToolResult:
        """Call a tool on a specific server"""
        if server_name not in self.clients:
            raise ValueError(f"MCP server {server_name} not registered")

        client = self.clients[server_name]
        call_id = f"mcp_call_{hash(str(parameters)) % 10000}"

        tool_call = MCPToolCall(
            tool_name=tool_name,
            parameters=parameters,
            call_id=call_id
        )

        result = await client.call_tool(tool_call)
        return result

    def get_available_tools(self, server_name: str) -> List[MCPCapability]:
        """Get available tools for a specific server"""
        return self.capabilities_cache.get(server_name, [])

    def get_all_tools(self) -> Dict[str, List[MCPCapability]]:
        """Get all available tools from all registered servers"""
        return self.capabilities_cache.copy()


# Integration with agency components
class MCPIntegration:
    """Integrates MCP with agency components for enhanced functionality"""

    def __init__(self, mcp_manager: MCPServerManager):
        self.mcp_manager = mcp_manager
        self._logger = get_logger(__name__)

    async def register_external_tool_server(self, name: str, server_url: str, api_key: Optional[str] = None):
        """Register an external tool server via MCP"""
        client = HTTPMCPClient(server_url, api_key)
        await self.mcp_manager.register_server(name, client)
        self._logger.info(f"Registered external tool server '{name}' at {server_url}")

    async def execute_external_tool(self, server_name: str, tool_name: str, parameters: Dict[str, Any]) -> Optional[Any]:
        """Execute an external tool via MCP"""
        try:
            result = await self.mcp_manager.call_tool(server_name, tool_name, parameters)
            if result.success:
                return result.result
            else:
                self._logger.error(f"External tool execution failed: {result.error}")
                return None
        except Exception as e:
            self._logger.error(f"Error executing external tool: {e}")
            return None

    def get_available_external_tools(self, server_name: str) -> List[str]:
        """Get list of available external tools from a server"""
        capabilities = self.mcp_manager.get_available_tools(server_name)
        return [cap.name for cap in capabilities]


# Global MCP manager instance
mcp_manager = MCPServerManager()
mcp_integration = MCPIntegration(mcp_manager)


def get_mcp_manager() -> MCPServerManager:
    """Get the global MCP manager instance"""
    return mcp_manager


def get_mcp_integration() -> MCPIntegration:
    """Get the global MCP integration instance"""
    return mcp_integration