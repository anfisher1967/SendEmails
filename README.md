# SendEmails

## Deploy Random Email Script

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fanfisher1967%2FSendEmails%2Fmain%2Farm-templates%2Fsend-random-emails-deploy.json)

Deploys a PowerShell deployment script that sends random test emails (with optional GTUBE spam test strings) via Microsoft Graph API. Requires a User-Assigned Managed Identity with `Mail.Send` application permission.

### Prerequisites for Random Email Script

Using the Azure CLI, follow these instructions to create and configure the managed identity:

#### 1. Create a Managed Identity

```bash
az identity create --name "SendRandomEmails-MI" --resource-group <yourresourcegroup>
```

#### 2. Get the Identity's Resource ID (keep this for later)

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

## Deploy Daily Email Schedule

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fanfisher1967%2FSendEmails%2Fmain%2Farm-templates%2Fsend-random-emails-schedule.json)

Deploys an Azure Automation Account with a PowerShell runbook and daily schedule to automatically restart the send-random-emails container group.

### Prerequisites for Daily Schedule
1. The **Random Email Script** container must already be deployed
2. You need the **container group name** from that deployment (e.g. `send-emails-3bre5ttjmnleo`)
