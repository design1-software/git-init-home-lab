<#
.SYNOPSIS
    Onboard an ARIA lab student into Active Directory in one call.

.DESCRIPTION
    Creates an AD user in the ARIA Students OU, adds the user to ARIA-Students,
    forces a password change at first logon, and prints verification output.

    Run this on JLM-DC01 as Administrator.
    Requires the ActiveDirectory PowerShell module.

.EXAMPLE
    . .\New-AriaStudent.ps1
    New-AriaStudent -FirstName Dominique -LastName Davis -SamAccountName student02

.EXAMPLE
    New-AriaStudent -FirstName Sha -LastName Prather -SamAccountName student01

.EXAMPLE
    Import-Csv .\students.csv | ForEach-Object {
        New-AriaStudent -FirstName $_.FirstName -LastName $_.LastName `
                        -SamAccountName $_.SamAccountName -Degree $_.Degree -GeneratePassword
    }

.NOTES
    Keep contact PII such as phone numbers and personal email addresses out of students.csv
    and out of the repository.

    The provisioning CSV only needs:
    FirstName, LastName, SamAccountName, Degree
#>

function New-AriaStudent {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$FirstName,
        [Parameter(Mandatory)][string]$LastName,
        [Parameter(Mandatory)][string]$SamAccountName,
        [string]$Degree    = 'BS in Cybersecurity and Assurance, WGU',
        [string]$Group     = 'ARIA-Students',
        [string]$OU        = 'OU=Students,OU=ARIA-Lab,DC=jlm,DC=lab',
        [string]$UpnSuffix = 'jlm.lab',
        [securestring]$Password,
        [switch]$GeneratePassword
    )

    Import-Module ActiveDirectory -ErrorAction Stop

    $existingUser = Get-ADUser -Filter "SamAccountName -eq '$SamAccountName'" -ErrorAction SilentlyContinue
    if ($existingUser) {
        Write-Warning "$SamAccountName already exists. Aborting."
        Get-ADUser $SamAccountName -Properties DisplayName,UserPrincipalName,Enabled,Description |
            Select-Object SamAccountName,DisplayName,UserPrincipalName,Enabled,Description
        Get-ADPrincipalGroupMembership $SamAccountName | Select-Object Name
        return
    }

    if ($GeneratePassword) {
        $plain = -join ((48..57) + (65..90) + (97..122) + (33,35,36,37,38,42) |
            Get-Random -Count 16 |
            ForEach-Object { [char]$_ })

        $Password = ConvertTo-SecureString $plain -AsPlainText -Force
        Write-Host "Temp password for ${SamAccountName}: $plain" -ForegroundColor Yellow
    }
    elseif (-not $Password) {
        $Password = Read-Host "Temp password for $FirstName $LastName" -AsSecureString
    }

    $display = "$FirstName $LastName"
    $params = @{
        Name                  = $display
        GivenName             = $FirstName
        Surname               = $LastName
        DisplayName           = $display
        SamAccountName        = $SamAccountName
        UserPrincipalName     = "$SamAccountName@$UpnSuffix"
        Path                  = $OU
        AccountPassword       = $Password
        Enabled               = $true
        ChangePasswordAtLogon = $true
        Description           = "ARIA $SamAccountName - Degree pending: $Degree"
    }

    New-ADUser @params
    Add-ADGroupMember -Identity $Group -Members $SamAccountName

    Write-Host "Created ARIA student account: $display ($SamAccountName)" -ForegroundColor Green

    Get-ADUser $SamAccountName -Properties DisplayName,UserPrincipalName,Enabled,Description |
        Select-Object SamAccountName,DisplayName,UserPrincipalName,Enabled,Description

    Get-ADPrincipalGroupMembership $SamAccountName | Select-Object Name
}
