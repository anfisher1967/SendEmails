# Quick Start Guide

## After Initial Setup

### 1. Activate Virtual Environment
```powershell
cd c:\MCP server
.\.venv\Scripts\Activate.ps1
```

### 2. Configure Azure Credentials
```powershell
cp .env.example .env
# Edit .env with your:
#  - AZURE_TENANT_ID
#  - AZURE_SUBSCRIPTION_ID  
#  - SENTINEL_WORKSPACE_ID
#  - AZURE_CLIENT_ID/SECRET
```

### 3. Authenticate to Azure
```powershell
az login
```

### 4. Run Verification Tests
```powershell
pytest tests/test_api_connectivity.py -v
```

Expected: ✅ Sentinel connection successful, ✅ Graph connection successful

### 5. Test Agents
```powershell
# AnalystBot01 alert triage test
python agents/analyst_bot_01/test_triage.py

# HUNTER threat hunt test
python agents/hunter/test_queries.py
```

### 6. Verify MCP Integration
In Claude Chat:
```
"List the sign-in related tables in my Sentinel data lake"
```
Expected: MCP tool call with Sentinel table results

---

## Development Workflow

### Adding New Code
1. Create files in appropriate directory
2. Follow existing patterns (base classes, models, clients)
3. Add tests in `tests/` folder
4. Run: `pytest -v` to validate

### Writing KQL Queries
1. Create `.kql` files in `queries/hunting/` or `queries/enrichment/`
2. Use KQL Assistant extension for syntax validation
3. Test with REST Client extension or directly in Sentinel

### Testing
```powershell
# Run all tests
pytest tests/ -v --cov

# Run specific test file
pytest tests/test_api_connectivity.py -v

# Run with output
pytest -v -s
```

### Code Quality
```powershell
# Format code
black agents/ shared/

# Lint code
flake8 agents/ shared/

# Type checking
mypy agents/ shared/
```

---

## Common Tasks

### Query Sentinel Directly
```python
from shared.api_clients.sentinel_client import SentinelClient

client = SentinelClient()
results = await client.get_alerts(hours=24, severity="High")
```

### Get User Enrichment
```python
from shared.api_clients.graph_client import GraphClient

client = GraphClient()
risky_users = await client.get_risky_users()
```

### Generate Hunt Query
```python
from agents.hunter.query_generator import KQLQueryGenerator

generator = KQLQueryGenerator()
query = await generator.generate_query(
    threat_type="ransomware",
    mitre_techniques=["Data Encrypted for Impact"]
)
```

### Run Agent
```python
from agents.analyst_bot_01.agent import AnalystBot01Agent

agent = AnalystBot01Agent(mode="advisory")
result = await agent.execute({"alert": alert_dict})
```

---

## File Locations

- **Agents**: `agents/analyst_bot_01/`, `agents/hunter/`
- **Models**: `shared/models/`
- **API Clients**: `shared/api_clients/`
- **KQL Queries**: `queries/hunting/`, `queries/enrichment/`
- **Tests**: `tests/`
- **Config**: `.env`, `.vscode/settings.json`, `.vscode/mcp.json`

---

## Debugging

### Enable Debug Logging
```python
from shared.utils.logging_config import setup_logging

setup_logging(level="DEBUG")
```

### Check Environment Variables
```powershell
# View loaded .env variables
Get-Content .env
```

### Test API Connectivity
```powershell
# Run connectivity tests with verbose output
pytest tests/test_api_connectivity.py -v -s
```

### View Python Path
```powershell
$env:PYTHONPATH
```

---

## Useful Commands

```powershell
# Activate venv
.\.venv\Scripts\Activate.ps1

# Deactivate venv
deactivate

# List installed packages
pip list

# Upgrade pip
python -m pip install --upgrade pip

# Install specific package
pip install <package_name>

# Run Python file
python script.py

# Format code
black .

# Run tests with coverage
pytest -v --cov=agents --cov=shared
```

---

## Documentation

- [SETUP_COMPLETE.md](SETUP_COMPLETE.md) - Setup summary
- [IDE-setup.md](IDE-setup.md) - Full setup guide
- [agents/analyst_bot_01/prompts/system.md](agents/analyst_bot_01/prompts/system.md) - AnalystBot01 system prompt
- [agents/hunter/prompts/system.md](agents/hunter/prompts/system.md) - HUNTER system prompt

---

**Last Updated**: February 18, 2026
