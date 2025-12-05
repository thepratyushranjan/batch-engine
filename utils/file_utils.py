import csv
import io
import pandas as pd


class FileProcessingError(Exception):
    """Raised when file processing fails"""
    pass


def sanitize_column_name(name: str) -> str:
    """
    Sanitize column name for MongoDB compatibility.
    
    Args:
        name: Raw column name from file
        
    Returns:
        Sanitized column name with control characters removed
    """
    sanitized = str(name).replace('\x00', '').strip()
    sanitized = ''.join(c for c in sanitized if ord(c) >= 32 or c in '\t')
    return sanitized if sanitized else "unnamed_column"


def extract_columns_from_file(file_content: bytes, filename: str) -> dict:
    """
    Extract column names from CSV or Excel file content.
    
    Args:
        file_content: Raw bytes of the uploaded file
        filename: Original filename (used to determine file type)
        
    Returns:
        dict with 'filename' and 'columns' keys
        
    Raises:
        FileProcessingError: If file cannot be processed
    """
    file_ext = filename.lower().split('.')[-1]
    
    try:
        if file_ext in ['xlsx', 'xls']:
            df = pd.read_excel(io.BytesIO(file_content), nrows=0)
            columns = [sanitize_column_name(col) for col in df.columns.tolist()]
        else:
            encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
            decoded = None
            for encoding in encodings:
                try:
                    decoded = file_content.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if decoded is None:
                decoded = file_content.decode('utf-8', errors='ignore')
            
            decoded = decoded.replace('\x00', '')
            decoded = decoded.replace('\r\n', '\n').replace('\r', '\n')
            
            reader = csv.reader(io.StringIO(decoded, newline=''))
            columns = next(reader, [])
            columns = [sanitize_column_name(col) for col in columns if sanitize_column_name(col)]
        
        return {
            "filename": filename,
            "columns": columns
        }
    
    except Exception as e:
        raise FileProcessingError(f"Error processing file '{filename}': {str(e)}")
