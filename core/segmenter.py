from streamlit.proto import ArrowNamedDataSet_pb2
from token import PLUS
from ctypes.wintypes import POINT
import pandas as pd

def process_segmentation(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies business logic to categorize transactions by business segment,
    maps failure reasons (Final Message), and assigns Error Segments.
    """
    df = df.copy()

    # 1. Business Segment Mapping
    # Maps Client Names to their respective Business Units
    biz_map = {
        "ACCRA HEARTS OF OAK SC": "Corporate",
        "Ahantaman Rural Bank": "Corporate",
        "KORBA 365": "Retail",
        "KORBA PAY": "Retail",
        "KORBA SMB": "SMB",
        "Mtn Products": "Retail",
        "SMB FLOAT": "SMB",
        "IGNITIA GHANA LTD": "Corporate",
        "UGCCU": "Corporate",
        "Oloan": "Corporate",
        "Korba FT": "Retail",
        "ASANTE KOTOKO SPORTING CLUB LIMITED": "Corporate",
        "AYATICKETS LTD.": "Corporate",
        "BENBOABEN PLUS LIMITED COMPANY": "Corporate",
        "BLUE IDEAR": "Corporate",
        "Chatbots Ghana": "Corporate",
        "Coronation Insurance": "Corporate",
        "EBENEZER THOMPSON MEMORIAL SCHOOL": "Corporate",
        "Empowerment Worship Center": "Corporate",
        "ENTERPRISE CLAIMS": "Corporate",
        "ENTERPRISE FUNERAL SERVICES GHANA LIMITED": "Corporate",
        "FAITHWORD CHARISMATIC MINISTRIES": "Corporate",
        "Ga Rural Bank Limited": "Corporate",
        "GameKaya (Efini)": "Corporate",
        "GH BET": "Corporate",
        "Ghana Gas Senior Staff Association Cooperative Credit Union": "Corporate",
        "Ghana Rubber Estate Ltd Co-operative credit union (GRELCCU)": "Corporate",
        "Group of pages Limited Company": "Corporate",
        "Hydro Co-operative Credit Union": "Corporate",
        "Hyper Pay Ghana": "Corporate",
        "INGAME TECHNOLOGY LTD": "Corporate",
        "KELEMM TECHNOLOGY GHANA": "Corporate",
        "BEST POINT SAVINGS AND LOANS": "Corporate",
        "CALBANK": "Corporate",
        "GN BANK": "Corporate",
        "First Atlantic Bank": "Corporate", 
        "GameKaya (Efini)": "Corporate",
        "GH BET": "Corporate",
        "Ghana Gas Senior Staff Association Cooperative Credit Union": "Corporate",
        "Ghana Rubber Estate Ltd Co-operative credit union (GRELCCU)": "Corporate",
        "Group of pages Limited Company": "Corporate",
        "Hydro Co-operative Credit Union": "Corporate",
        "Hyper Pay Ghana": "Corporate",
        "INGAME TECHNOLOGY LTD": "Corporate",
        "KELEMM TECHNOLOGY GHANA": "Corporate",
        "BEST POINT SAVINGS AND LOANS": "Corporate",
        "CALBANK": "Corporate",
        "GN BANK": "Corporate",
        "First Atlantic Bank": "Corporate", 
        "KRISH TECH ENTERPRISE": "Corporate",
        "Kwami Alone Enterprise": "Corporate",
        "LIFELINE FOR CHILDHOOD CANCER GHANA": "Corporate",
        "Loud Company Limited": "Corporate",
        "Loyalty Insurance Disbursement": "Corporate",
        "LUCKYLIVE (FORTULIVE)": "Corporate",
        "Methodist Church Koforidua Diocese Co-operative Credit Union (MCKDCCU)": "Corporate",
        "Mighty Service Venture": "Corporate",
        "Mobicom Excite": "Corporate",
        "POLICE HOSPITAL CO-OPERATIVE CREDIT UNION": "Corporate",
        "POWERCARE ENERGY LTD": "Corporate",
        "PRESTO SOLUTIONS": "Corporate",
        "Prudential Life": "Corporate",
        "Rancard Solutions": "Corporate",
        "RESOLUT BUSINESS SOLUTIONS LTD": "Corporate",
        "ROBSAM TECHNOLOGIES": "Corporate",
        "SAVEST TECHNOLOGY LIMITED": "Corporate",
        "Speakupp Digital Services": "Corporate",
        "STASH UP SUSU ENTERPRISE": "Corporate",
        "Sunflower": "Corporate",
        "SUPER 'J' CY-BUSINESS AND SERVICES": "Corporate",
        "TOP MENSAH VENTURES": "Corporate",
        "UGCCU": "Corporate",
        "VICTORY BIBLE CHURCH INTERNATIONAL": "Corporate",
        "WINWIN GAMES": "Corporate",
        "WIWI GAMING AND ENTERTAINMENT LIMITED": "Corporate",
        "Smb Mtn Products": "SMB",


    }

    # 2. Failure Wildcard Mapping
    # Looks for keywords in technical logs to produce a "clean" human-readable message
    wildcards = [
    ("larger", "Amount below minimum"),
    ("minimum", "Amount below minimum"),
    ("greater", "Amount below minimum"),
    ("lowest", "Amount below minimum"),

    ("duplicate", "Duplicate Transaction ID"),

    ("an error occurred", "External Application Error"),
    ("alert ID", "External Application Error"),
    ("an internal error caused", "External Application Error"),
    ("external app", "External Application Error"),
    ("External Application", "External Application Error"),
    ("External_Application", "External Application Error"),
    ("upstream", "External Application Error"),
    ("FAIL_2006", "External Application Error"),
    ("FAIL_280046", "External Application Error"),
    ("FAIL_4", "External Application Error"),
    ("failed", "External Application Error"),
    ("General failure", "External Application Error"),
    ("id does not", "External Application Error"),
    ("link", "External Application Error"),
    ("Payment failed", "External Application Error"),
    ("PC_0006: There is no online security module", "External Application Error"),
    ("resource not found", "External Application Error"),
    ("vend message", "External Application Error"),
    ("transaction failed", "External Application Error"),
    ("Rejected", "External Application Error"),
    ("Request error, please contact administrator", "External Application Error"),
    ("Sorry, we could not process your transaction", "External Application Error"),
    ("Status Check failed", "External Application Error"),
    ("There is an intermittent issue with the billing proxy at Rancard. Please retry after 10 seconds.", "External Application Error"),
    ("Token is empty", "External Application Error"),

    ("inconclusive stat", "Inconclusive Status"),

    ("insufficient fu", "Insufficient funds"),
    ("low balance", "Insufficient funds"),
    ("low_balance", "Insufficient funds"),
    ("target_authorization_error", "Insufficient funds"),

    ("Successful", "Internal Error"),
    ("system error", "Internal Error"),

    ("invalid account", "Invalid Account"),
    ("not found", "Invalid Account"),
    ("Please provide the customer_number value", "Invalid Account"),
    ("Please provide the network_code value", "Invalid Account"),
    ("Please provide the transaction_id value", "Invalid Account"),
    ("msisdn", "Invalid Account"),
    ("failed to authenticate", "Invalid Account"),

    ("amt_inv", "Invalid Amount"),
    ("taxerror", "Invalid Amount"),
    ("invalid amount", "Invalid Amount"),

    ("invalid network code", "Invalid network code"),
    ("invalid product", "Invalid Product"),

    ("enough", "Low balance"),

    ("max_trans", "Max Amount Reached"),
    ("max", "Max Amount Reached"),
    ("highest transaction", "Max Amount Reached"),
    ("limit", "Max Amount Reached"),

    ("no error code", "No error code"),

    ("11250", "None"),
    ("13", "None"),
    ("14", "None"),
    ("16", "None"),
    ("17357", "None"),
    ("20", "None"),
    ("25", "None"),

    ("accountholder_with_fri", "Payer Not Found"),
    ("sender_account_not", "Payer Not Found"),
    ("cardholder", "Payer Not Found"),
    ("merchant authentication", "Payer Not Found"),
    ("card not in service", "Payer Not Found"),
    ("error retrieving merchant", "Payer Not Found"),
    ("register", "Payer Not Found"),
    ("payer_not_found", "Payer Not Found"),

    ("prepayment", "Recipient Not Found"),
    ("bank has been selected", "Recipient Not Found"),
    ("payee_not_found", "Recipient Not Found"),
    ("institution unavailable", "Recipient Not Found"),
    ("number format", "Recipient Not Found"),
    ("receiver ID is not valid", "Recipient Not Found"),
    ("record is not active", "Recipient Not Found"),

    ("resource_not_found", "Resource Not Found"),
    ("No records match the info passed", "Resource Not Found"),
    ("transaction not found", "Resource Not Found"),
    ("transaction_not_found", "Resource Not Found"),

    ("timeout", "Time Out"),
    ("Please provide the amount value", "Time Out"),
    ("expiired", "Time Out"),
    ("timed out", "Time Out"),
    ("conta", "Time Out"),

    ("pin", "Wrong PIN"),
    ("locked", "Wrong PIN"),

    ("format", "Data Format Error"),
    ("rejected by provider", "External Provider Rejection"),
]

    # 3. Error Segment Mapping
    # Categorizes the "Final Message" into a responsibility segment
    # 'Operational' is used for successful or pending transactions
    error_segment_map = {
        "Amount below minimum": "Customer",
        "Duplicate Transaction ID": "External",
        "External Application Error": "External",
        "Insufficient funds": "Customer",
        "Internal Error": "Internal",
        "Time Out": "Customer",
        "Invalid Account": "Customer",
        "External Provider Rejection": "External",
        "Data Format Error": "Internal",
        "Uncategorized Failure": "External"
    }

    # --- Column Detection ---
    # Automatically finds columns even if names are slightly different
    client_col = next((c for c in df.columns if 'client' in c and 'name' in c), 'client_name')
    status_col = next((c for c in df.columns if 'status' in c), 'transaction_status')
    msg_col = next((c for c in df.columns if 'message' in c or 'exchange' in c), 'exchange_message')

    # Ensure columns exist to prevent crashes
    if client_col not in df.columns:
        df[client_col] = "Unknown"
    if msg_col not in df.columns:
        df[msg_col] = ""

    # A. Assign Business Segment
    # Strips whitespace and maps; defaults to "Unknown" if no match found
    df['biz_segment'] = df[client_col].astype(str).str.strip().map(biz_map).fillna("Unknown")

    # B. Processing Logic for Messages and Segments
    def get_analysis(row):
        status = str(row.get(status_col, '')).lower().strip()
        msg = str(row.get(msg_col, '')).strip()

        # Handle Success/Pending first (No Error Segment needed)
        if status in ['success', 'pending', 'reprocessing', 'approved']:
            return status.capitalize(), "Operational"

        # Handle Failures
        if status == 'failed' or status == 'error':
            final_msg = "Uncategorized Failure"
            
            # Check tech message against wildcards
            for keyword, clean_msg in wildcards:
                if keyword.lower() in msg.lower():
                    final_msg = clean_msg
                    break
            
            # Look up the Error Segment based on the clean message
            err_seg = error_segment_map.get(final_msg, "External")
            return final_msg, err_seg
            
        # Fallback for undefined statuses
        return "Unknown Status", "Operational"

    # C. Apply the logic across the dataframe
    df[['final_message', 'error_segment']] = df.apply(
        lambda x: pd.Series(get_analysis(x)), axis=1
    )

    return df