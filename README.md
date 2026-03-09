# MCP Server

## Deploy MDO Telemetry Container

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fanfisher1967%2FMCP-server%2Fmain%2Farm-templates%2Fmdotelemetry-deploy.json)

Deploys an Azure Container Instance running the MDO Telemetry container image for generating synthetic Spam/Phish/Malware detections in Microsoft Defender for Office 365.

## Deploy Random Email Script

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fanfisher1967%2FMCP-server%2Fmain%2Farm-templates%2Fsend-random-emails-deploy.json)

Deploys a PowerShell deployment script that sends random test emails (with optional GTUBE spam test strings) via Microsoft Graph API. Requires a User-Assigned Managed Identity with `Mail.Send` application permission.

### Prerequisites for Random Email Script
1. A **User-Assigned Managed Identity** with `Mail.Send` Graph API application permission
2. The managed identity resource ID (paste into the deployment parameters)
