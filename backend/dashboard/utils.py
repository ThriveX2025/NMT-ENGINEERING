import os
import pandas as pd
from django.conf import settings
from datetime import datetime
from decouple import config
import gspread
from google.oauth2.service_account import Credentials
import io
import requests

def use_google_sheets():
    """Check if we should use Google Sheets"""
    return config('USE_GOOGLE_SHEETS', default='False', cast=bool)

def get_google_sheet_id():
    """Extract sheet ID from Google Sheets URL"""
    url = config('GOOGLE_SHEET_URL', default='')
    # Extract ID from URL like: https://docs.google.com/spreadsheets/d/SHEET_ID/edit...
    if '/d/' in url:
        return url.split('/d/')[1].split('/')[0]
    return None

def get_gspread_client():
    """
    Get authenticated gspread client for write operations
    Reads credentials from environment variables
    """
    try:
        # Build credentials dict from environment variables
        creds_dict = {
            "type": config('GOOGLE_TYPE', default='service_account'),
            "project_id": config('GOOGLE_PROJECT_ID', default=''),
            "private_key_id": config('GOOGLE_PRIVATE_KEY_ID', default=''),
            "private_key": config('GOOGLE_PRIVATE_KEY', default='').replace('\\n', '\n'),
            "client_email": config('GOOGLE_CLIENT_EMAIL', default=''),
            "client_id": config('GOOGLE_CLIENT_ID', default=''),
            "auth_uri": config('GOOGLE_AUTH_URI', default='https://accounts.google.com/o/oauth2/auth'),
            "token_uri": config('GOOGLE_TOKEN_URI', default='https://oauth2.googleapis.com/token'),
            "auth_provider_x509_cert_url": config('GOOGLE_AUTH_PROVIDER_CERT_URL', default='https://www.googleapis.com/oauth2/v1/certs'),
            "client_x509_cert_url": config('GOOGLE_CLIENT_CERT_URL', default=''),
            "universe_domain": config('GOOGLE_UNIVERSE_DOMAIN', default='googleapis.com')
        }
        
        # Check if required fields are present
        if not creds_dict['client_email'] or not creds_dict['private_key']:
            print("Google credentials not found in environment variables")
            return None
        
        SCOPES = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        client = gspread.authorize(creds)
        print("✓ Successfully authenticated with Google Sheets API from environment variables")
        return client
    except Exception as e:
        print(f"Error authenticating with Google Sheets: {str(e)}")
        return None

def read_google_sheet_as_excel():
    """
    Read Google Sheet and return as pandas DataFrame
    Uses authenticated access via service account
    """
    sheet_id = get_google_sheet_id()
    if not sheet_id:
        raise ValueError("Invalid Google Sheet URL")
    
    # Try authenticated access first
    client = get_gspread_client()
    if client:
        try:
            print(f"Reading Google Sheet with authentication: {sheet_id}")
            spreadsheet = client.open_by_key(sheet_id)
            worksheet = spreadsheet.sheet1
            
            # Get all values as list of lists
            data = worksheet.get_all_values()
            
            if not data:
                raise Exception("No data found in Google Sheet")
            
            # Convert to DataFrame (first row is headers)
            df = pd.DataFrame(data[1:], columns=data[0])
            print(f"Successfully loaded Google Sheet. Rows: {len(df)}, Columns: {list(df.columns)}")
            return df
        except Exception as e:
            print(f"Error reading Google Sheet with authentication: {str(e)}")
            # Fall through to try public access
    
    # Fallback: Try public export URL
    export_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx'
    
    try:
        print(f"Trying public access: {export_url}")
        response = requests.get(export_url)
        response.raise_for_status()
        
        # Read Excel data from response content
        df = pd.read_excel(io.BytesIO(response.content))
        print(f"Successfully loaded Google Sheet via public export. Rows: {len(df)}, Columns: {list(df.columns)}")
        return df
    except Exception as e:
        print(f"Error reading Google Sheet via public export: {str(e)}")
        raise Exception(f"Failed to read Google Sheet. Make sure it's shared with the service account: nmt-dashboard-service@dashboard-nmt-project.iam.gserviceaccount.com")

def get_excel_path():
    """Get the path to the Excel file"""
    return os.path.join(settings.BASE_DIR, '..', 'DATA_V2.xlsx')

def read_excel_data(limit=None):
    """
    Read data from Excel file or Google Sheets
    Returns: DataFrame or dict
    """
    try:
        if use_google_sheets():
            print("Using Google Sheets as data source")
            df = read_google_sheet_as_excel()
        else:
            print("Using local Excel file as data source")
            excel_path = get_excel_path()
            
            if not os.path.exists(excel_path):
                raise FileNotFoundError(f"Excel file not found at {excel_path}")
            
            df = pd.read_excel(excel_path)
        
        # Limit rows if specified
        if limit:
            df = df.head(limit)
        
        # Convert DataFrame to list of dictionaries for JSON serialization
        # Handle NaN values and dates
        data = df.fillna('').to_dict('records')
        
        # Convert any datetime objects to strings
        for record in data:
            for key, value in record.items():
                if pd.isna(value):
                    record[key] = None
                elif isinstance(value, (pd.Timestamp, datetime)):
                    record[key] = value.strftime('%Y-%m-%d')
        
        return data
    except Exception as e:
        print(f"Error in read_excel_data: {str(e)}")
        raise

