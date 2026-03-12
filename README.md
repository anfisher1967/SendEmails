# SendEmails (SMTP Branch)

This project deploys a PowerShell script that sends random test emails via SMTP (smtp.office365.com). Emails flow through the Exchange Online Protection (EOP) transport pipeline, enabling full threat detection (GTUBE, Safe Links, Safe Attachments).

There are two steps to get it to work correctly. First, ensure SMTP AUTH is enabled on the sending mailbox. Then deploy the ARM templates below.

### Prerequisites

#### 1. Enable SMTP AUTH on the Sending Mailbox

SMTP client authentication is disabled by default in Exchange Online. You must enable it on the mailbox that will send emails:

```powershell
Connect-ExchangeOnline
Set-CASMailbox -Identity sender@yourdomain.com -SmtpClientAuthenticationDisabled $false
```

To verify it's enabled:

```powershell
Get-CASMailbox -Identity sender@yourdomain.com | Select-Object SmtpClientAuthenticationDisabled
```

The value should be `False`. If it's blank, the mailbox inherits the org-wide default — check that with:

```powershell
Get-TransportConfig | Select-Object SmtpClientAuthenticationDisabled
```

#### 2. Note the Mailbox Credentials

You will need the sender email address and password for the ARM template deployment.

## Deploy Random Email Script

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fanfisher1967%2FSendEmails%2FSendEmailsSMTP%2Farm-templates%2Fsend-random-emails-deploy.json)

## Deploy Daily Email Schedule

This creates an automation account and schedules the emails to be sent daily at 8 am. You can change this as needed.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fanfisher1967%2FSendEmails%2FSendEmailsSMTP%2Farm-templates%2Fsend-random-emails-schedule.json)

Deploys an Azure Automation Account with a PowerShell runbook and daily schedule to automatically restart the send-random-emails container group.

### Prerequisites for Daily Schedule
1. The **Random Email Script** container must already be deployed
2. You need the **container group name** from that deployment (e.g. `send-emails-3bre5ttjmnleo`)
