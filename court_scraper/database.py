import sqlite3
import json
import logging
import os
from typing import Dict, Any

DATABASE_PATH = 'data/court_data.db'

def get_db_connection():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_type TEXT NOT NULL,
                case_number TEXT NOT NULL,
                filing_year TEXT NOT NULL,
                search_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_api BOOLEAN DEFAULT FALSE,
                success BOOLEAN DEFAULT TRUE,
                ip_address TEXT,
                user_agent TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_type TEXT NOT NULL,
                case_number TEXT NOT NULL,
                filing_year TEXT NOT NULL,
                case_title TEXT,
                petitioner TEXT,
                respondent TEXT,
                filing_date TEXT,
                hearing_date TEXT,
                status TEXT,
                judge TEXT,
                court_name TEXT,
                case_data JSON,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(case_type, case_number, filing_year)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS raw_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_type TEXT NOT NULL,
                case_number TEXT NOT NULL,
                filing_year TEXT NOT NULL,
                html_content TEXT,
                parsed_data JSON,
                response_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pdf_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id INTEGER,
                document_type TEXT,
                document_title TEXT,
                pdf_url TEXT,
                file_path TEXT,
                file_size INTEGER,
                download_timestamp DATETIME,
                FOREIGN KEY (case_id) REFERENCES cases (id)
            )
        ''')

        conn.commit()
        logging.info("Database initialized successfully")

    except Exception as e:
        logging.error(f"Database initialization failed: {str(e)}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

def save_case_data(case_data: Dict[str, Any]) -> bool:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO cases (
                case_type, case_number, filing_year, case_title,
                petitioner, respondent, filing_date, hearing_date,
                status, judge, court_name, case_data, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (
            case_data.get('case_type', ''),
            case_data.get('case_number', ''),
            case_data.get('filing_year', ''),
            case_data.get('case_title', ''),
            case_data.get('petitioner', ''),
            case_data.get('respondent', ''),
            case_data.get('filing_date', ''),
            case_data.get('hearing_date', ''),
            case_data.get('status', ''),
            case_data.get('judge', ''),
            case_data.get('court_name', 'Delhi High Court'),
            json.dumps(case_data or {}, ensure_ascii=False)
        ))

        conn.commit()
        logging.info("Case data saved")
        return True

    except Exception as e:
        logging.error(f"Failed to save case data: {str(e)}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def save_raw_response(case_type: str, case_number: str, filing_year: str, html_content: str, parsed_data: Dict[str, Any]) -> bool:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO raw_responses (
                case_type, case_number, filing_year, html_content, parsed_data
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            case_type,
            case_number,
            filing_year,
            html_content or '',
            json.dumps(parsed_data or {}, ensure_ascii=False)
        ))

        conn.commit()
        return True

    except Exception as e:
        logging.error(f"Failed to save raw response: {str(e)}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()