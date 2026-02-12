import os
import sys
import logging
import argparse
from typing import Any
import pandas as pd
from pycaret.datasets import get_data
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
from pydantic import AnyUrl

# Reconfigure UnicodeEncodeError prone default (i.e. windows-1252) to utf-8
if sys.platform == "win32" and os.environ.get('PYTHONIOENCODING') is None:
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

logger = logging.getLogger('pycaret_mcp')
logger.setLevel(logging.DEBUG)
logger.info("Starting PyCaret MCP Server")

server = Server("pycaret-server")

# Available PyCaret datasets (commonly used ones)
AVAILABLE_DATASETS = [
    "diabetes", "iris", "credit", "juice", "bank", "blood",
    "cancer", "heart", "hepatitis", "income", "insurance",
    "parkinsons", "pokemon", "satellite", "telescope", "wine"
]

# Store loaded dataset
current_dataset: pd.DataFrame | None = None
current_dataset_name: str = ""


@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """List available resources"""
    logger.debug("Handling list_resources request")
    resources = [
        types.Resource(
            uri=AnyUrl("memo://datasets"),
            name="Available Datasets",
            description="List of all available PyCaret sample datasets",
            mimeType="text/plain",
        )
    ]
    
    if current_dataset is not None:
        resources.append(
            types.Resource(
                uri=AnyUrl(f"memo://current_dataset"),
                name=f"Current Dataset: {current_dataset_name}",
                description=f"Information about the currently loaded dataset: {current_dataset_name}",
                mimeType="text/plain",
            )
        )
    
    return resources


@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    """Read resource content"""
    logger.debug("Handling read_resource request for URI: %s", uri)
    if uri.scheme != "memo":
        logger.error("Unsupported URI scheme: %s", uri.scheme)
        raise ValueError(f"Unsupported URI scheme: {uri.scheme}")

    path = str(uri).replace("memo://", "")
    
    if path == "datasets":
        return "\n".join([f"- {name}" for name in AVAILABLE_DATASETS])
    elif path == "current_dataset":
        if current_dataset is None:
            return "No dataset loaded"
        info = f"Dataset: {current_dataset_name}\n"
        info += f"Shape: {current_dataset.shape}\n"
        info += f"Columns: {', '.join(current_dataset.columns.tolist())}\n"
        info += f"\nFirst 5 rows:\n{current_dataset.head().to_string()}"
        return info
    else:
        logger.error(f"Unknown resource path: {path}")
        raise ValueError(f"Unknown resource path: {path}")


@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    """List available prompts"""
    logger.debug("Handling list_prompts request")
    return []


