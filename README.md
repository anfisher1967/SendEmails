# SendEmails

## Deploy Random Email Script

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fanfisher1967%2FSendEmails%2Fmain%2Farm-templates%2Fsend-random-emails-deploy.json)

Deploys a PowerShell deployment script that sends random test emails (with optional GTUBE spam test strings) via Microsoft Graph API. Requires a User-Assigned Managed Identity with `Mail.Send` application permission.

### Prerequisites for Random Email Script
1. A **User-Assigned Managed Identity** with `Mail.Send` Graph API application permission
2. The managed identity resource ID (paste into the deployment parameters)

## Deploy Daily Email Schedule

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fanfisher1967%2FSendEmails%2Fmain%2Farm-templates%2Fsend-random-emails-schedule.json)

Deploys an Azure Automation Account with a PowerShell runbook and daily schedule to automatically restart the send-random-emails container group.

### Prerequisites for Daily Schedule
1. The **Random Email Script** container must already be deployed
2. You need the **container group name** from that deployment (e.g. `send-emails-3bre5ttjmnleo`)
