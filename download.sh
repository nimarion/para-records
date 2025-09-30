#!/bin/bash

python3 main.py --url https://www.ipc-services.org/sdms/web/record/at/excel/type/WR/category/out/age/senior --output records/world.csv 
python3 main.py --url https://www.ipc-services.org/sdms/web/record/at/excel/type/AFR/category/out/age/senior --output records/africa.csv --code AF
python3 main.py --url https://www.ipc-services.org/sdms/web/record/at/excel/type/AMR/category/out/age/senior --output records/america.csv --code AM
python3 main.py --url https://www.ipc-services.org/sdms/web/record/at/excel/type/ASR/category/out/age/senior --output records/asia.csv --code AS
python3 main.py --url https://www.ipc-services.org/sdms/web/record/at/excel/type/EUR/category/out/age/senior --output records/europe.csv --code ER
python3 main.py --url https://www.ipc-services.org/sdms/web/record/at/excel/type/OCR/category/out/age/senior --output records/oceania.csv --code OC

python3 main.py --url https://www.ipc-services.org/sdms/web/ranking/at/excel/type/WR/list/1091/category/out --output leads/world.csv --code WL
python3 main.py --url https://www.ipc-services.org/sdms/web/ranking/at/excel/type/AFR/list/1091/category/out --output leads/africa.csv --code AL
python3 main.py --url https://www.ipc-services.org/sdms/web/ranking/at/excel/type/AMR/list/1091/category/out --output leads/america.csv --code AL
python3 main.py --url https://www.ipc-services.org/sdms/web/ranking/at/excel/type/ASR/list/1091/category/out --output leads/asia.csv --code AL
python3 main.py --url https://www.ipc-services.org/sdms/web/ranking/at/excel/type/EUR/list/1091/category/out --output leads/europe.csv --code AL
python3 main.py --url https://www.ipc-services.org/sdms/web/ranking/at/excel/type/OCR/list/1091/category/out --output leads/oceania.csv --code AL
python3 main.py --url https://www.ipc-services.org/sdms/web/record/at/excel/type/PR/category/out/age/senior --output records/paralympics.csv --code PR
python3 main.py --url https://www.ipc-services.org/sdms/web/record/at/excel/type/CR/category/out/age/senior --output records/championship.csv --code CR
