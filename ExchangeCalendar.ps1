<#
.SYNOPSIS
    Exchange Calendar Helper script
.DESCRIPTION
    Automates some Exchang calendar permission functions. Assumes you are connected to an Exchange shell via Connect-EXOPSSession -UserPrincipalName "identity" already
.PARAMETER Action
    A valid action, either Check, All, Add, or Remove. Check is for permissions on the current calendar, All is calendars the user has permission for
.PARAMETER User
    The user to check for, or add/remove Author permission to
.PARAMETER Calendars
    List of user names to add/remove permissions from
.Parameter AccessRights
	Optional when adding permissions to a calendar, the access rights level for the user. Defaults to LimitedDetails
.EXAMPLE
    C:\PS>ExchangeCalendar.ps1 Add user1 -Calendars user2,user3
	
	Adds User1 as an Author to Calendars for Users 2 and 3
.NOTES
    Author: Rob Weber   
#>

param(
[Parameter(Mandatory=$true,Position=0)][ValidateNotNullOrEmpty()][string]$Action, 
[Parameter(Mandatory=$true,Position=1)][ValidateNotNullOrEmpty()][string]$User,
[Parameter(Mandatory=$false,Position=2)][string[]]$Calendars,
[Parameter(Mandatory=$false,Position=3)][ValidateSet("Author","Contributor","Owner","NonEditingAuthor","AvailabilityOnly","Reviewer","Editor","None","LimitedDetails")][string]$AccessRights = "LimitedDetails"
)

#Tab character for output
$Tab = [char]9

function log{
	param([string]$Message)
	
	Write-Host $Message
}

if($Action -eq "Check"){
	log -Message "Checking permission on calendar for $User"
	Get-MailboxFolderPermission -Identity ($User + ":\Calendar")
}
elseif($Action -eq "All"){
	log -Message "Checking permissions on all Calendars for $User"
	
	$perms = Get-Mailbox | % { Get-MailboxFolderPermission (($_.PrimarySmtpAddress.ToString())+":\Calendar") -User $User -ErrorAction SilentlyContinue} | select Identity,AccessRights
	
	foreach($p in $perms){
		$lastSlash = $p.Identity.LastIndexOf("/") + 1
		$cUser = $p.Identity.Substring($lastSlash,($p.Identity.length - $lastSlash))
		
		log -Message "$cUser"
		foreach($a in $p.AccessRights){
			log -Message "$Tab $a"
		}
	}
}
elseif ($Action -eq "Add"){
	log -Message "Adding $User with $AccessRights permissions on Calendars"
	
	foreach($c in $Calendars)
	{
		log -Message "Adding as $AccessRights to $c"
		Add-MailboxFolderPermission -Identity ($c + ":\Calendar") -User $User -AccessRights $AccessRights
	}
}
elseif ($Action -eq "Remove"){
	log -Message "Removing $User permissions from Calendars"
	
	foreach($c in $Calendars){
		log -Message "Removing from $c"
		Remove-MailboxFolderPermission -Identity ($c + ":\Calendar") -User $User -Confirm:$false
	}
}
else {
	log -Message "Valid actions are Check, All, Add, or Remove"
}