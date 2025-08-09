import time
import logging
import json
import re
import base64
import tempfile
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
import requests

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logging.warning("Playwright not available - install with: pip install playwright && playwright install chromium")

from bs4 import BeautifulSoup
from .database import save_case_data, save_raw_response
from .utils import clean_text, random_delay

class CourtScraper:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://delhihighcourt.nic.in"
        self.search_url = "https://delhihighcourt.nic.in/case_status.asp"
        self.session = requests.Session()
        self.setup_session()
        
    def setup_session(self):
        """Setup requests session with proper headers"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

    def search_case(self, case_type: str, case_number: str, filing_year: str, captcha_text: str = None) -> Dict[str, Any]:
        """
        Search for a case using Delhi High Court website
        """
        if not PLAYWRIGHT_AVAILABLE:
            return self._fallback_mock_search(case_type, case_number, filing_year)
        
        try:
            return self._search_with_playwright(case_type, case_number, filing_year, captcha_text)
        except Exception as e:
            self.logger.error(f"Playwright search failed: {str(e)}")
            return self._fallback_mock_search(case_type, case_number, filing_year)

    def _search_with_playwright(self, case_type: str, case_number: str, filing_year: str, captcha_text: str = None) -> Dict[str, Any]:
        """
        Real search using Playwright browser automation
        """
        try:
            with sync_playwright() as p:
                # Launch browser
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu',
                        '--disable-web-security',
                        '--disable-features=VizDisplayCompositor'
                    ]
                )
                
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                
                page = context.new_page()
                page.set_default_timeout(30000)
                
                self.logger.info(f"Starting search for {case_type}/{case_number}/{filing_year}")
                
                # Step 1: Navigate to Delhi High Court case status page
                try:
                    page.goto(self.search_url, wait_until='networkidle')
                    random_delay(2, 4)
                except:
                    # Fallback to main site
                    page.goto(self.base_url, wait_until='networkidle')
                    # Look for case status link
                    try:
                        case_status_link = page.locator('a:has-text("Case Status"), a:has-text("case status"), a[href*="case_status"]').first
                        if case_status_link.is_visible():
                            case_status_link.click()
                            page.wait_for_load_state('networkidle')
                    except:
                        pass
                
                # Step 2: Fill the search form
                search_result = self._fill_search_form(page, case_type, case_number, filing_year, captcha_text)
                
                if search_result.get('need_captcha'):
                    browser.close()
                    return search_result
                
                # Step 3: Parse results
                case_data = self._parse_case_results(page, case_type, case_number, filing_year)
                
                # Step 4: Save data
                if case_data.get('success'):
                    html_content = page.content()
                    save_raw_response(case_type, case_number, filing_year, html_content, case_data['data'])
                    save_case_data(case_data['data'])
                
                browser.close()
                return case_data
                
        except Exception as e:
            self.logger.error(f"Playwright automation failed: {str(e)}")
            return {
                'success': False,
                'message': f'Browser automation failed: {str(e)}',
                'error': str(e)
            }

    def _fill_search_form(self, page, case_type: str, case_number: str, filing_year: str, captcha_text: str = None) -> Dict[str, Any]:
        """
        Fill the search form on Delhi High Court website
        """
        try:
            # Look for common form elements
            form_selectors = [
                'form[name="form1"]',
                'form[method="post"]',
                'form:first-of-type',
                'table form'
            ]
            
            form_found = False
            for selector in form_selectors:
                try:
                    if page.locator(selector).is_visible():
                        form_found = True
                        break
                except:
                    continue
            
            if not form_found:
                self.logger.warning("Could not find search form, trying alternative approach")
                return self._alternative_search_approach(page, case_type, case_number, filing_year)
            
            # Fill case type dropdown
            case_type_selectors = [
                'select[name*="case"], select[name*="Case"], select[name*="TYPE"]',
                'select:has(option:text("CWP")), select:has(option:text("CRL"))',
                'select:first-of-type'
            ]
            
            for selector in case_type_selectors:
                try:
                    case_type_dropdown = page.locator(selector).first
                    if case_type_dropdown.is_visible():
                        # Try to select by value first, then by text
                        try:
                            case_type_dropdown.select_option(value=case_type)
                        except:
                            case_type_dropdown.select_option(label=case_type)
                        break
                except:
                    continue
            
            random_delay(1, 2)
            
            # Fill case number
            case_number_selectors = [
                'input[name*="case"], input[name*="Case"], input[name*="NUMBER"]',
                'input[type="text"]:not([name*="captcha"]):not([name*="Captcha"])',
                'input[placeholder*="Case"], input[placeholder*="Number"]'
            ]
            
            for selector in case_number_selectors:
                try:
                    case_number_input = page.locator(selector).first
                    if case_number_input.is_visible():
                        case_number_input.fill(case_number)
                        break
                except:
                    continue
            
            # Fill year
            year_selectors = [
                'input[name*="year"], input[name*="Year"], input[name*="YEAR"]',
                'select[name*="year"], select[name*="Year"]',
                'input[placeholder*="Year"]'
            ]
            
            for selector in year_selectors:
                try:
                    year_element = page.locator(selector).first
                    if year_element.is_visible():
                        if year_element.get_attribute('tagName').lower() == 'select':
                            year_element.select_option(value=filing_year)
                        else:
                            year_element.fill(filing_year)
                        break
                except:
                    continue
            
            random_delay(1, 2)
            
            # Handle CAPTCHA
            captcha_result = self._handle_captcha(page, captcha_text)
            if captcha_result.get('need_captcha'):
                return captcha_result
            
            # Submit form
            submit_selectors = [
                'input[type="submit"], button[type="submit"]',
                'input[value*="Search"], input[value*="search"]',
                'button:has-text("Search"), button:has-text("search")',
                'input[name*="submit"], input[name*="Submit"]'
            ]
            
            for selector in submit_selectors:
                try:
                    submit_btn = page.locator(selector).first
                    if submit_btn.is_visible():
                        submit_btn.click()
                        break
                except:
                    continue
            
            # Wait for results
            page.wait_for_load_state('networkidle', timeout=15000)
            random_delay(2, 3)
            
            return {'success': True}
            
        except Exception as e:
            self.logger.error(f"Form filling failed: {str(e)}")
            return {
                'success': False,
                'message': f'Form filling failed: {str(e)}'
            }

    def _handle_captcha(self, page, captcha_text: str = None) -> Dict[str, Any]:
        """
        Handle CAPTCHA on the search form
        """
        try:
            # Look for CAPTCHA image
            captcha_img_selectors = [
                'img[src*="captcha"], img[src*="Captcha"], img[src*="CAPTCHA"]',
                'img[alt*="captcha"], img[alt*="Captcha"]',
                'img[name*="captcha"], img[id*="captcha"]'
            ]
            
            captcha_img = None
            for selector in captcha_img_selectors:
                try:
                    img_element = page.locator(selector).first
                    if img_element.is_visible():
                        captcha_img = img_element
                        break
                except:
                    continue
            
            if captcha_img:
                if captcha_text is None:
                    # Need CAPTCHA input from user
                    try:
                        # Get CAPTCHA image as base64
                        captcha_src = captcha_img.get_attribute('src')
                        if captcha_src.startswith('data:'):
                            # Already base64
                            captcha_image_b64 = captcha_src.split(',')[1]
                        else:
                            # Fetch image
                            if captcha_src.startswith('/'):
                                captcha_url = self.base_url + captcha_src
                            else:
                                captcha_url = urljoin(page.url, captcha_src)
                            
                            response = requests.get(captcha_url, headers=self.session.headers)
                            captcha_image_b64 = base64.b64encode(response.content).decode('utf-8')
                        
                        return {
                            'need_captcha': True,
                            'captcha_image': f"data:image/png;base64,{captcha_image_b64}",
                            'message': 'CAPTCHA verification required'
                        }
                    except Exception as e:
                        self.logger.error(f"CAPTCHA image extraction failed: {str(e)}")
                        return {
                            'success': False,
                            'message': 'CAPTCHA required but could not extract image'
                        }
                else:
                    # Fill CAPTCHA text
                    captcha_input_selectors = [
                        'input[name*="captcha"], input[name*="Captcha"], input[name*="CAPTCHA"]',
                        'input[placeholder*="captcha"], input[placeholder*="Captcha"]',
                        'input[type="text"]:near(img[src*="captcha"])'
                    ]
                    
                    for selector in captcha_input_selectors:
                        try:
                            captcha_input = page.locator(selector).first
                            if captcha_input.is_visible():
                                captcha_input.fill(captcha_text)
                                break
                        except:
                            continue
                    
                    random_delay(1, 2)
            
            return {'success': True}
            
        except Exception as e:
            self.logger.error(f"CAPTCHA handling failed: {str(e)}")
            return {
                'success': False,
                'message': f'CAPTCHA handling failed: {str(e)}'
            }

    def _parse_case_results(self, page, case_type: str, case_number: str, filing_year: str) -> Dict[str, Any]:
        """
        Parse case results from the results page
        """
        try:
            html_content = page.content()
            soup = BeautifulSoup(html_content, 'lxml')
            
            # Check for "No records found" or similar messages
            no_results_patterns = [
                'no records found', 'no record found', 'record not found',
                'case not found', 'no case found', 'no data found',
                'no result', 'not available', 'does not exist'
            ]
            
            page_text = soup.get_text().lower()
            for pattern in no_results_patterns:
                if pattern in page_text:
                    return {
                        'success': False,
                        'message': f'No case found with number {case_type}/{case_number}/{filing_year}'
                    }
            
            # Extract case information
            case_data = {
                'case_type': case_type,
                'case_number': case_number,
                'filing_year': filing_year,
                'court_name': 'Delhi High Court'
            }
            
            # Parse case details using multiple strategies
            case_data.update(self._extract_case_details(soup))
            
            # Extract PDF links
            pdf_links = self._extract_pdf_links(soup, page.url)
            if pdf_links:
                case_data['pdf_links'] = pdf_links
            
            # Generate case title if not found
            if not case_data.get('case_title'):
                petitioner = case_data.get('petitioner', 'Petitioner')
                respondent = case_data.get('respondent', 'Respondent')
                case_data['case_title'] = f"{petitioner} vs {respondent} ({case_type} {case_number}/{filing_year})"
            
            self.logger.info(f"Successfully parsed case: {case_data.get('case_title', 'Unknown')}")
            
            return {
                'success': True,
                'data': case_data,
                'message': 'Case details retrieved successfully'
            }
            
        except Exception as e:
            self.logger.error(f"Result parsing failed: {str(e)}")
            return {
                'success': False,
                'message': f'Failed to parse case results: {str(e)}',
                'error': str(e)
            }

    def _extract_case_details(self, soup: BeautifulSoup) -> Dict[str, str]:
        """
        Extract case details from HTML using multiple parsing strategies
        """
        details = {}
        
        # Strategy 1: Look for labeled data in tables
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    label = clean_text(cells[0].get_text())
                    value = clean_text(cells[1].get_text())
                    
                    if label and value and len(value) > 1:
                        details.update(self._map_field(label, value))
        
        # Strategy 2: Look for patterns in text
        text_content = soup.get_text()
        patterns = {
            'petitioner': [
                r'petitioner[:\s]*(.+?)(?:\n|vs?\.|respondent)',
                r'appellant[:\s]*(.+?)(?:\n|vs?\.|respondent)'
            ],
            'respondent': [
                r'respondent[:\s]*(.+?)(?:\n|petitioner|appellant)',
                r'vs?\.\s*(.+?)(?:\n|court|judge)'
            ],
            'filing_date': [
                r'filing\s+date[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
                r'filed\s+on[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{4})'
            ],
            'hearing_date': [
                r'next\s+hearing[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
                r'next\s+date[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{4})'
            ],
            'status': [
                r'status[:\s]*(.+?)(?:\n|date|court)',
                r'stage[:\s]*(.+?)(?:\n|date|court)'
            ],
            'judge': [
                r'(?:hon\'?ble\s+)?justice\s+(.+?)(?:\n|court|date)',
                r'before[:\s]*(?:hon\'?ble\s+)?(.+?)(?:\n|court|date)'
            ]
        }
        
        for field, field_patterns in patterns.items():
            if field not in details:
                for pattern in field_patterns:
                    match = re.search(pattern, text_content, re.IGNORECASE | re.DOTALL)
                    if match:
                        details[field] = clean_text(match.group(1))
                        break
        
        return details

    def _map_field(self, label: str, value: str) -> Dict[str, str]:
        """
        Map extracted labels to standard field names
        """
        label_lower = label.lower()
        field_mapping = {}
        
        # Map various label formats to standard fields
        if any(term in label_lower for term in ['petitioner', 'appellant', 'plaintiff']):
            field_mapping['petitioner'] = value
        elif any(term in label_lower for term in ['respondent', 'defendant']):
            field_mapping['respondent'] = value
        elif any(term in label_lower for term in ['filing', 'filed', 'registration']):
            field_mapping['filing_date'] = value
        elif any(term in label_lower for term in ['next', 'hearing', 'date']):
            field_mapping['hearing_date'] = value
        elif any(term in label_lower for term in ['status', 'stage']):
            field_mapping['status'] = value
        elif any(term in label_lower for term in ['judge', 'justice', 'court']):
            field_mapping['judge'] = value
        elif any(term in label_lower for term in ['title', 'case']):
            field_mapping['case_title'] = value
        
        return field_mapping

    def _extract_pdf_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """
        Extract PDF document links from the page
        """
        pdf_links = []
        
        # Look for PDF links
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link['href']
            text = clean_text(link.get_text())
            
            # Check if it's a PDF link
            is_pdf = (
                '.pdf' in href.lower() or
                'pdf' in text.lower() or
                any(term in text.lower() for term in ['order', 'judgment', 'judgement', 'document'])
            )
            
            if is_pdf and text:
                # Convert relative URLs to absolute
                if href.startswith('/'):
                    full_url = urljoin(base_url, href)
                elif not href.startswith('http'):
                    full_url = urljoin(base_url, href)
                else:
                    full_url = href
                
                doc_type = 'document'
                if 'order' in text.lower():
                    doc_type = 'order'
                elif any(term in text.lower() for term in ['judgment', 'judgement']):
                    doc_type = 'judgment'
                elif 'notice' in text.lower():
                    doc_type = 'notice'
                
                pdf_links.append({
                    'title': text,
                    'url': full_url,
                    'type': doc_type
                })
        
        return pdf_links[:5]  # Limit to 5 documents

    def _alternative_search_approach(self, page, case_type: str, case_number: str, filing_year: str) -> Dict[str, Any]:
        """
        Alternative approach when main form is not found
        """
        try:
            # Try to find any input fields and fill them
            inputs = page.locator('input[type="text"]').all()
            
            if len(inputs) >= 2:
                # Assume first input is case number, second is year
                inputs[0].fill(case_number)
                inputs[1].fill(filing_year)
                
                # Look for submit button
                page.locator('input[type="submit"], button').first.click()
                page.wait_for_load_state('networkidle')
                
                return {'success': True}
            
            return {
                'success': False,
                'message': 'Could not locate search form elements'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Alternative search failed: {str(e)}'
            }

    def _fallback_mock_search(self, case_type: str, case_number: str, filing_year: str) -> Dict[str, Any]:
        """
        Fallback to mock data when Playwright is not available or fails
        """
        self.logger.warning("Using fallback mock data - install Playwright for real scraping")
        
        time.sleep(2)  # Simulate processing time
        
        mock_data = {
            'case_type': case_type,
            'case_number': case_number,
            'filing_year': filing_year,
            'case_title': f'{case_type} {case_number}/{filing_year} - Sample Case vs State of Delhi (MOCK DATA)',
            'petitioner': 'Sample Petitioner Name',
            'respondent': 'State of Delhi & Others',
            'filing_date': '15/01/2023',
            'hearing_date': '25/12/2025',
            'status': 'Pending (MOCK)',
            'judge': 'Hon\'ble Justice Sample Singh',
            'court_name': 'Delhi High Court',
            'act': 'Article 226 of Constitution of India',
            'stage': 'Arguments',
            'pdf_links': [
                {
                    'title': f'Order dated 15/01/2023 - {case_type} {case_number}/{filing_year} (MOCK)',
                    'url': 'https://example.com/mock-order.pdf',
                    'type': 'order'
                }
            ]
        }
        
        save_case_data(mock_data)
        
        return {
            'success': True,
            'data': mock_data,
            'message': 'Case details retrieved successfully (MOCK DATA - Install Playwright for real scraping)'
        }