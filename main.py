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

    resp = requests.get(args.url, verify=False)

    df  = pd.read_excel(io.BytesIO(resp.content), header=0)

    # Remove IPC "Header"
    event_code_index = df[df.eq("Event Code").any(axis=1)].index[0]
    df = df.iloc[event_code_index:]
    df.columns = df.iloc[0]
    df = df[1:]
    df.reset_index(drop=True, inplace=True)

    # Drop every row where vacant is set
    df = df[~df.eq("vacant").any(axis=1)]

    # Drop all rows where "SDMS ID" is 1 or NaN
    df.loc[df["SDMS ID"] == 1, "SDMS ID"] = np.nan
    df = df.dropna(subset=["SDMS ID"])

    # remove all where Equalled is "="
    if "Equalled" in df.columns:
        df = df[~df["Equalled"].eq("=")]

    # Remove Womens's or Men's Prefix from Event Type
    if "Event Type" in df.columns:
        df["Event Type"] = df["Event Type"].str.split(" ", n=1).str[1]

    if "Event" in df.columns:
        df["Class"] = df["Event"].str.split().str[-1]
        df["Event Type"] = df["Event"].str.split().str[1:-1].str.join(" ")
        df = df.drop(columns=["Event"])

    if "Rank" in df.columns:
        df = df[df["Rank"].eq(1)]
        df = df.drop(columns=["Rank"])

    split_rows = []
    for index, row in df.iterrows():
        class_value = row['Class']
        if '-' in class_value:
            classes = class_value.split('-')
            type = class_value[0]
            classes = ["".join(filter(str.isdigit, c)) for c in classes]
            start = int(classes[0])
            end = int(classes[1])
            for i in range(start, end + 1):
                new_row = row.copy()
                new_row['Class'] = type + str(i)
                split_rows.append(new_row)
        elif '/' in class_value:
            type = class_value[0]
            classes = class_value.split('/')
            for new_class in classes:
                new_row = row.copy()
                if(new_class[0] == type):
                    new_row['Class'] = new_class
                else:
                    new_row['Class'] = type + new_class
                split_rows.append(new_row)
        else: 
            split_rows.append(row)

    df = pd.DataFrame(split_rows)

    df["Klasse"] = df["Gender"].astype(str)  + df["Class"]
    df["Geschlecht"] = df["Gender"].map({"M": "Male", "W": "Female"})
    df['Birth'] = df['Birth'].fillna(-1).astype(float).astype(int)
    # replace all Birth -1 with NaN
    df['Birth'] = df['Birth'].replace(-1, pd.NA)
    df = df.drop(columns=["Event Code", "Time (ms)", "SDMS ID", "Gender", "Class", "Equalled", "Points"], errors="ignore")
    # rename Event Type to discipline
    df = df.rename(columns={"Event Type": "discipline"})

    mapping = disciplineMapping[["ipc", "taf"]]
    mapping.columns = ["discipline", "taf"]
    df = pd.merge(df, mapping, on="discipline", how="left")

    if df["taf"].isna().sum() > 0:
        print(df[df["taf"].isna()])
        raise ValueError("Some disciplines are not mapped")

    df = df.drop(columns=["discipline"], errors="ignore")
    df = df.rename(columns={"taf": "Bewerb"})

    mapping = countriesMapping[["countryCode", "countryName"]]
    mapping.columns = ["countryCode", "Country"]
    df = pd.merge(df, mapping, on="Country", how="left")
    df = df.drop(columns=["Country"], errors="ignore")
    df = df.rename(columns={"countryCode": "RNAT"})

    if args.code and (args.code == "AL" or args.code == "AR"):
        mapping = areaMapping[["Country", "AreaId"]]
        mapping.columns = ["NPC", "AreaId"]
        df = pd.merge(df, mapping, on="NPC", how="left")
        df = df.rename(columns={"AreaId": "Typ"})
        # NPC RPA  -> Neutral Paralympic Athlete,Russia Paralympic Committee
        df["Typ"] = df["Typ"].fillna(0)
    

    df["Umgebung"] = "Outdoor"

    df = df.rename(columns={"Family Name": "Name", "Given Name": "Vorname", "Birth": "YOB", "NPC": "Nation", "Date": "Datum", "City": "RORT", "Result": "Leistung", "Record Type": "Code"})

    if(args.code):
        df["Code"] = args.code

    desired_order = ['Code', 'Typ', 'Klasse', 'Bewerb', 'Leistung', 'Wind', 'Name', 'Vorname', 'Nation', 'YOB', 'RNAT', 'RORT', 'Datum', 'Geschlecht', 'Umgebung']
    columns_to_drop = set(df.columns) - set(desired_order)
    df = df.drop(columns=columns_to_drop, errors="ignore")
    df = df.reindex(columns=desired_order)

    df = df.drop_duplicates()

    df.to_csv(args.output, index=False, sep=";")

