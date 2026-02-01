import pandas as pd
import os
import re

# Folder Location
MEDIA_UPLOAD_PATH = 'media/uploads/'
OUTPUT_PATH =  'outputs/'

# Function to extract Partner Pin
def extract_partner_pin(description):
    if pd.isna(description):
        return None

    text = str(description).strip()
    match = re.search(r'(\d{9})(?!.*\d)', str(description))
    return match.group(1) if match else None

# Function to read and clean statement file
def read_and_clean_statement_file(statement_file):
    ############################## Reading Statement File data ##############################
    statement_file = os.path.join(MEDIA_UPLOAD_PATH, statement_file)

    df = pd.read_excel(statement_file, header=9)

    # 2️⃣ Now delete row 11 ONLY (Excel row 11 → index 1 after header)
    df = df.drop(index=0).reset_index(drop=True)

    # Clean column names
    df.columns = df.columns.astype(str).str.strip()

    # 3️⃣ Write to Excel for verification
    # output_file = os.path.join(
    #     OUTPUT_PATH, "statement_after_row_deletion.xlsx"
    # )
    # df.to_excel(output_file, index=False)

    # print("Final cleaned DataFrame:")
    # print(df.head())
    # print(f"Written to {output_file}")
    ###########################################################################################
    ############################## Fetching Partner Pin from Description Col[D] ##############################
    df["PartnerPin"] = df.iloc[:,3].apply(extract_partner_pin)

    df["is_duplicate"] = df["PartnerPin"].duplicated(keep=False)

    # Duplicates + Cancel
    df.loc[(df["is_duplicate"]) & (df["Type"].str.strip() == "Cancel"), "Type"] = "Should Reconcile"

    # Duplicates + Dollar Received
    df.loc[(df["is_duplicate"]) & (df["Type"].str.strip() == "Dollar received"),"Type"] = "Should Not Reconcile"

    # Non-Duplicates
    df.loc[(~df["is_duplicate"]),"Type"] = "Should Reconcile"

    return df.copy()

    ###########################################################################################

# Function to read and clean settlement file
def read_and_clean_settlement_file(settlement_file):
    ############################## Reading Settlement File data ##############################
    settlement_file = os.path.join(MEDIA_UPLOAD_PATH, settlement_file)

    df = pd.read_excel(settlement_file, header=None)
    
    df.columns = df.iloc[2].astype(str).str.strip()

    df = df.iloc[3:].reset_index(drop=True)

    # Clean column names
    df.columns = df.columns.astype(str).str.strip()

    # Creating new column "Estimate Amount(usd)" 
    df["Estimate Amount(usd)"] = (
        pd.to_numeric(
            df["PayoutRoundAmt"]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.strip(),
            errors="coerce"
        )
        // pd.to_numeric(
            df["APIRATE"].astype(str).str.strip(),
            errors="coerce"
        )
    )    

    # Fetching duplicate transcations from partner pin
    df["is_duplicate"] = df["PartnerPin"].duplicated(keep=False)

    # Assigning Should Reconcile on "Cancel" type with duplicate partner pin 
    df.loc[(df["is_duplicate"]) & (df["Status"].str.strip() == "Cancel"), "Status"] = "Should Reconcile"

    # Assigning Should Reconcile on "Non-Duplicate" type with duplicate partner pin
    df.loc[(~df["is_duplicate"]),"Status"] = "Should Reconcile"


    # with open('text.txt', 'w') as f:
    #     for val in df["Status"]:
    #         f.write(str(val) + '\n')

    return df.copy()


###########################################################################################

    

statement_df = read_and_clean_statement_file("Statement.xlsx")
settlement_df = read_and_clean_settlement_file("Settlement.xlsx")

################################# Compare both Type & Status from both files #################################
# Filter only "Should Reconcile"
settlement_pins = set(
    settlement_df.loc[
        settlement_df["Status"] == "Should Reconcile",
        "PartnerPin"
    ].dropna().astype(str).str.strip()
)

statement_pins = set(
    statement_df.loc[
        statement_df["Type"] == "Should Reconcile",
        "PartnerPin"
    ].dropna().astype(str).str.strip()
)

# Reconciliation logic
present_in_both = settlement_pins & statement_pins
only_in_settlement = settlement_pins - statement_pins
only_in_statement = statement_pins - settlement_pins

# Counts for UI summary cards
summary_counts = {
    "present_in_both": len(present_in_both),
    "only_in_settlement": len(only_in_settlement),
    "only_in_statement": len(only_in_statement),
}

# Count of records
print("Summary Counts:", summary_counts["present_in_both"])
###########################################################################################
# Filter only rows that are Present in Both
settlement_common = settlement_df[
    (settlement_df["Status"] == "Should Reconcile") &
    (settlement_df["PartnerPin"].astype(str).str.strip().isin(present_in_both))
].copy()

statement_common = statement_df[
    (statement_df["Type"] == "Should Reconcile") &
    (statement_df["PartnerPin"].astype(str).str.strip().isin(present_in_both))
].copy()

# Merge ONLY matched records (inner join is correct here)
amount_compare_df = settlement_common.merge(
    statement_common[["PartnerPin", "Settle.Amt"]],
    on="PartnerPin",
    how="inner"
)

# Compare amounts
amount_compare_df["Amount_Match"] = (
    amount_compare_df["Estimate Amount(usd)"].astype(float)
    == amount_compare_df["Settle.Amt"].astype(float)
)

# print(len(amount_compare_df))
###########################################################################################

###########################################################################################

# Variance -> Partner pins exists in statement but not in Settlement file
variance_df = statement_df[
    (statement_df["Type"] == "Should Reconcile") &
    (statement_df["PartnerPin"].astype(str).str.strip().isin(only_in_statement))
].copy()

print(len(variance_df))

###########################################################################################
# variance_df.to_excel("text1.xlsx", sheet_name="Sheet1", index=False)
# settlement_df.to_excel("text2.xlsx", sheet_name="Sheet1", index=False)