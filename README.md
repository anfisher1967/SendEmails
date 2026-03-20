# SendEmails

This project deploys Azure Container Instances that send synthetic Spam/Phish/Malware emails to populate your MCAPS tenant with MDO detections for Threat Explorer, Advanced Hunting, and reporting.

Two approaches are available:

| Template | Method | Auth Required? |
|----------|--------|----------------|
| **Send-Emails.json** (SMTP relay) | Direct SMTP to EOP MX endpoint | None |
| send-random-emails-deploy.json (Graph API) | Microsoft Graph `Mail.Send` | Managed Identity |

---

## Option 1: SMTP Relay (Recommended)

No managed identity or Graph permissions needed. Emails are sent directly to your tenant's EOP MX endpoint via SMTP.

### Prerequisites

1. Fill in [Send-Emails.parameters.json](arm-templates/Send-Emails.parameters.json):
   - `tenantDomain` — your tenant's email domain (e.g. `contoso.com`)
   - `toAddresses` — comma-separated recipient mailboxes

### Deploy SMTP Email Sender

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fanfisher1967%2FSendEmails%2FSendEmails2%2Farm-templates%2FSend-Emails.json)

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `tenantDomain` | `contoso.com` | Your tenant's email domain — SMTP endpoint is derived automatically |
| `smtpPort` | `587` | SMTP port (587 for STARTTLS, 25 for direct) |
| `toAddresses` | *(required)* | Comma-separated recipient mailboxes |
| `emailsPerRecipient` | `20` | Emails each recipient receives |
| `threatTestPercentage` | `30` | % of emails with GTUBE/Phish URL/EICAR payload |

---

## Option 2: Graph API (Alternative)

Sends via Microsoft Graph API using a User-Assigned Managed Identity with `Mail.Send` permission.

### Prerequisites for Graph API

Using the Azure CLI, follow these instructions to create and configure the managed identity:

#### 1. Create a Managed Identity

```bash
az identity create --name "SendRandomEmails-MI" --resource-group <yourresourcegroup>
```

#### 2. Get the Identity's Resource ID (Save this value for later. You will need it for the first ARM template)

```bash
az identity show --name "SendRandomEmails-MI" --resource-group <yourresourcegroup> --query id -o tsv
```

#### 3. Get the Identity's Principal ID

```powershell
$principalId = az identity show --name "SendRandomEmails-MI" --resource-group <yourresourcegroup> --query principalId -o tsv
```

#### 4. Grant Mail.Send Application Permission via Microsoft Graph

> **Note:** Requires Global Admin or Privileged Role Admin.

```powershell
Connect-MgGraph -Scopes "AppRoleAssignment.ReadWrite.All"
$graphSp = Get-MgServicePrincipal -Filter "appId eq '00000003-0000-0000-c000-000000000000'"
$mailSendRole = $graphSp.AppRoles | Where-Object { $_.Value -eq "Mail.Send" }
New-MgServicePrincipalAppRoleAssignment `
    -ServicePrincipalId (Get-MgServicePrincipal -Filter "displayName eq 'SendRandomEmails-MI'").Id `
    -PrincipalId (Get-MgServicePrincipal -Filter "displayName eq 'SendRandomEmails-MI'").Id `
    -AppRoleId $mailSendRole.Id `
    -ResourceId $graphSp.Id
```
## Deploy Random Email Script

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fanfisher1967%2FSendEmails%2Fmain%2Farm-templates%2Fsend-random-emails-deploy.json)

## Deploy Daily Email Schedule

This creates an automation account and schedules the emails to be sent daily at 8 am. You can change this as needed.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fanfisher1967%2FSendEmails%2Fmain%2Farm-templates%2Fsend-random-emails-schedule.json)

Deploys an Azure Automation Account with a PowerShell runbook and daily schedule to automatically restart the send-random-emails container group.

### Prerequisites for Daily Schedule
1. The **Random Email Script** container must already be deployed
2. You need the **container group name** from that deployment (e.g. `send-emails-3bre5ttjmnleo`)