def get_excel_info():
    """
    Get information about the Excel file or Google Sheet
    """
    try:
        if use_google_sheets():
            df = read_google_sheet_as_excel()
            return {
                'total_rows': len(df),
                'columns': list(df.columns),
                'source': 'Google Sheets',
                'sheet_id': get_google_sheet_id(),
                'last_modified': 'Real-time',
            }
        else:
            excel_path = get_excel_path()
            
            if not os.path.exists(excel_path):
                return None
            
            df = pd.read_excel(excel_path)
            
            # Get file modification time
            mod_time = os.path.getmtime(excel_path)
            last_modified = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')
            
            return {
                'total_rows': len(df),
                'columns': list(df.columns),
                'file_path': excel_path,
                'source': 'Local Excel',
                'last_modified': last_modified,
            }
    except Exception as e:
        return {
            'error': str(e),
            'source': 'Google Sheets' if use_google_sheets() else 'Local Excel',
        }

def get_excel_stats():
    """
    Get statistics from Excel data or Google Sheets
    """
    try:
        if use_google_sheets():
            df = read_google_sheet_as_excel()
        else:
            df = pd.read_excel(get_excel_path())
        
        stats = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'columns': list(df.columns),
            'source': 'Google Sheets' if use_google_sheets() else 'Local Excel',
        }
        
        # Add basic statistics for numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if numeric_cols:
            stats['numeric_columns'] = numeric_cols
            stats['numeric_stats'] = df[numeric_cols].describe().to_dict()
        
        return stats
    except Exception as e:
        return {'error': str(e)}

def update_remark(row_index, remark_value):
    """
    Update the Remark column for a specific row
    Supports both Google Sheets (with credentials) and local Excel
    """
    if use_google_sheets():
        # Try to use Google Sheets API with write permissions
        client = get_gspread_client()
        
        if not client:
            return {
                'success': False, 
                'error': 'Google Sheets write access not configured. Please set up service account credentials (see GOOGLE_SHEETS_WRITE_SETUP.md)'
            }
        
        try:
            sheet_id = get_google_sheet_id()
            spreadsheet = client.open_by_key(sheet_id)
            worksheet = spreadsheet.sheet1  # Use first sheet
            
            print(f"Updating Google Sheet row {row_index + 2} (Excel row) with remark: {remark_value}")
            
            # Find Remark column
            headers = worksheet.row_values(1)
            if 'Remark' not in headers:
                return {'success': False, 'error': 'Remark column not found in Google Sheet'}
            
            remark_col_index = headers.index('Remark') + 1  # gspread uses 1-based indexing
            
            # Update the cell (row_index + 2 because: +1 for header, +1 for 1-based indexing)
            worksheet.update_cell(row_index + 2, remark_col_index, remark_value)
            
            print(f"✓ Successfully updated Google Sheet")
            return {'success': True, 'message': 'Remark updated successfully in Google Sheets'}
            
        except Exception as e:
            print(f"Error updating Google Sheet: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': f'Failed to update Google Sheet: {str(e)}'}
    
    # Local Excel file update
    excel_path = get_excel_path()
    
    print(f"update_remark called with row_index={row_index}, remark_value={remark_value}")
    print(f"Excel path: {excel_path}")
    
    if not os.path.exists(excel_path):
        print(f"ERROR: Excel file not found at {excel_path}")
        return {'success': False, 'error': 'Excel file not found'}
    
    try:
        # Read Excel file
        print("Reading Excel file...")
        df = pd.read_excel(excel_path)
        print(f"Excel loaded. Total rows: {len(df)}, Columns: {list(df.columns)}")
        
        # Add Remark column if it doesn't exist
        if 'Remark' not in df.columns:
            print("Remark column not found, adding it...")
            df['Remark'] = 'Pending Email'
        
        # Validate row index
        if row_index < 0 or row_index >= len(df):
            print(f"ERROR: Invalid row index {row_index}. Valid range: 0-{len(df)-1}")
            return {'success': False, 'error': f'Invalid row index. Valid range: 0-{len(df)-1}'}
        
        # Update the remark
        print(f"Updating row {row_index} with remark: {remark_value}")
        df.at[row_index, 'Remark'] = remark_value
        
        # Save back to Excel
        print("Saving Excel file...")
        df.to_excel(excel_path, index=False)
        print("Excel file saved successfully!")
        
        return {'success': True, 'message': 'Remark updated successfully'}
    except Exception as e:
        print(f"ERROR in update_remark: {str(e)}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}
