#!/bin/bash

python3 main.py --url https://www.ipc-services.org/sdms/web/records/ath/excel/type/wr --output records/world.csv 
python3 main.py --url https://www.ipc-services.org/sdms/web/records/ath/excel/type/afr --output records/africa.csv --code PAR
python3 main.py --url https://www.ipc-services.org/sdms/web/records/ath/excel/type/amr --output records/america.csv --code PAR
python3 main.py --url https://www.ipc-services.org/sdms/web/records/ath/excel/type/asr --output records/asia.csv --code PAR
python3 main.py --url https://www.ipc-services.org/sdms/web/records/ath/excel/type/eur --output records/europe.csv --code PAR
python3 main.py --url https://www.ipc-services.org/sdms/web/records/ath/excel/type/ocr --output records/oceania.csv --code PAR
python3 main.py --url https://www.ipc-services.org/sdms/web/records/ath/excel/type/pr --output records/paralympics.csv --code PR


python3 main.py --url https://www.ipc-services.org/sdms/web/rankings/ath/excel/type/world/list/1155/location/outdoor --output leads/world.csv --code WL
python3 main.py --url https://www.ipc-services.org/sdms/web/rankings/ath/excel/type/afr/list/1155/location/outdoor --output leads/africa.csv --code PAL
python3 main.py --url https://www.ipc-services.org/sdms/web/rankings/ath/excel/type/amr/list/1155/location/outdoor --output leads/america.csv --code PAL
python3 main.py --url https://www.ipc-services.org/sdms/web/rankings/ath/excel/type/asr/list/1155/location/outdoor --output leads/asia.csv --code PAL
python3 main.py --url https://www.ipc-services.org/sdms/web/rankings/ath/excel/type/eur/list/1155/location/outdoor --output leads/europe.csv --code PAL
python3 main.py --url https://www.ipc-services.org/sdms/web/rankings/ath/excel/type/ocr/list/1155/location/outdoor --output leads/oceania.csv --code PAL