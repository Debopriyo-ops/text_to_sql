import pandas as pd
from io import StringIO
import re

# Your text data (provided by you)
text_data = """
CAF_SERIAL_NO|CONNECTION_TYPE|NAME_OF_ORGANIZATION|AUTHORIZED_SIGNATORY_NAME|AS_FATHER_HUSBAND_NAME|GENDER|AS_BIRTHDATE|NATIONALITY|loc_addr_houseno_flatno|LOC_ADDR_STREET_ADDR_NAME|loc_addr_landmark|LOC_ADDR_LOCALITY|LOCAL_CITY|local_addr_district|LOC_ADDR_STATE_UT_NAME|LOC_ADDR_POSTL_CODE|PERM_ADDR_HOUSENO_FLATNO|PERM_ADDR_STREET_ADDR_NAME|perm_addr_landmark|PERM_ADDR_LOCALITY|PERM_ADDR_CITY|perm_addr_district_corp|PERM_ADDR_STATE_UT_NAME|PERM_ADDR_POSTL_CODE|status_of_subscriber|WhetherCompanyIsGovtofIndiaundertakingcompanies|POI_NO|POI_DATE_OF_ISSUE|POI_PLACE_OF_ISSUE|POI_ISSUING_AUTHORITY|ADDRESS_PROOF_DOC_NUMBER|ADDRESS_PROOF_DATE_OF_ISSUE|ADDRESS_PROOF_PLACE_OF_ISSUE|ADDR_PROOF_ISSUING_AUTHORITY|POI_NO_OF_Authorized_Signatory|POI_DATE_OF_ISSUE_Authorized_Signatory|POI_PLACE_OF_ISSUE_Authorized_Signatory|POI_ISSUING_AUTHORITY_Authorized_Signatory|End_user_list|TOT_no_connection|Number_of_Mobile_connections_already_held_in_name_of_entity_comp|Tariff_Plan_Applied|Value_Added_Services_Applied|email_id|pan_gir|form_of_payment_postpaid|PAYM_DESC|Bank_Ac_No|bank_name|bank_name_address|AUTH_SIGNATORY_CONTACT|AS_OTP|AS_OTP_Validation_Date_time|Number_of_Mobile_connections_issued_as_per_End_user_list|NAME_OF_SUBSCRIBER|Designation_of_End_user|Pol_document_type_of_End_user|Pol_document_No_of_End_user|PoA_document_type_of_End_user|PoA_document_No_of_End_user|Address_mentioned_in_PoA_document_of_End_user|IMSI_allotted_to_End_user|telephone_number|POS_CODE|POS_NAME|pos_agent_name|pos_houseno_flatno|POS_STREET_ADDR_NAME|pos_landmark|POS_LOCALITY|POS_CITY|pos_district_corp|POS_STATE_UT_NAME|POS_POSTL_CODE|POS_Mobile_Number|POS_OTP|POS_OTP_validation_Date_and_Time|Latitude_Longitude_of_premises|Date_and_time_of_the_Last_physical_verification|Digitally_signed_by|AO_CODE|ACTIVATION_OFFICER|Designation_of_AO|AO_Signature_Date_and_Time|SIM_ACTIVATION_DATE|Live_photograph_of_Authorized_Signatory_captured_during_the_proc|POS_photograph_captured_during_the_process|Latitude_Longitude_of_premises_6_Months|Date_and_time_of_the_Last_physical_verification_6_Months
KOEH004O4S|Postpaid|EASTERN RAILWAY|PREETI KUMARI|RAM NAGINA  SAHU|Female|21-02-1993|Indian|E R - DIVISION SEALDAH|SEALDAH EASTERN RAILWAY||KAIZER STREE|KOLKATA||West Bengal|700014|EASTERN RAILWAY 17|N S ROAD|||KOLKATA||West Bengal|700001|Bulk|Yes|G4322|20-12-2022||CENTRAL GOVERNMENT OR STATE GOVERNMENT|2017/Tele/11-2/1|26-11-2018|New Delhi|GOVERNMENT OF INDIA|G4322|20-12-2022||CENTRAL GOVERNMENT OR STATE GOVERNMENT||16625||1405598||DSTESDAH@GMAIL.COM|AAAGM0289C||Cheque||||+9147180666|292698|15-01-2024 14:01:01|0000000614|SUBHENDU  GUHA|Technician|AADHAR|467766244698|||71ShibKrishna Daw Line Kankurgachi Main road Phulbagan 700014 WB|405873075633162|8617212423|67683768|Tanmoy Pal|Tanmoy Pal|.,|TOWER II 17TH & 18TH FLOOR,GODREJ WATERSIDE,||SALTLAKE CITY,SECTOR-V,PLOT NO: 5, BLOCK - DP|KOLKATA||West Bengal|700091|+919330027168|212831|15-01-2024 14:01:29|22.5699129,88.3740682|15-01-2024 13:34:59|Reliance Jio Infocomm Limited|55018409|Amit Kumar Das|Activation Officer|18-01-2024 17:15:02|18-01-2024 17:15:02|D:KO202401COCPAS8617212423|D:KO202401COCPAS8617212423|22.5678000,88.3710000|17-04-2024 14:15:00
"""

# Load the data into a DataFrame
data = StringIO(text_data)

# Attempt to read the data while skipping problematic lines
try:
    df = pd.read_csv(data, delimiter='|', on_bad_lines='skip')  # 'skip' skips problematic lines
    print("Data loaded successfully.")
except Exception as e:
    print(f"Error loading data: {e}")

# Function to clean up illegal characters in the data
def clean_data(df):
    # Clean any non-printable characters or null byte characters
    for col in df.columns:
        df[col] = df[col].apply(lambda x: re.sub(r'[^\x20-\x7E]', '', str(x)) if isinstance(x, str) else x)
    return df

# Replace NaN values with NULL for MySQL compatibility (this is the crucial part)
df = df.applymap(lambda x: None if pd.isna(x) else x)

# Function to generate SQL for creating table and inserting data
def generate_sql(df, table_name):
    # Start with CREATE TABLE statement
    sql = f"CREATE TABLE {table_name} (\n"
    
    # Add column definitions (TEXT is used for simplicity, you may adjust types later)
    for col in df.columns:
        sql += f"  `{col}` TEXT,\n"
    
    # Remove the last comma and close the parentheses
    sql = sql.rstrip(',\n') + '\n);\n\n'

    # Add INSERT INTO statements
    for _, row in df.iterrows():
        sql += f"INSERT INTO {table_name} ({', '.join([f'`{col}`' for col in df.columns])}) VALUES ({', '.join([repr(value) if value is not None else 'NULL' for value in row])});\n"

    return sql

# Generate the SQL file content
sql_content = generate_sql(df, "SUB_DETAILS")

# Write to an SQL file
with open("sub_data.sql", "w") as f:
    f.write(sql_content)

print("SQL file has been created: 'sub_data.sql'")
