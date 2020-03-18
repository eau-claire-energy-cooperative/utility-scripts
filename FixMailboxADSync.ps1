#This will fix hybrid exchange configurations where a mailbox was made in Office365 but hasn't synced with the hybrid exchange instance. This adds the necessary AD attributes for the user. 

$uid = read-host "Please enter User's username"
 
$mailnick = read-host "Please enter User's mail nickname"
 
$tmail = $uid+"@ecec.mail.onmicrosoft.com"
 
$pmail = $mailnick+"@ecec.com"
 
Set-ADUser $uid -Clear homemdb, homemta, msExchHomeServerName, msExchPoliciesExcluded
 
Set-ADUser $uid -Add @{msExchRemoteRecipientType="4"}
 
Set-ADUser $uid -Add @{mailNickname="$mailnick"}
 
Set-ADUser $uid -Add @{msExchProvisioningFlags="0"}
 
Set-ADUser $uid -Add @{msExchModerationFlags="6"}
 
Set-ADUser $uid -Add @{msExchAddressBookFlags="1"}
 
Set-ADUser $uid -Replace @{targetaddress="$tmail"}
 
Set-ADUser $uid -Replace @{msExchRecipientDisplayType="-2147483642"}
 
Set-ADUser $uid -Replace @{msExchRecipientTypeDetails="2147483648"}
 
Set-RemoteMailbox $uid -PrimarySMTPAddress $pmail