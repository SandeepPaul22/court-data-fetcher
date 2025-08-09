"""
Court Scraper Package
"""

__version__ = "1.0.0"

import os
import logging

logging.basicConfig(level=logging.INFO)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
os.makedirs(DATA_DIR, exist_ok=True)

from .database import init_db, get_db_connection
from .scraper import CourtScraper
from .utils import validate_case_inputs, format_case_data
from .forms import SearchForm

__all__ = [
    'init_db',
    'get_db_connection', 
    'CourtScraper',
    'validate_case_inputs',
    'format_case_data',
    'SearchForm'
]
