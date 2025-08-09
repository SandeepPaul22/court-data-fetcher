# Court Data Fetcher & Mini-Dashboard

A comprehensive web application for fetching and displaying Indian court case metadata and orders/judgments from Delhi High Court.

![Court Data Fetcher](https://img.shields.io/badge/Court-Data%20Fetcher-blue) ![Python](https://img.shields.io/badge/Python-3.9+-brightgreen) ![Flask](https://img.shields.io/badge/Flask-2.3+-orange) ![License](https://img.shields.io/badge/License-MIT-green)

## 🎯 Overview

This project implements a robust court case data fetching system that automatically scrapes case information from Delhi High Court's website. It features advanced CAPTCHA bypassing, comprehensive data storage, and a beautiful web interface.

## 🏗️ Project Structure

```
court-data-fetcher/
├── app.py                  # Main Flask application entry point
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── README.md             # Project documentation
├── LICENSE               # MIT License file
├── .gitignore            # Git ignore patterns
├── setup.py              # Package setup configuration
├── court_scraper/        # Main application package
│   ├── __init__.py
│   ├── models.py         # Database models
│   ├── scraper.py        # Web scraping logic
│   ├── database.py       # Database operations
│   ├── forms.py          # Flask forms
│   └── utils.py          # Utility functions
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── search.html
│   ├── results.html
│   └── error.html
├── static/               # Static assets
│   ├── css/style.css
│   ├── js/main.js
│   └── images/
├── tests/                # Test files
├── data/                 # Database and data files
└── .github/workflows/    # CI/CD workflows
```

## 🎯 Features

- **🏛️ Court Integration**: Direct integration with Delhi High Court
- **🔍 Advanced Search**: Multiple search options (Case Type, Number, Year)
- **🤖 CAPTCHA Handling**: Automatic anti-bot detection bypass
- **💾 Data Storage**: SQLite database for query logging and caching
- **📄 PDF Downloads**: Direct links to orders/judgments
- **🚨 Error Handling**: Comprehensive error handling with user-friendly messages
- **📱 Responsive UI**: Beautiful, mobile-friendly interface
- **🔗 RESTful API**: Full API access for developers
- **📊 Analytics**: Search history and usage statistics
- **🐳 Docker Ready**: Containerized deployment support

## 🛠️ Tech Stack

- **Backend**: Python 3.9+, Flask 2.3+
- **Database**: SQLite3
- **Web Scraping**: Selenium WebDriver, BeautifulSoup4
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Containerization**: Docker
- **Testing**: pytest, pytest-flask

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Chrome/Chromium browser
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/court-data-fetcher.git
   cd court-data-fetcher
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables**
   ```bash
   # Create .env file
   cp .env.example .env
   
   # Edit .env with your configuration
   export FLASK_APP=app.py
   export FLASK_ENV=development
   export SECRET_KEY=your-secret-key-here
   ```

5. **Initialize database**
   ```bash
   python -c "from court_scraper.database import init_db; init_db()"
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Access the application**
   Open http://localhost:5000 in your browser

## 🐳 Docker Deployment

### Build and Run

```bash
# Build the image
docker build -t court-data-fetcher .

# Run the container
docker run -p 5000:5000 court-data-fetcher
```

### Docker Compose (Recommended)

```yaml
version: '3.8'
services:
  court-app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=your-production-secret-key
    volumes:
      - ./data:/app/data
```

Run with:
```bash
docker-compose up -d
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Environment (development/production) | `development` |
| `SECRET_KEY` | Flask secret key | `dev-secret-key` |
| `DATABASE_PATH` | Database file path | `data/court_data.db` |
| `SELENIUM_TIMEOUT` | Selenium timeout in seconds | `30` |
| `CAPTCHA_SERVICE_KEY` | 2captcha service API key | `` |

### Court Configuration

The application is configured for **Delhi High Court** by default. Key settings:

- **Target Court**: Delhi High Court (delhihighcourt.nic.in)
- **Supported Case Types**: CWP, CRL, FAO, MAC, CS, CM, CRM, SA, RFA, CRL.A, BAIL, ARB
- **Search Methods**: Case Type + Number + Year

## 🎯 CAPTCHA Bypass Strategy

Our multi-layered approach to handle CAPTCHAs:

1. **Undetected ChromeDriver**: Uses undetected-chromedriver to avoid basic detection
2. **Human Behavior Simulation**: Random delays and mouse movements
3. **Session Management**: Maintains cookies and session state
4. **2captcha Integration**: Fallback to human CAPTCHA solving service
5. **Manual Override**: Option for manual CAPTCHA entry during development

### CAPTCHA Service Setup (Optional)

For production environments, integrate with 2captcha:

1. Sign up at [2captcha.com](https://2captcha.com)
2. Get your API key
3. Set the `CAPTCHA_SERVICE_KEY` environment variable

## 📊 API Documentation

### Endpoints

#### POST /api/search
Search for court cases

**Request:**
```json
{
    "case_type": "CWP",
    "case_number": "123",
    "filing_year": "2023"
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "Case Title": "Sample vs State",
        "Petitioner": "John Sample",
        "Respondent": "State of Delhi",
        "Filing Date": "2023-01-15",
        "Status": "Pending"
    }
}
```

#### GET /health
Check API status

**Response:**
```json
{
    "status": "healthy",
    "timestamp": "2023-12-07T10:00:00Z",
    "version": "1.0.0"
}
```

## 🧪 Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-flask pytest-cov

# Run tests
pytest

# Run with coverage
pytest --cov=court_scraper

# Run specific test file
pytest tests/test_scraper.py -v
```

### Test Coverage

The test suite covers:
- ✅ Web scraping functionality
- ✅ Database operations
- ✅ Form validation
- ✅ API endpoints
- ✅ Utility functions
- ✅ Error handling

## 🚦 Development

### Setup Development Environment

1. **Install development dependencies**
   ```bash
   pip install -r requirements.txt
   pip install black flake8 isort pytest-cov
   ```

2. **Code formatting**
   ```bash
   black .
   isort .
   flake8 .
   ```

3. **Run in debug mode**
   ```bash
   export FLASK_ENV=development
   export FLASK_DEBUG=1
   python app.py
   ```

### Contributing Guidelines

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📁 Data Storage

The application stores data in SQLite database with the following tables:

- **cases**: Case information and metadata
- **search_logs**: Search query history and performance metrics
- **raw_responses**: Raw HTML responses for debugging
- **pdf_documents**: PDF document references and metadata

## 🔒 Security Features

- **Input Validation**: Comprehensive form and API input validation
- **SQL Injection Protection**: Parameterized queries
- **CSRF Protection**: Flask-WTF CSRF tokens
- **Rate Limiting**: Built-in request rate limiting
- **Secure Headers**: Security headers for XSS protection
- **Environment Variables**: Sensitive configuration via env vars

## 📈 Performance

- **Caching**: Database caching for repeated searches
- **Asynchronous Processing**: Non-blocking request handling
- **Connection Pooling**: Efficient database connections
- **Static Asset Optimization**: Minified CSS/JS
- **Docker Optimization**: Multi-stage builds for smaller images

## 🐛 Troubleshooting

### Common Issues

**Chrome/ChromeDriver Issues:**
```bash
# Update ChromeDriver
pip install --upgrade webdriver-manager
```

**Database Lock Issues:**
```bash
# Reset database
rm data/court_data.db
python -c "from court_scraper.database import init_db; init_db()"
```

**CAPTCHA Failures:**
- Check Chrome browser version compatibility
- Verify 2captcha API key
- Enable debug logging for detailed error information

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
python app.py
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Delhi High Court** for providing public access to case information
- **Selenium WebDriver** for browser automation capabilities
- **Flask Framework** for the robust web framework
- **Bootstrap** for the responsive UI components
- **2captcha** for CAPTCHA solving services

## 📞 Support

For support and questions:

- **Issues**: [GitHub Issues](https://github.com/yourusername/court-data-fetcher/issues)
- **Documentation**: [Wiki](https://github.com/yourusername/court-data-fetcher/wiki)
- **Email**: support@court-data-fetcher.com

## 🗺️ Roadmap

### Upcoming Features

- [ ] **Multiple Court Support**: Extend to other High Courts
- [ ] **Advanced Analytics**: Search patterns and case statistics
- [ ] **Email Notifications**: Case update notifications
- [ ] **Bulk Operations**: Batch case searches
- [ ] **Export Features**: CSV/Excel export functionality
- [ ] **Mobile App**: React Native mobile application
- [ ] **Machine Learning**: Predictive case outcome analysis

### Version History

- **v1.0.0**: Initial release with Delhi High Court support
- **v1.1.0**: CAPTCHA bypass improvements (Coming Soon)
- **v2.0.0**: Multi-court support (Planned)

---

**⭐ Star this repository if you find it helpful!**

**🐛 Found a bug? [Report it here](https://github.com/yourusername/court-data-fetcher/issues)**

**💡 Have a feature request? [Let us know!](https://github.com/yourusername/court-data-fetcher/discussions)**