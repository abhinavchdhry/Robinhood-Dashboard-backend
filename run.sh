#!/bin/bash

export RH_USERNAME=abhinav155.bits@gmail.com
export RH_DEVICE_TOKEN=62f7039e-d0ae-41ed-9cfd-88cb00d22d60

echo -n "Robinhood Password: "; stty -echo; read passwd; stty echo; echo
export RH_PASSWORD=$passwd

echo Success! Password stored in environment. Moving on...

python3 get-options-data.py # --start '2020-12-22T00:00:00Z' --end '2021-01-22T00:00:00Z'
