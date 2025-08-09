import re
import logging
from typing import Dict, Any

import random
import time

def random_delay(min_seconds: float = 1.0, max_seconds: float = 3.0):
    """Pause execution for a random duration between min_seconds and max_seconds."""
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)


def validate_case_inputs(case_type: str, case_number: str, filing_year: str) -> Dict[str, Any]:
    errors = []
    
    if not case_type or not case_type.strip():
        errors.append("Case type is required")
    
    if not case_number or not case_number.strip():
        errors.append("Case number is required")
    
    if not filing_year or not filing_year.strip():
        errors.append("Filing year is required")
    else:
        try:
            year = int(filing_year)
            current_year = time.gmtime().tm_year
            if year < 1950 or year > current_year + 1:
                errors.append(f"Filing year must be between 1950 and {current_year + 1}")
        except ValueError:
            errors.append("Filing year must be a valid number")
    
    if case_number:
        clean_case_number = re.sub(r'[\/\-\s]', '', case_number)
        if not re.match(r'^[A-Za-z0-9]+$', clean_case_number):
            errors.append("Case number contains invalid characters")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'message': '; '.join(errors) if errors else 'Valid inputs'
    }

def clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text.strip())
    text = re.sub(r'[^\w\s\-\.\,\:\;\(\)\/]', '', text)
    return text

def format_case_data(case_data: Dict[str, Any]) -> Dict[str, Any]:
    formatted = {}
    
    field_mappings = {
        'case_title': 'Case Title',
        'case_number': 'Case Number',
        'case_type': 'Case Type',
        'filing_date': 'Filing Date',
        'hearing_date': 'Next Hearing Date',
        'status': 'Case Status',
        'petitioner': 'Petitioner',
        'respondent': 'Respondent',
        'judge': 'Judge',
        'court_name': 'Court',
        'act': 'Act/Section',
        'stage': 'Current Stage'
    }
    
    for key, display_name in field_mappings.items():
        value = case_data.get(key, '')
        if value:
            formatted[display_name] = clean_text(str(value))
    
    if 'pdf_links' in case_data:
        formatted['Documents'] = case_data['pdf_links']
    
    formatted['_raw_data'] = case_data
    
    return formatted
