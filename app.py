"""
Court Data Fetcher - Main Flask Application with Real Delhi High Court Scraping
"""

from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from court_scraper.database import init_db, get_db_connection
from court_scraper.scraper import CourtScraper
from court_scraper.forms import SearchForm
from court_scraper.utils import validate_case_inputs, format_case_data
import os
import logging
from datetime import datetime
import traceback

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
app.config['DEBUG'] = True

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

# Ensure directories exist
os.makedirs('data', exist_ok=True)
os.makedirs('logs', exist_ok=True)

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    
    if request.method == 'GET':
        return render_template('search.html', form=form)
    
    if form.validate_on_submit():
        try:
            case_type = form.case_type.data
            case_number = form.case_number.data
            filing_year = str(form.filing_year.data)
            captcha_text = request.form.get('captcha_text')
            
            # Validation
            validation_result = validate_case_inputs(case_type, case_number, filing_year)
            if not validation_result['valid']:
                flash(validation_result['message'], 'error')
                return render_template('search.html', form=form)
            
            # Log search attempt
            log_search_query(case_type, case_number, filing_year)
            
            # Initialize scraper and search
            scraper = CourtScraper()
            app.logger.info(f"Starting search for: {case_type}/{case_number}/{filing_year}")
            
            result = scraper.search_case(case_type, case_number, filing_year, captcha_text)
            
            # Handle CAPTCHA requirement
            if result.get('need_captcha'):
                flash('CAPTCHA verification required. Please solve the CAPTCHA below.', 'info')
                return render_template('search.html', 
                                     form=form,
                                     captcha_image=result.get('captcha_image'),
                                     captcha_data={
                                         'case_type': case_type,
                                         'case_number': case_number,
                                         'filing_year': filing_year
                                     })
            
            # Handle successful search
            if result['success']:
                formatted_data = format_case_data(result['data'])
                
                # Add success message
                if 'MOCK' in result.get('message', ''):
                    flash('Showing mock data - Install Playwright for real scraping', 'warning')
                else:
                    flash('Case information retrieved successfully', 'success')
                
                return render_template('results.html', 
                                     case_data=formatted_data,
                                     search_params={
                                         'case_type': case_type,
                                         'case_number': case_number,
                                         'filing_year': filing_year
                                     })
            else:
                flash(result.get('message', 'Search failed'), 'error')
                return render_template('search.html', form=form)
                
        except Exception as e:
            app.logger.error(f"Search error: {str(e)}")
            app.logger.error(traceback.format_exc())
            flash('An unexpected error occurred. Please try again later.', 'error')
            return render_template('search.html', form=form)
    
    # Form validation failed
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'{field}: {error}', 'error')
    
    return render_template('search.html', form=form)

@app.route('/api/search', methods=['POST'])
def api_search():
    """API endpoint for case search"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        case_type = data.get('case_type')
        case_number = data.get('case_number')
        filing_year = str(data.get('filing_year', ''))
        captcha_text = data.get('captcha_text')
        
        # Validate inputs
        validation_result = validate_case_inputs(case_type, case_number, filing_year)
        if not validation_result['valid']:
            return jsonify({'success': False, 'message': validation_result['message']}), 400
        
        # Log API request
        log_search_query(case_type, case_number, filing_year, is_api=True)
        
        # Perform search
        scraper = CourtScraper()
        result = scraper.search_case(case_type, case_number, filing_year, captcha_text)
        
        if result.get('need_captcha'):
            return jsonify({
                'success': False,
                'need_captcha': True,
                'captcha_image': result.get('captcha_image'),
                'message': result.get('message', 'CAPTCHA required')
            }), 200
        
        if result['success']:
            formatted_data = format_case_data(result['data'])
            return jsonify({
                'success': True,
                'data': formatted_data,
                'search_params': {
                    'case_type': case_type,
                    'case_number': case_number,
                    'filing_year': filing_year
                },
                'message': result.get('message', 'Success')
            })
        else:
            return jsonify({
                'success': False, 
                'message': result.get('message', 'Search failed')
            }), 404
            
    except Exception as e:
        app.logger.error(f"API search error: {str(e)}")
        return jsonify({
            'success': False, 
            'message': 'Internal server error'
        }), 500

@app.route('/health')
def health_check():
    """Health check endpoint with Playwright status"""
    try:
        from playwright.sync_api import sync_playwright
        playwright_status = "available"
    except ImportError:
        playwright_status = "not_installed"
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'scraper': 'delhi_high_court',
        'playwright': playwright_status,
        'features': {
            'real_scraping': playwright_status == "available",
            'captcha_support': True,
            'pdf_extraction': True,
            'mock_fallback': True
        }
    })

@app.route('/install-playwright')
def install_playwright():
    """Helper endpoint to show Playwright installation instructions"""
    return jsonify({
        'message': 'To enable real scraping, install Playwright',
        'instructions': [
            'pip install playwright',
            'playwright install chromium',
            'Restart the application'
        ],
        'current_mode': 'mock_data_only'
    })

def log_search_query(case_type, case_number, filing_year, is_api=False, success=True):
    """Log search query to database"""
    try:
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO search_logs (case_type, case_number, filing_year, is_api, success)
            VALUES (?, ?, ?, ?, ?)
        ''', (case_type, case_number, filing_year, is_api, success))
        conn.commit()
        conn.close()
    except Exception as e:
        app.logger.error(f"Logging error: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)