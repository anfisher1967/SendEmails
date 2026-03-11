##############################################################################################
#This sample script is not supported under any Microsoft standard support program or service.
#Microsoft further disclaims all implied warranties including, without limitation, any implied
#warranties of merchantability or of fitness for a particular purpose. The entire risk arising
#out of the use or performance of the sample script and documentation remains with you. In no
#event shall Microsoft, its authors, or anyone else involved in the creation, production, or
#delivery of the scripts be liable for any damages whatsoever (including, without limitation,
#damages for loss of business profits, business interruption, loss of business information,
#or other pecuniary loss) arising out of the use of or inability to use the sample script or
#documentation, even if Microsoft has been advised of the possibility of such damages.
##############################################################################################

<#
    .SYNOPSIS
        Deploys resources necessary to run MDO Telemetry container in Azure

    .DESCRIPTION
        Connects to Exchange Online tenant to discover mailbox details and SMTP destination, and
        then deploys resources in Azure tenant required for the Azure Container Instance.
        Container will send synthetic Spam/Phish/Malware detections by MDO to improve native
        reporting, Threat Explorer, Advanced Hunting etc experiences. The latest version of this script can be found at https://aka.ms/mdotelemetry/deploy

    .EXAMPLE
        PS> .\DeployScript.ps1

    .LINK
        Wiki on installation and usage is available at https://aka.ms/mdotelemetry

    .NOTES
        Version: 0.2.2
        Date: 13 October 2025

        Jonathan Devere-Ellery - Cloud Solution Architect
#>

