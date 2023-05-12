<#
.SYNOPSIS
    Check File Size
.DESCRIPTION
    Windows Script to check the size of a file. Returns Warning or Critical if above a certain size. 
    By default the file size units are KB, can be changed with Unit parameter.
.EXAMPLE
    C:\PS>check_file_size_windows.ps1 "C:\file.txt" 100 200 - checks file and displays warning if over 100 KB and critical if over 200 KB
    C:\PS>check_file_size_windows.ps1 "C:\file.txt" 100 200 MB - checks file and displays warning if over 100 MB and critical if over 200 MB
.NOTES
    Author: Rob Weber   
#>
param(
[Parameter(Mandatory=$true,Position=0)][ValidateNotNullOrEmpty()][string]$FilePath,
[Parameter(Mandatory=$true,Position=1)][ValidateNotNullOrEmpty()][int]$WarningThreshold, 
[Parameter(Mandatory=$true,Position=2)][ValidateNotNullOrEmpty()][int]$CriticalThreshold,
[Parameter(Mandatory=$False,Position=3)][Validateset("KB","MB","GB","TB")][string]$Unit = "KB"
)

$STATUS_OK = 0
$STATUS_WARNING = 1
$STATUS_CRITICAL = 2
$STATUS_UNKNOWN = 3

# get the right units
switch ($Unit) {                     
    "KB" {$UnitSize = 1KB}            
    "MB" {$UnitSize = 1MB}            
    "GB" {$UnitSize = 1GB}            
    "TB" {$UnitSize = 1TB}
}

try{
    $File = Get-Item "$FilePath" -ErrorAction Stop

} catch {
    Write-Host "$FilePath does not exist"
    exit $STATUS_UNKNOWN
}

# file exists - check size
$size = $File.Length/$UnitSize
Write-Host "$($File.FullName) is $($size)$($Unit)"

if($size -gt $CriticalThreshold)
{
    exit $STATUS_CRITICAL
}
elseif($size -gt $WarningThreshold)
{
    exit $STATUS_WARNING
}
else
{
    exit $STATUS_OK
}