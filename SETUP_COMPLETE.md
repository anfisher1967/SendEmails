# Agentic SOC Development Environment - Setup Complete ✅

**Date**: February 18, 2026  
**Status**: Initial Setup Complete | Ready for Credential Configuration

---

## What Was Set Up

✅ **Environment**
- Python 3.13 installed via winget
- Virtual environment created at `.venv/`
- 164 packages installed (Azure SDK, agents framework, testing tools)
- Windows Long Paths enabled for nested dependencies

✅ **Configuration**
- `.env.example` - Template with all required variables
- `.gitignore` - Excludes secrets, cache, venv
- `.vscode/settings.json` - Python path, formatter, language associations
- `.vscode/mcp.json` - MCP servers (Azure + Enterprise)
- `requirements.txt` - All Python dependencies with pre-release flags
- `pyproject.toml` - Project metadata and build config

✅ **Project Structure**
```
agentic-soc/
├── agents/
│   ├── base_agent.py                    # Base class for all agents
│   ├── analyst_bot_01/                  # Alert Triage Agent
│   │   ├── agent.py, triage.py, enrichment.py
│   │   ├── prompts/ (system.md)
│   │   └── tests/
│   └── hunter/                          # Threat Hunting Agent
│       ├── agent.py, query_generator.py, threat_mappings.py
│       ├── prompts/ (system.md)
│       └── tests/
├── shared/
│   ├── api_clients/                     # Sentinel, Graph, Defender wrappers
│   ├── models/                          # Pydantic models (Alert, Entity, HuntResult)
│   └── utils/                           # KQL validator, logging config
├── queries/
│   ├── hunting/                         # Ransomware, Credential Theft, Lateral Movement
│   └── enrichment/                      # User & Device Context
├── tests/                               # API connectivity + MCP verification
├── docs/                                # Documentation
├── .venv/                               # Python virtual environment
└── [config files]
```

✅ **Code Foundation **
- **Base Agent** - Abstract class for agent inheritance
- **Data Models** - Pydantic models for Alert, Entity (User/Device/IP), HuntResult
- **API Clients** - Wrappers for Sentinel, Graph, Defender
- **Utilities** - KQL validator, structured logging
- **Sample Queries** - 5 pre-built KQL hunts (ransomware, credential theft, lateral movement, enrichment)
- **Agent Logic** - AnalystBot01 triage engine, HUNTER query generator + MITRE mapper

✅ **VS Code Extensions** (11 installed)
- Prettier, PowerShell, Python, Pylance, ESLint, YAML
- KQL Assistant, REST Client, DotENV
- Azure MCP Server, Microsoft Sentinel

---

## Critical Next Steps

### Step 1: Azure Credentials (⚠️ REQUIRED)
You must populate `.env` with real Azure credentials:

```powershell
# In PowerShell or terminal:
cp .env.example .env

# Edit .env with your values:
AZURE_TENANT_ID=<from Azure Portal>
AZURE_SUBSCRIPTION_ID=<from Azure Portal>
SENTINEL_WORKSPACE_ID=<from Sentinel workspace>
SENTINEL_RESOURCE_GROUP=<RG containing workspace>
AZURE_CLIENT_ID=<app registration>
AZURE_CLIENT_SECRET=<app secret>
```

**How to find these:**
- **TENANT_ID**: Azure Portal → Azure AD → Properties
- **SUBSCRIPTION_ID**: Azure Portal → Subscriptions
- **SENTINEL_WORKSPACE_ID**: Sentinel workspace → Settings → Workspace Settings
- **CLIENT_ID/SECRET**: Azure Portal → App Registrations → Sentinel API App

### Step 2: Verify Environment
```powershell
cd c:\MCP server
.\.venv\Scripts\Activate.ps1
pytest tests/test_api_connectivity.py -v
```

Expected output:
```
✅ Sentinel connection successful
✅ Graph connection successful
```

### Step 3: Verify MCP Tools (in Claude Chat)
Ask Claude:
- "List the sign-in related tables in my Sentinel data lake"
- "Show schema for the DeviceProcessEvents table"

Expected: MCP tool calls + Sentinel/Graph data returned

