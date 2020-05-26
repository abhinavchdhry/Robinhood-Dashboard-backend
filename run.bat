@echo off
set RH_USERNAME=abhinav155.bits@gmail.com
set RH_DEVICE_TOKEN=62f7039e-d0ae-41ed-9cfd-88cb00d22d60

set "psCommand=powershell -Command "$pword = read-host 'Enter Robinhood Password' -AsSecureString ; ^
    $BSTR=[System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($pword); ^
        [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)""
for /f "usebackq delims=" %%p in (`%psCommand%`) do set password=%%p

set RH_PASSWORD=%password%
echo Success! Password stored in environment. Moving on...

python csv-export.py --start '2020-05-22T00:00:00Z' --end '2020-05-22T00:00:00Z'