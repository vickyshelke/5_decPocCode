#!/bin/bash

echo 'Fetching configuration from NIFI'
python fetchConfiguration.py
echo 'Configuration fetched'
echo 'started genrating Random inputs'
python randomInput.py &
echo 'Starting data collection from machine'
python plc_collect.py