@server.get_prompt()
async def handle_get_prompt(name: str, arguments: dict[str, str] | None) -> types.GetPromptResult:
    """Get a specific prompt"""
    logger.debug(f"Handling get_prompt request for {name} with args {arguments}")
    raise ValueError(f"Unknown prompt: {name}")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools"""
    return [
        types.Tool(
            name="list_datasets",
            description="List all available PyCaret sample datasets",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        types.Tool(
            name="load_dataset",
            description="Load a specific PyCaret dataset by name",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_name": {
                        "type": "string",
                        "description": "Name of the dataset to load (e.g., 'diabetes', 'iris', 'credit')",
                        "enum": AVAILABLE_DATASETS,
                    },
                },
                "required": ["dataset_name"],
            },
        ),
        types.Tool(
            name="get_dataset_info",
            description="Get detailed information about the currently loaded dataset",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        types.Tool(
            name="get_dataset_shape",
            description="Get the shape (rows, columns) of the currently loaded dataset",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        types.Tool(
            name="get_column_info",
            description="Get information about a specific column in the current dataset",
            inputSchema={
                "type": "object",
                "properties": {
                    "column_name": {
                        "type": "string",
                        "description": "Name of the column to get information about",
                    },
                },
                "required": ["column_name"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any] | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool execution requests"""
    global current_dataset, current_dataset_name
    
    try:
        if name == "list_datasets":
            datasets_list = "\n".join([f"{i+1}. {name}" for i, name in enumerate(AVAILABLE_DATASETS)])
            return [types.TextContent(
                type="text",
                text=f"Available PyCaret datasets:\n\n{datasets_list}\n\nUse 'load_dataset' to load any of these datasets."
            )]
        
        elif name == "load_dataset":
            if not arguments:
                raise ValueError("Missing arguments")
            
            dataset_name = arguments.get("dataset_name")
            if not dataset_name:
                raise ValueError("dataset_name is required")
            
            if dataset_name not in AVAILABLE_DATASETS:
                raise ValueError(f"Dataset '{dataset_name}' not found. Available datasets: {', '.join(AVAILABLE_DATASETS)}")
            
            logger.info(f"Loading dataset: {dataset_name}")
            current_dataset = get_data(dataset_name)
            current_dataset_name = dataset_name
            
            info = f"Successfully loaded dataset: {dataset_name}\n\n"
            info += f"Shape: {current_dataset.shape[0]} rows, {current_dataset.shape[1]} columns\n"
            info += f"Columns: {', '.join(current_dataset.columns.tolist())}\n\n"
            info += f"First 5 rows:\n{current_dataset.head().to_string()}\n\n"
            info += f"Data types:\n{current_dataset.dtypes.to_string()}"
            
            return [types.TextContent(type="text", text=info)]
        
        elif name == "get_dataset_info":
            if current_dataset is None:
                return [types.TextContent(
                    type="text",
                    text="No dataset loaded. Use 'load_dataset' first."
                )]
            
            info = f"Dataset: {current_dataset_name}\n\n"
            info += f"Shape: {current_dataset.shape[0]} rows, {current_dataset.shape[1]} columns\n\n"
            info += f"Columns:\n{current_dataset.columns.tolist()}\n\n"
            info += f"Data types:\n{current_dataset.dtypes.to_string()}\n\n"
            info += f"Missing values:\n{current_dataset.isnull().sum().to_string()}\n\n"
            info += f"Summary statistics:\n{current_dataset.describe().to_string()}"
            
            return [types.TextContent(type="text", text=info)]
        
        elif name == "get_dataset_shape":
            if current_dataset is None:
                return [types.TextContent(
                    type="text",
                    text="No dataset loaded. Use 'load_dataset' first."
                )]
            
            return [types.TextContent(
                type="text",
                text=f"Dataset '{current_dataset_name}' shape: {current_dataset.shape[0]} rows, {current_dataset.shape[1]} columns"
            )]
        
        elif name == "get_column_info":
            if current_dataset is None:
                return [types.TextContent(
                    type="text",
                    text="No dataset loaded. Use 'load_dataset' first."
                )]
            
            if not arguments:
                raise ValueError("Missing arguments")
            
            column_name = arguments.get("column_name")
            if not column_name:
                raise ValueError("column_name is required")
            
            if column_name not in current_dataset.columns:
                return [types.TextContent(
                    type="text",
                    text=f"Column '{column_name}' not found. Available columns: {', '.join(current_dataset.columns.tolist())}"
                )]
            
            col_data = current_dataset[column_name]
            info = f"Column: {column_name}\n\n"
            info += f"Data type: {col_data.dtype}\n"
            info += f"Non-null count: {col_data.count()}\n"
            info += f"Null count: {col_data.isnull().sum()}\n\n"
            
            if pd.api.types.is_numeric_dtype(col_data):
                info += f"Statistics:\n{col_data.describe().to_string()}\n\n"
            else:
                info += f"Unique values: {col_data.nunique()}\n"
                info += f"Top values:\n{col_data.value_counts().head(10).to_string()}"
            
            return [types.TextContent(type="text", text=info)]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        logger.error(f"Error executing tool {name}: {str(e)}")
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]


async def run_server() -> None:
    """Run the MCP server"""
    logger.info("Starting PyCaret MCP Server")
    
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        logger.info("Server running with stdio transport")
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="pycaret",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="PyCaret MCP Server")
    parser.add_argument("--version", action="version", version="0.1.0")
    args = parser.parse_args()
    
    import asyncio
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
