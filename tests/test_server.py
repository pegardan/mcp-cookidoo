"""Tests for MCP server tools via in-process FastMCP Client."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastmcp import Client

import server
from server import mcp


def _get_text(result) -> str:
    """Extract text from a CallToolResult."""
    return result.content[0].text


# ---------------------------------------------------------------------------
# generate_recipe_structure
# ---------------------------------------------------------------------------


async def test_generate_recipe_newline_ingredients():
    async with Client(mcp) as client:
        result = await client.call_tool(
            "generate_recipe_structure",
            {
                "name": "Pasta",
                "ingredients": "200g pasta\n100ml sauce\n1 onion",
                "steps": "Boil water\nCook pasta",
            },
        )
    text = _get_text(result)
    assert "validated successfully" in text
    data = json.loads(text.split("validated successfully!\n\n")[1].split("\n\nYou")[0])
    assert len(data["ingredients"]) == 3
    assert data["ingredients"][0] == "200g pasta"


async def test_generate_recipe_comma_ingredients():
    async with Client(mcp) as client:
        result = await client.call_tool(
            "generate_recipe_structure",
            {
                "name": "Salad",
                "ingredients": "lettuce,tomato,olive oil",
                "steps": "Mix everything",
            },
        )
    text = _get_text(result)
    assert "validated successfully" in text
    data = json.loads(text.split("validated successfully!\n\n")[1].split("\n\nYou")[0])
    assert len(data["ingredients"]) == 3
    assert "lettuce" in data["ingredients"]


async def test_generate_recipe_numbered_steps_stripped():
    async with Client(mcp) as client:
        result = await client.call_tool(
            "generate_recipe_structure",
            {
                "name": "Cake",
                "ingredients": "flour,eggs",
                "steps": "1. Mix ingredients\n2. Bake at 180°C\n3. Let cool",
            },
        )
    text = _get_text(result)
    assert "validated successfully" in text
    data = json.loads(text.split("validated successfully!\n\n")[1].split("\n\nYou")[0])
    assert data["steps"][0] == "Mix ingredients"
    assert data["steps"][1] == "Bake at 180°C"
    assert data["steps"][2] == "Let cool"


async def test_generate_recipe_hints_parsed():
    async with Client(mcp) as client:
        result = await client.call_tool(
            "generate_recipe_structure",
            {
                "name": "Cookies",
                "ingredients": "flour,butter",
                "steps": "Mix\nBake",
                "hints": "Don't overmix\nLet cool before eating",
            },
        )
    text = _get_text(result)
    assert "validated successfully" in text
    data = json.loads(text.split("validated successfully!\n\n")[1].split("\n\nYou")[0])
    assert data["hints"] is not None
    assert len(data["hints"]) == 2


async def test_generate_recipe_servings_out_of_range_returns_error():
    async with Client(mcp) as client:
        result = await client.call_tool(
            "generate_recipe_structure",
            {
                "name": "Party Food",
                "ingredients": "1 egg",
                "steps": "Cook",
                "servings": 25,
            },
        )
    text = _get_text(result)
    assert "Validation failed" in text


async def test_generate_recipe_empty_name_returns_error():
    async with Client(mcp) as client:
        result = await client.call_tool(
            "generate_recipe_structure",
            {
                "name": "",
                "ingredients": "1 egg",
                "steps": "Cook",
            },
        )
    text = _get_text(result)
    assert "Validation failed" in text


# ---------------------------------------------------------------------------
# upload_custom_recipe
# ---------------------------------------------------------------------------


async def test_upload_recipe_not_connected_returns_message():
    server._cookidoo_service = None
    server._cookidoo_api = None

    async with Client(mcp) as client:
        result = await client.call_tool(
            "upload_custom_recipe",
            {"recipe_json": '{"name": "Test", "ingredients": ["egg"], "steps": ["cook"]}'},
        )
    text = _get_text(result)
    assert "Not connected" in text


async def test_upload_recipe_invalid_json_returns_message():
    server._cookidoo_service = MagicMock()
    server._cookidoo_api = MagicMock()
    try:
        async with Client(mcp) as client:
            result = await client.call_tool(
                "upload_custom_recipe",
                {"recipe_json": "not valid json at all"},
            )
        text = _get_text(result)
        assert "Invalid JSON" in text
    finally:
        server._cookidoo_service = None
        server._cookidoo_api = None


async def test_upload_recipe_success_returns_id_and_url():
    mock_created = MagicMock()
    mock_created.name = "Cookies"
    mock_created.id = "abc123"
    mock_created.url = "https://cookidoo.es/recipes/abc123"

    mock_service = MagicMock()
    mock_service.create_custom_recipe = AsyncMock(return_value=mock_created)

    server._cookidoo_service = mock_service
    server._cookidoo_api = MagicMock()
    try:
        recipe_json = json.dumps(
            {
                "name": "Cookies",
                "ingredients": ["200g flour", "100g butter"],
                "steps": ["Mix", "Bake"],
            }
        )
        async with Client(mcp) as client:
            result = await client.call_tool(
                "upload_custom_recipe",
                {"recipe_json": recipe_json},
            )
        text = _get_text(result)
        assert "abc123" in text
        assert "Cookies" in text
        assert "https://cookidoo.es/recipes/abc123" in text
    finally:
        server._cookidoo_service = None
        server._cookidoo_api = None


async def test_upload_recipe_invalid_recipe_data_returns_message():
    server._cookidoo_service = MagicMock()
    server._cookidoo_api = MagicMock()
    try:
        # Valid JSON but missing required fields
        async with Client(mcp) as client:
            result = await client.call_tool(
                "upload_custom_recipe",
                {"recipe_json": '{"name": "test"}'},
            )
        text = _get_text(result)
        assert "Invalid recipe data" in text
    finally:
        server._cookidoo_service = None
        server._cookidoo_api = None


# ---------------------------------------------------------------------------
# connect_to_cookidoo
# ---------------------------------------------------------------------------


@patch("cookidoo_service.load_dotenv")
async def test_connect_missing_credentials_returns_error(mock_dotenv, monkeypatch):
    monkeypatch.delenv("COOKIDOO_EMAIL", raising=False)
    monkeypatch.delenv("COOKIDOO_PASSWORD", raising=False)

    async with Client(mcp) as client:
        result = await client.call_tool("connect_to_cookidoo", {})
    text = _get_text(result)
    assert "Configuration Error" in text


@patch("cookidoo_service.load_dotenv")
@patch("server.CookidooService")
async def test_connect_success_returns_message(MockService, mock_dotenv, monkeypatch):
    monkeypatch.setenv("COOKIDOO_EMAIL", "user@test.com")
    monkeypatch.setenv("COOKIDOO_PASSWORD", "pass")
    monkeypatch.setenv("COOKIDOO_COUNTRY", "es")
    monkeypatch.setenv("COOKIDOO_LANGUAGE", "es-ES")
    monkeypatch.setenv("COOKIDOO_DEVICE", "TM6")

    mock_instance = AsyncMock()
    mock_instance.login = AsyncMock(return_value=MagicMock())
    MockService.return_value = mock_instance

    try:
        async with Client(mcp) as client:
            result = await client.call_tool("connect_to_cookidoo", {})
        text = _get_text(result)
        assert "Successfully connected" in text
        assert "user@test.com" in text
    finally:
        server._cookidoo_service = None
        server._cookidoo_api = None
