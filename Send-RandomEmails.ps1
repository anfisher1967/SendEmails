#Author:            Lee Jeffries
#Company:           LJC (https://www.leeejeffries.com) 
#Script help:       Designed to generate random email content to be passed to an SMTP server
#Purpose:           Fill up a mailbox with random content
########

##Introduction
#This script has been put together to enable random email content to be generated from Open Source content
#and then to relay that mail through a local SMTP relay. Once this content is generated a PST file can be 
#exported and then imported into a live mailbox account on Office 365 for testing purposes. All content referenced
#here can be downloaded in a seperate zip file from my blog site. https://www.leeejeffries.com/wp-content/uploads/2018/09/Random_Content.zip
#The file paths will need to be changed to reflect the location you extract them to.
#
#The text content and subject lines of emails are generated from a public domain ebook
#The images, video and audio are all public domain open license so should be okay to use
#without incurring any copyright infringement
#
#Script to be run in powershell 2.0 or newer
#Just place in the smtpserver (Assuming unauthenticated) and the To and From address of the sender
#Amend the content locations and you are good to go
#Note: The script is infinite so a CTRL+C will exit it when you require it to stop
##
#Install-Module Microsoft.Graph -Scope CurrentUser
Import-Module Microsoft.Graph.Users.Actions
Connect-MgGraph 
#-NoWelcome

#Function to  generate random text between 100 and 400 words from an array of strings
Function Random-Text([Array] $stringArray) {
    #Reset the selected text variable
    $selectedText = ""
    #Build the random number of times we will loop and collect words
    $maximumWords = Get-Random -Minimum 100 -Maximum 1000
    do {
        $selectedText = $selectedText + $stringArray[(Get-Random -Maximum ([array]$stringArray).count)]
        $selectedText = $selectedText + " "
        $i++
    } until ($i -eq $maximumWords)
    return $selectedText
}

#Function to randomly generate an email subject from a random array of strings
Function Email-Subject([Array] $stringArray) {
    #Reset the selected text varibale
    $selectedText = ""
    #Build the random number of times we will loop and collect words
    $maximumWords = Get-Random -Minimum 1 -Maximum 10
    do {
        $selectedText = $selectedText + $stringArray[(Get-Random -Maximum ([array]$stringArray).count)]
        $selectedText = $selectedText + " "
        $i++
    } until ($i -eq $maximumWords)
    return $selectedText
}

#Location of Movie file attachments
$movieLocation = "C:\temp\MOV\"
#Location of MP3 music attachments
$audioLocation = "C:\temp\MP3\"
#Location of JPG picture attachments
$imageLocation = "C:\temp\JPG\"
#Location of text document that holds words, an ebook in this case
$textLocation = "C:\temp\ebook.txt"
#badmaker
$badFile = "C:\temp\Litware_SOW.doc"

#GTUBE - Generic Test for Unsolicited Bulk Email (triggers spam detection in EOP/MDO)
$gtubeString = "XJS*C4JDBQADN1.NSBN3*2IDNEN*GTUBE-STANDARD-ANTI-UBE-TEST-EMAIL*C.34X"

#Phishing test URLs (triggers Safe Links / URL detonation in MDO)
$phishingTestUrls = @(
    "https://highspamlink.contoso.com"
)

#Address details
$toAddresses = @(
    "meganb@fancygeekgirl.com",
    "jonis@fancygeekgirl.com",
    "leeg@fancygeekgirl.com",
    "alexw@fancygeekgirl.com",
    "adelev@fancygeekgirl.com"
)
$fromAddress = "anfisher@fancygeekgirl.com"

#Create all arrays of files and an array of words from the ebook
$movieFiles = @(Get-ChildItem -Path $movieLocation)
$audioFiles = @(Get-ChildItem -Path $audioLocation)
$imageFiles = @(Get-ChildItem -Path $imageLocation)
$textFile = Get-Content $textLocation
$stringArray = @($textfile.Split(" "))

#Loop through each recipient and send 20 emails to each
foreach ($recipient in $toAddresses) {
    $toRecipients = @(@{ emailAddress = @{ address = $recipient } })
    $tracker = 0
    Write-Host "`nSending 20 emails to $recipient..."

    do {
        #Select a random amount of words from our ebook and also a random file of each type
    $selectedText = Random-Text -stringArray $stringArray
    $selectedMovie = $movieFiles[(Get-Random -Maximum ([array]$movieFiles).count)]
    $selectedAudio = $audioFiles[(Get-Random -Maximum ([array]$audioFiles).count)]
    $selectedImage = $imageFiles[(Get-Random -Maximum ([array]$imageFiles).count)]

    #Pick a number between 1 and 10 to see if there will be a Movie,Music,Image or no attachment
    $numberSelected = Get-Random -Minimum 1 -Maximum 10

    switch($numberSelected){
        1 {$selectedAttachment = $selectedMovie.FullName}
        2 {$selectedAttachment = $selectedAudio.FullName}
        3 {$selectedAttachment = $badFile}
        4 {$selectedAttachment = $selectedImage.FullName}
        5 {$selectedAttachment = ""}
        6 {$selectedAttachment = ""}
        7 {$selectedAttachment = ""}
        8 {$selectedAttachment = ""}
        9 {$selectedAttachment = ""}
        10 {$selectedAttachment = ""}
    }

    #Randomly inject GTUBE spam test string or phishing URL into ~30% of messages
    $injectThreat = (Get-Random -Minimum 1 -Maximum 10) -le 3
    $threatType = "none"
    if ($injectThreat) {
        $threatChoice = Get-Random -Minimum 1 -Maximum 3
        switch ($threatChoice) {
            1 {
                $selectedText = $selectedText + "`n`n" + $gtubeString + "`n"
                $threatType = "GTUBE"
            }
            2 {
                $randomUrl = $phishingTestUrls[(Get-Random -Maximum $phishingTestUrls.Count)]
                $selectedText = $selectedText + "`nClick here to verify your account: $randomUrl`n"
                $threatType = "PHISH-URL"
            }
        }
    }

    #Call the function to generate a random email Subject
    $selectedSubject = Email-Subject -stringArray $stringArray

    If ($numberSelected -gt 4) {
        # No attachment
        $params = @{
            message = @{
                subject = $selectedSubject
                body = @{
                    contentType = "Text"
                    content = $selectedText
                }
                toRecipients = @($toRecipients)
            }
            saveToSentItems = "false"
        }
        Send-MgUserMail -UserId $fromAddress -BodyParameter $params
    } else {
        # With attachment
        $base64Bytes = [Convert]::ToBase64String([IO.File]::ReadAllBytes($selectedAttachment))
        $params = @{
            message = @{
                subject = $selectedSubject
                body = @{
                    contentType = "Text"
                    content = $selectedText
                }
                toRecipients = @($toRecipients)
                attachments = @(
                    @{
                        "@odata.type" = "#microsoft.graph.fileAttachment"
                        name = (Split-Path $selectedAttachment -Leaf)
                        contentType = "application/octet-stream"
                        contentBytes = $base64Bytes
                    }
                )
            }
            saveToSentItems = "false"
        }
        Send-MgUserMail -UserId $fromAddress -BodyParameter $params
    }
    
    #Increment email being sent
    $tracker++
    $threatFlag = if ($threatType -ne "none") { "[$threatType]" } else { "" }
    "[$recipient] Email $tracker/20 - $numberSelected $threatFlag - $selectedSubject - $selectedAttachment"
   
    } until ($tracker -eq 20)
}
