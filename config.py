import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() in ['true', '1', 'on']
    
    # Database
    DATABASE_PATH = os.environ.get('DATABASE_PATH', 'data/court_data.db')
    
    # Court Settings
    TARGET_COURT = os.environ.get('TARGET_COURT', 'delhi_high_court')
    COURT_URL = os.environ.get('COURT_URL', 'https://delhihighcourt.nic.in')
    
    # Selenium Settings
    SELENIUM_TIMEOUT = int(os.environ.get('SELENIUM_TIMEOUT', 30))
    CHROME_HEADLESS = os.environ.get('CHROME_HEADLESS', 'True').lower() == 'true'
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Supported case types
    CASE_TYPES = [
        ('CWP', 'Civil Writ Petition'),
        ('CRL', 'Criminal Writ Petition'),
        ('FAO', 'First Appeal from Order'),
        ('MAC', 'Motor Accident Claims'),
        ('CS', 'Civil Suit'),
        ('CM', 'Civil Miscellaneous'),
        ('CRM', 'Criminal Miscellaneous'),
        ('SA', 'Second Appeal'),
        ('RFA', 'Regular First Appeal'),
        ('CRL.A', 'Criminal Appeal'),
        ('BAIL', 'Bail Application'),
        ('ARB', 'Arbitration Petition')
    ]

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-must-set-a-secret-key'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
