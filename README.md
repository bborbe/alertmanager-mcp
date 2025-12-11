# Alertmanager MCP Server

MCP Server for Prometheus Alertmanager. Allows querying alerts and managing silences via Claude Code.

## Setup

1.  **Install dependencies:**
    ```bash
    uv venv
    uv sync --all-extras
    ```

2.  **Configure environment:**
    Set the following environment variables:
    ```
    ALERTMANAGER_URL=https://alertmanager.example.com
    ALERTMANAGER_USERNAME=your_username  # Optional - for HTTP basic auth
    ALERTMANAGER_PASSWORD=your_password  # Optional - for HTTP basic auth
    ALERTMANAGER_TIMEOUT=30              # Optional - request timeout in seconds (default: 30)
    ALERTMANAGER_CREATED_BY=alertmanager-mcp  # Optional - identity for silence creation
    ```

    **Note:** Authentication (username/password) is optional. If not provided, requests will be made without authentication.

## Usage

### Direct Execution

Run the server with environment variables:
```bash
ALERTMANAGER_URL=https://alertmanager.example.com \
ALERTMANAGER_USERNAME=monitoring \
ALERTMANAGER_PASSWORD=your_password \
uv run alertmanager-mcp
```

### With .env File

Create a `.env` file:
```
ALERTMANAGER_URL=https://alertmanager.example.com
ALERTMANAGER_USERNAME=monitoring
ALERTMANAGER_PASSWORD=your_password
```

Then run:
```bash
uv run alertmanager-mcp
```

## Claude Code Configuration

### Basic Configuration

Add to your Claude Code MCP settings (`~/.claude/mcp.json`):

```json
{
  "mcpServers": {
    "alertmanager": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "--directory", "/path/to/alertmanager-mcp", "alertmanager-mcp"],
      "env": {
        "ALERTMANAGER_URL": "https://alertmanager.example.com",
        "ALERTMANAGER_USERNAME": "monitoring",
        "ALERTMANAGER_PASSWORD": "your_password"
      }
    }
  }
}
```

**For Alertmanager instances without authentication:**

```json
{
  "mcpServers": {
    "alertmanager": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "--directory", "/path/to/alertmanager-mcp", "alertmanager-mcp"],
      "env": {
        "ALERTMANAGER_URL": "https://alertmanager.example.com"
      }
    }
  }
}
```

### Multiple Environments

For multiple Alertmanager instances (prod, staging, dev):

```json
{
  "mcpServers": {
    "alertmanager-prod": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "--directory", "/path/to/alertmanager-mcp", "alertmanager-mcp"],
      "env": {
        "ALERTMANAGER_URL": "https://alertmanager.prod.example.com",
        "ALERTMANAGER_USERNAME": "monitoring",
        "ALERTMANAGER_PASSWORD": "prod_password"
      }
    },
    "alertmanager-staging": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "--directory", "/path/to/alertmanager-mcp", "alertmanager-mcp"],
      "env": {
        "ALERTMANAGER_URL": "https://alertmanager.staging.example.com",
        "ALERTMANAGER_USERNAME": "monitoring",
        "ALERTMANAGER_PASSWORD": "staging_password"
      }
    }
  }
}
```

### Using GitHub Installation

Install directly from GitHub (once published):

```json
{
  "mcpServers": {
    "alertmanager": {
      "type": "stdio",
      "command": "uvx",
      "args": ["--from", "git+https://github.com/yourusername/alertmanager-mcp", "alertmanager-mcp"],
      "env": {
        "ALERTMANAGER_URL": "https://alertmanager.example.com",
        "ALERTMANAGER_USERNAME": "monitoring",
        "ALERTMANAGER_PASSWORD": "your_password"
      }
    }
  }
}
```

## MCP Tools

### `get_alerts`
Fetch alerts from Alertmanager.

**Parameters:**
- `active_only` (boolean, optional): Fetch only active alerts. Defaults to `true`.
- `filter` (string, optional): Alertmanager filter query string.

**Example:**
```json
{
  "name": "get_alerts",
  "arguments": {
    "active_only": true,
    "filter": "severity=\"critical\""
  }
}
```

### `silence_alert`
Create a silence for an alert.

**Parameters:**
- `fingerprint` (string): The fingerprint of the alert to silence.
- `duration` (string): Duration of the silence (e.g., "2h", "1d", "1w").
- `comment` (string): A comment explaining the reason for the silence.

**Example:**
```json
{
  "name": "silence_alert",
  "arguments": {
    "fingerprint": "abc123def456",
    "duration": "2h",
    "comment": "Maintenance window - upgrading service"
  }
}
```

### `list_silences`
List existing silences from Alertmanager.

**Example:**
```json
{
  "name": "list_silences",
  "arguments": {}
}
```

## Testing

Run unit tests:
```bash
uv run pytest
```

## License

This project is licensed under the BSD-2-Clause License - see the [LICENSE](LICENSE) file for details.
