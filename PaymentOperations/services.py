# Requried Libraries
import pandas as pd
import os
import re

# Folder Location
MEDIA_UPLOAD_PATH = 'media/uploads/'
OUTPUT_PATH =  'outputs/'

# Function to extract Partner Pin from Description
def extract_partner_pin(description):
    if pd.isna(description):
        return None

    text = str(description).strip()
    match = re.search(r'(\d{9})(?!.*\d)', str(description))
    return match.group(1) if match else None

# Function to read and clean statement file
def read_and_clean_statement_file(statement_file):
    ############################ Fetching Statement File & removing unused rows ##############################
    statement_file = os.path.join(MEDIA_UPLOAD_PATH, statement_file)

    # Reading Statement File data
    df = pd.read_excel(statement_file, header=9)

    # Now delete row 11 ONLY 
    df = df.drop(index=0).reset_index(drop=True)

    # Clean column names
    df.columns = df.columns.astype(str).str.strip()

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
    ############################# Reading Settlement File & Removing unused rows #############################
    settlement_file = os.path.join(MEDIA_UPLOAD_PATH, settlement_file)

    df = pd.read_excel(settlement_file, header=None)
    
    df.columns = df.iloc[2].astype(str).str.strip()

    df = df.iloc[3:].reset_index(drop=True)

    # Clean column names
    df.columns = df.columns.astype(str).str.strip()

    ############################# Creating new column "Estimate Amount(usd)" ##################################
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

    return df.copy()

    ###############################################################################################

def MatchingAndTagingEntries(statement_df, settlement_df):
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
    summary_counts = [present_in_both, only_in_settlement, only_in_statement]

    return summary_counts

    # Count of records
    # print("Summary Counts:", summary_counts)

def ComparingPresentInBothAmount(statement_df, settlement_df, present_in_both):
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
    return len(amount_compare_df)

def FindingVariance(statement_df, only_in_statement):
    variance_df = statement_df[
        (statement_df["Type"] == "Should Reconcile") &
        (statement_df["PartnerPin"].astype(str).str.strip().isin(only_in_statement))
    ].copy()

    return len(variance_df)

def main():
    # Reading both files & cleaning data
    statement_df = read_and_clean_statement_file("Statement.xlsx")
    settlement_df = read_and_clean_settlement_file("Settlement.xlsx")

    # Matching and Taging
    entries_data = MatchingAndTagingEntries(statement_df, settlement_df)

    # Comparing Amounts
    amount_compare_df = ComparingPresentInBothAmount(statement_df, settlement_df, entries_data[0])

    # Finding Variance
    variance = FindingVariance(statement_df, entries_data[2])

    return {
        "present_in_both_count": len(entries_data[0]),
        "only_in_settlement_count": len(entries_data[1]),
        "only_in_statement_count": len(entries_data[2]),
        "amount_match_count": amount_compare_df,
        "variance_count": variance
    }




