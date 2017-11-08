#!/bin/bash

echo 'fetching configuration from NIFI'
python fetchConfiguration.py
echo 'configuration fetched'
echo 'starting data collection from machine'
python plc_collect.py