### Step 4: Test Agents
```powershell
# AnalystBot01 test:
python agents/analyst_bot_01/test_triage.py

# HUNTER test:
python agents/hunter/test_queries.py
```

---

## Architecture Overview

### AnalystBot01 Agent - Alert Triage & Enrichment
**Input**: Sentinel security alert  
**Process**:
1. Triage alert (severity score 0.0-1.0)
2. Identify risk indicators (MITRE tactics/techniques)
3. Enrich with context (user history, device posture)
4. Recommend action: dismiss → escalate_immediately

**Output**: Triage result + enriched context + recommendation

### HUNTER Agent - Threat Hunting & Query Generation
**Input**: Threat type + MITRE tactics  
**Process**:
1. Map threat to MITRE ATT&CK framework
2. Generate KQL query for threat hunting
3. Execute query against Sentinel
4. Synthesize findings + anomalies

**Output**: Hunt results + anomalies + recommendations + follow-up hunts

### MCP Integration
- **Azure MCP**: Enables Claude to query Sentinel tables
- **Enterprise MCP**: Enables Claude to call Microsoft Graph APIs
- Both require `az login` authentication (handled in VS Code)

---

## Key Files

| File | Purpose |
|---|---|
| [.env.example](.env.example) | Environment template (copy to .env) |
| [requirements.txt](requirements.txt) | Python dependencies |
| [pyproject.toml](pyproject.toml) | Project metadata |
| [agents/base_agent.py](agents/base_agent.py) | Agent base class |
| [shared/models/alert.py](shared/models/alert.py) | Alert data model |
| [shared/api_clients/sentinel_client.py](shared/api_clients/sentinel_client.py) | Sentinel wrapper |
| [agents/analyst_bot_01/agent.py](agents/analyst_bot_01/agent.py) | AnalystBot01 logic |
| [agents/hunter/agent.py](agents/hunter/agent.py) | HUNTER logic |
| [.vscode/settings.json](.vscode/settings.json) | VS Code config |
| [.vscode/mcp.json](.vscode/mcp.json) | MCP server config |

---

## Troubleshooting

### "SENTINEL_WORKSPACE_ID not set"
→ Create `.env` file and populate from Azure Portal

### "Azure API calls fail"
→ Run `az login` to authenticate to Azure

### "Python path not found"
→ Reload VS Code after `.venv` creation

### "msgraph-sdk install failed"
→ Windows Long Paths must be enabled (admin registry setting)

### "MCP tools don't work"
→ Provision Enterprise MCP (one-time Entra admin task) OR ensure `az login` completes

---

## Validation Checklist

- [ ] `.env` file populated with real Azure credentials
- [ ] `az login` completes successfully
- [ ] `pytest tests/test_api_connectivity.py -v` passes ✅
- [ ] Claude Chat MCP tool calls work (Sentinel + Graph)
- [ ] AnalystBot01 test runs without errors
- [ ] HUNTER agent generates KQL queries
- [ ] All VS Code extensions loaded (no warnings)

---

## Documentation Structure

- [IDE-setup.md](IDE-setup.md) - Full original setup guide
- [agents/](agents/) - Agent implementations
- [shared/](shared/) - Shared code libraries
- [queries/](queries/) - KQL query library
- [tests/](tests/) - Test suites

---

## Next Phase: Agent Development

Once credentials are configured:

1. **Extend AnalystBot01**
   - Connect to Sentinel API for real alert fetching
   - Integrate Entra ID for user enrichment
   - Add threat intel lookups

2. **Extend HUNTER**
   - Execute generated KQL queries vs. Sentinel
   - Parse results into HuntResult models
   - Trigger AnalystBot01 on high-risk findings

3. **Build Collaboration**
   - AnalystBot01 → HUNTER workflow
   - Hunt results → Alert escalation feedback loop
   - Analyst review → Agent learning

---

## Support & Issues

For setup issues, reference [IDE-setup.md](IDE-setup.md) "Known Issues & Gotchas" section.

For agent-specific questions, see agent `prompts/system.md` files.

---

**Setup Date**: February 18, 2026  
**Status**: ✅ Ready for Credential Configuration  
**Next**: Populate `.env` with Azure credentials