Function Get-IsAdministrator {
    $currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    Return $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (Get-IsAdministrator) {
    $InstallArguments = @{
        Scope = "AllUsers"
    }
}
else {
    $InstallArguments = @{
        Scope = "CurrentUser"
    }
}



Write-Host "Preparing to install Container into Azure tenant..."

$EXOModule = (Get-Module ExchangeOnlineManagement -ListAvailable | Sort-Object Version -Descending)
if ($null -eq $EXOModule) {
    Write-Host "$(Get-Date) ExchangeOnlineManagement module not installed. Preparing to install from the PowerShell Gallery"
    Install-Module ExchangeOnlineManagement -Force -AllowClobber @InstallArguments
} else {
    Write-Host "$(Get-Date) ExchangeOnlineManagement module installed. Preparing to update the module to latest version from the PowerShell Gallery"
    Update-Module ExchangeOnlineManagement
}

$AzModule = (Get-Module Az.Accounts -ListAvailable | Sort-Object Version -Descending)
if ($null -eq $AzModule) {
    Write-Host "$(Get-Date) Az module not installed. Preparing to install from the PowerShell Gallery"
    Install-Module Az -Force -AllowClobber @InstallArguments
} else {
    Write-Host "$(Get-Date) Az module installed. Preparing to update the module to latest version from the PowerShell Gallery"
    Update-Module Az
}


# Try looking up the Tenant ID to provide to the Connect-AzAccount command
Write-Host ""
$TenantDomain = Read-Host "Enter your '<tenantname>.onmicrosoft.com' domain name"
Try {
    $OIDCResult = Invoke-RestMethod "https://login.microsoftonline.com/$TenantDomain/.well-known/openid-configuration"
    $TenantId = (($OIDCResult).token_endpoint | Select-String -Pattern '([0-9A-Fa-f]{8}(?:-[0-9A-Fa-f]{4}){3}-[0-9A-Fa-f]{12})').Matches.Value
    $ConnArguments = @{
        Tenant = $TenantId
    }
} Catch {
    Write-Warning "Unable to retrieve the Tenant ID automatically"
}

Write-Host "$(Get-Date) Connecting to Azure"
if ($null -eq (Get-AzContext)) {
    Connect-AzAccount @ConnArguments # Splatting arguments so it will continue even if Tenant ID lookup had failed
}


# Connecting to Exchange Online tenant
Write-Host "$(Get-Date) Connecting to Exchange Online"
if ($null -eq (Get-ConnectionInformation)) {
    Connect-ExchangeOnline -ShowBanner:$false
}


# Check whether any Az Resource Providers are not registered
$CIRP = Get-AzResourceProvider -ListAvailable |  Where-Object -Property ProviderNamespace -Like -Value "Microsoft.ContainerInstance"
$NRP = Get-AzResourceProvider -ListAvailable |  Where-Object -Property ProviderNamespace -Like -Value "Microsoft.Network"

if  ($CIRP.RegistrationState -eq "NotRegistered") {
    Register-AzResourceProvider -ProviderNamespace "Microsoft.ContainerInstance"
}
if  ($NRP.RegistrationState -eq "NotRegistered") {
    Register-AzResourceProvider -ProviderNamespace "Microsoft.Network"
}


# Determine hostname of EOP to send messages to
$InitialDomain = (Get-AcceptedDomain | Where-Object {$_.InitialDomain -eq $true}).DomainName
$SmtpServer = ((Resolve-DnsName -Name $InitialDomain -Type MX -Server 1.1.1.1) | Where-Object {$_.NameExchange -match ".mail.protection.outlook.com"} | Select-Object -First 1).NameExchange


Write-Host ""
Write-Host "At the prompt select which Resource Group to deploy resources" -ForegroundColor Yellow
$RG = Get-AzResourceGroup | Select-Object ResourceGroupName,Location | Out-GridView -OutputMode Single

Write-Host ""
Write-Host "$(Get-Date) Selected Resource Group: $($RG.ResourceGroupName)"

Write-Host ""
Write-Host "Should telemetry be sent to " -NoNewline; Write-Host "all" -ForegroundColor Green -NoNewline;  Write-Host " mailboxes within the tenant automatically?"
Write-Host " 1) Yes, Send test Spam/Phish to all mailboxes " -NoNewline; Write-Host "(Recommended)" -ForegroundColor Green
Write-Host " 2) No, Manually configure each individual mailboxes to send Spam/Phish (Advanced)"
Write-Host ""
$selected = $null
do {
    $selected = Read-Host "Select preference (Type '1' or '2' and press Enter)"
}
until ($selected -eq 1 -or $selected -eq 2)

switch ($selected) {
    1 {$MailboxSelection = "Auto"}
    2 {$MailboxSelection = "Manual"}
}

# Collect email addresses of mailboxes which are in scope
$Emails = @()
if ($MailboxSelection -eq "Auto") {
    # All mailboxes
    $Emails = (Get-Mailbox | Where-Object {$_.RecipientTypeDetails -eq "UserMailbox"}).PrimarySmtpAddress -join ','
} elseif ($MailboxSelection -eq "Manual") {
    # Manually enter mailboxes
    Write-Host ""
    $SelectedMailboxes = @()
    do {
        $respMbx = Read-Host "Enter the PrimarySMTPAddress for each mailbox to target. Enter a blank line when finished"
        try {
            $mbx = Get-Mailbox -Identity $respMbx -ErrorAction Stop
            if ($null -ne $mbx) {
                $SelectedMailboxes += $mbx.PrimarySmtpAddress
            }
        } catch {}
    } until ($respMbx -eq "")
    $Emails = $SelectedMailboxes -join ','
}


# Determine whether to also deploy a NAT gateway to control egress traffic from container instance
# https://learn.microsoft.com/en-us/azure/container-instances/container-instances-nat-gateway
$selected = $null
do {
    Write-Host ""
    Write-Host ""
    Write-Host "Do you also want to deploy a NAT Gateway so that the egress/outbound IP address for the container instance can be modified?"
    Write-Host "Note: This will incur additional costs for resources."
    Write-Host ""
    Write-Host " 1) No, Skip creating a NAT gateway. Will use a randomly selected public IP for egress traffic " -NoNewline; Write-Host "(Simple - Recommended)" -ForegroundColor Green
    Write-Host " 2) Yes, Create a NAT gateway to allow for manual control of the public IP of egress traffic (Advanced)"
    Write-Host ""
    $selected = Read-Host "Select preference (Type '1' or '2' and press Enter)"
}
until ($selected -eq 1 -or $selected -eq 2)

switch ($selected) {
    1 {$NATOptin = "No"}
    2 {$NATOptin = "Yes"}
}
if ($NATOptin -eq "Yes") {
    Write-Host ""
    Write-Host "$(Get-Date) Starting deployment of NAT Gateway resources in $($RG.ResourceGroupName)"

    Write-Host "$(Get-Date) Deploying Public IP"
    $Pip = New-AzPublicIpAddress -ResourceGroupName $RG.ResourceGroupName -Location $RG.Location -AllocationMethod "Static" -Sku "Standard" -Name "nat-pip" -IpAddressVersion "IPv4"

    Write-Host "$(Get-Date) Deploying NAT Gateway"
    $NatGateway = New-AzNatGateway -ResourceGroupName $RG.ResourceGroupName -Location $RG.Location -Name "natgateway" -Sku "Standard" -PublicIpAddress $Pip 

    Write-Host "$(Get-Date) Deploying Network Security Group"
    $rule = New-AzNetworkSecurityRuleConfig -Name allow-smtp -Description "Allow SMTP" -Access Allow -Protocol Tcp -Direction Outbound -Priority 100 -SourceAddressPrefix * -SourcePortRange * -DestinationAddressPrefix * -DestinationPortRange 25
    $NSG = New-AzNetworkSecurityGroup -Name "mdotelemetry-nsg" -ResourceGroupName $RG.ResourceGroupName -Location $RG.Location -SecurityRules $rule

    Start-Sleep -Seconds 5 # Avoid race conditions with deploying resources

    Write-Host "$(Get-Date) Deploying VNet"
    $delegation = New-AzDelegation -Name "Microsoft.ContainerInstance/containerGroups" -ServiceName "Microsoft.ContainerInstance/containerGroups"
    $Subnet = New-AzVirtualNetworkSubnetConfig -Name "mdotelemetry-subnet" -AddressPrefix 10.183.10.0/24 -NatGatewayId $NatGateway.Id -Delegation $delegation -NetworkSecurityGroupId $NSG.Id
    $Vnet = New-AzVirtualNetwork -Name "mdotelemetry-vnet" -ResourceGroupName $RG.ResourceGroupName -Location $RG.Location -AddressPrefix 10.183.10.0/24 -DnsServer 1.1.1.1,1.0.0.1 -Subnet $Subnet

    Start-Sleep -Seconds 5 # Avoid race conditions with deploying resources

    # Splat the arguments when creating the container group
    $CGArguments = @{
        'SubnetId' = @{
            'Id' = $Vnet.Subnets.Id
            'Name' = $Vnet.Subnets.Name
        }
        'IpAddressType' = 'Private'
    }

    Start-Sleep -Seconds 5 # Avoid race conditions with deploying resources

} else {
    # Configure the container to use random public IP address
    $CGArguments = @{
        'IpAddressType' = 'Public'
    }
}


Write-Host ""
Write-Host "$(Get-Date) Starting deployment of Azure Container Instance in $($RG.ResourceGroupName)"

# Pass the values to the container as environment variables
$env1 = New-AzContainerInstanceEnvironmentVariableObject -Name "EMAILS" -Value $Emails
$env2 = New-AzContainerInstanceEnvironmentVariableObject -Name "SMTPHOST" -Value $SmtpServer

$port = New-AzContainerInstancePortObject -Port 80 -Protocol TCP

$Container = New-AzContainerInstanceObject -Name "mdotelemetry" -Image "ghcr.io/jonade/mdotelemetry:latest" -Port @($port) -RequestCpu 0.2 -RequestMemoryInGb 0.2 -EnvironmentVariable @($env1, $env2)


$ContainerGroup = New-AzContainerGroup -Name "mdotelemetry" -ResourceGroupName $RG.ResourceGroupName -Location $RG.Location -Container $Container -OsType Linux -IPAddressPort @($port) @CGArguments


Write-Host ""
if ($ContainerGroup.ProvisioningState -eq "Succeeded") {
    Write-Host "$(Get-Date) Deployment Succeeded"
} else {
    Write-Host "$(Get-Date) Deployment Failed"
}
Write-Host ""