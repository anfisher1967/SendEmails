# Restart-SendEmailsContainer.ps1
# Azure Automation Runbook - Restarts the send-random-emails ACI container group.
# Uses the Automation Account's system-assigned managed identity for authentication.

param(
    [Parameter(Mandatory = $true)]
    [string]$ResourceGroupName,

    [Parameter(Mandatory = $true)]
    [string]$ContainerGroupName,

    [Parameter(Mandatory = $true)]
    [string]$SubscriptionId
)

try {
    Write-Output "$(Get-Date) Connecting with managed identity..."
    Connect-AzAccount -Identity | Out-Null
    Set-AzContext -SubscriptionId $SubscriptionId | Out-Null

    Write-Output "$(Get-Date) Getting container group: $ContainerGroupName in $ResourceGroupName"
    $cg = Get-AzContainerGroup -ResourceGroupName $ResourceGroupName -Name $ContainerGroupName
    Write-Output "$(Get-Date) Current provisioning state: $($cg.ProvisioningState)"

    Write-Output "$(Get-Date) Sending restart command..."
    Invoke-AzResourceAction `
        -ResourceGroupName $ResourceGroupName `
        -ResourceType "Microsoft.ContainerInstance/containerGroups" `
        -ResourceName $ContainerGroupName `
        -Action "restart" `
        -ApiVersion "2023-05-01" `
        -Force

    Write-Output "$(Get-Date) Restart command sent successfully."
}
catch {
    Write-Error "Failed to restart container group: $_"
    throw
}
