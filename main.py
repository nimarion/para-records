import requests
import pandas as pd
import io
import argparse

disciplineMapping = pd.read_csv("mapping/disciplines.csv").astype(str)
countriesMapping = pd.read_csv("mapping/countries.csv").astype(str)
areaMapping = pd.read_csv("mapping/areas.csv").astype(str)

if __name__ == '__main__':
    argparse = argparse.ArgumentParser()
    argparse.add_argument("--url", help="URL to download the records from", required=True)
    argparse.add_argument("--output", help="Output file name", required=True)
    argparse.add_argument("--code", help="Record Code WR,AL;NR", required=False)
    args = argparse.parse_args()

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }

    resp = requests.get(args.url, verify=False, headers=headers)
    resp.raise_for_status() 
    print("Downloading IPC Records from: " + args.url)
    # save content to file
    with open("ipc_records.xlsx", "wb") as f:
        f.write(resp.content)

    df  = pd.read_excel(io.BytesIO(resp.content), header=0, engine="openpyxl")

    # Remove IPC "Header"
    event_code_index = df[df.eq("Event Code").any(axis=1)].index[0]
    df = df.iloc[event_code_index:]
    df.columns = df.iloc[0]
    df = df[1:]
    df.reset_index(drop=True, inplace=True)

    # Drop every row where vacant is set
    df = df[~df.eq("vacant").any(axis=1)]

    print(df.head())

    # Drop all rows where "SDMS ID" is 1 or NaN
    if "SDMS ID" in df.columns:
        df = df[~df["SDMS ID"].eq(1)]
        df = df.dropna(subset=["SDMS ID"])

    # remove all where Equalled is "="
    if "Equalled" in df.columns:
        df = df[~df["Equalled"].eq("=")]

    # Remove Womens's or Men's Prefix from Event Type
    if "Event Type" in df.columns:
        df["Event Type"] = df["Event Type"].str.split(" ", n=1).str[1]

    if "Event" in df.columns:
        # 4x100 m Universal Relay is a special case, because it has no class and the event type is 4x100 m
        mask = df["Event"] == "4x100 m Universal Relay"
        df.loc[mask, "Class"] = "X"
        df.loc[mask, "Event Type"] = "4x100 m"

        # Handle all other rows
        df.loc[~mask, "Class"] = df.loc[~mask, "Event"].str.split().str[-1]
        df.loc[~mask, "Event Type"] = (
            df.loc[~mask, "Event"].str.split().str[1:-1].str.join(" ")
        )

        df = df.drop(columns=["Event"])

    if "Rank" in df.columns:
        df = df[df["Rank"].eq(1)]
        df = df.drop(columns=["Rank"])

    split_rows = []
    for index, row in df.iterrows():
        class_value = row['Class']
        prefix = class_value[0]   # T

        # split by /
        parts = class_value.split('/')

        for part in parts:
            # if no prefix in later parts, add it
            if not part[0].isalpha():
                part = prefix + part

            if '-' in part:
                start_end = part[1:].split('-')   # remove T
                start = int(start_end[0])
                end = int(start_end[1])

                for i in range(start, end + 1):
                    new_row = row.copy()
                    new_row['Class'] = prefix + str(i)
                    split_rows.append(new_row)

            else:
                new_row = row.copy()
                new_row['Class'] = part
                split_rows.append(new_row)

    df = pd.DataFrame(split_rows)

    df["Klasse"] = df.apply(
        lambda row: row["Class"]
        if str(row["Class"]).upper() == "X"
        else str(row["Gender"]) + str(row["Class"]),
        axis=1
    )
    df["Geschlecht"] = df["Gender"].map({"M": "Male", "W": "Female"})
    df['Birth'] = df['Birth'].fillna(-1).astype(float).astype(int)
    # replace all Birth -1 with NaN
    df['Birth'] = df['Birth'].replace(-1, pd.NA)
    df = df.drop(columns=["Event Code", "Time (ms)", "SDMS ID", "Gender", "Class", "Equalled"], errors="ignore")
    # rename Event Type to discipline
    df = df.rename(columns={"Event Type": "discipline"})

    mapping = disciplineMapping[["ipc", "taf"]]
    mapping.columns = ["discipline", "taf"]
    df = pd.merge(df, mapping, on="discipline", how="left")

    if df["taf"].isna().sum() > 0:
        print(df[df["taf"].isna()])
        print(df.loc[df["taf"].isna(), ["discipline", "Klasse"]])
        df = df.dropna(subset=["taf"])
        raise ValueError("Some disciplines are not mapped")

    df = df.drop(columns=["discipline"], errors="ignore")
    df = df.rename(columns={"taf": "Bewerb"})

    mapping = countriesMapping[["countryCode", "countryName"]]
    mapping.columns = ["countryCode", "Country"]
    df = pd.merge(df, mapping, on="Country", how="left")
    df = df.drop(columns=["Country"], errors="ignore")
    df = df.rename(columns={"countryCode": "RNAT"})

    if args.code and (args.code == "PAL" or args.code == "PAR"):
        mapping = areaMapping[["Country", "AreaId"]]
        mapping.columns = ["NPC", "AreaId"]
        df = pd.merge(df, mapping, on="NPC", how="left")
        df = df.rename(columns={"AreaId": "Typ"})
        # NPC RPA  -> Neutral Paralympic Athlete,Russia Paralympic Committee
        df["Typ"] = df["Typ"].fillna(0)
    

    df["Umgebung"] = "Outdoor"

    df["Result"] = df["Time"].fillna(df["Width"]).fillna(df["Points"])
    df = df.rename(columns={"Wind Speed": "Wind", "Family Name": "Name", "Given Name": "Vorname", "Birth": "YOB", "NPC": "Nation", "Date": "Datum", "City": "RORT", "Result": "Leistung", "Record Type": "Code"})

    if(args.code):
        df["Code"] = args.code

    desired_order = ['Code', 'Typ', 'Klasse', 'Bewerb', 'Leistung', 'Wind', 'Name', 'Vorname', 'Nation', 'YOB', 'RNAT', 'RORT', 'Datum', 'Geschlecht', 'Umgebung']
    columns_to_drop = set(df.columns) - set(desired_order)
    df = df.drop(columns=columns_to_drop, errors="ignore")
    df = df.reindex(columns=desired_order)

    df = df.drop_duplicates()

    df.to_csv(args.output, index=False, sep=";")
