from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Regexp
from datetime import datetime

class SearchForm(FlaskForm):
    case_type = SelectField(
        'Case Type',
        choices=[
            ('', 'Select Case Type'),
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
        ],
        validators=[DataRequired(message="Please select a case type")],
        render_kw={"class": "form-select"}
    )
    
    case_number = StringField(
        'Case Number',
        validators=[
            DataRequired(message="Case number is required"),
            Length(min=1, max=50, message="Case number must be between 1 and 50 characters"),
            Regexp(r'^[A-Za-z0-9\/\-\s]+$', message="Invalid characters in case number")
        ],
        render_kw={
            "class": "form-control",
            "placeholder": "Enter case number (e.g., 123, 456/2023)",
            "autocomplete": "off"
        }
    )
    
    current_year = datetime.now().year
    filing_year = IntegerField(
        'Filing Year',
        validators=[
            DataRequired(message="Filing year is required"),
            NumberRange(min=1950, max=current_year + 1, 
                       message=f"Filing year must be between 1950 and {current_year + 1}")
        ],
        render_kw={
            "class": "form-control",
            "placeholder": f"Enter year (e.g., {current_year})",
            "min": "1950",
            "max": str(current_year + 1)
        }
    )
    
    submit = SubmitField(
        'Search Case',
        render_kw={"class": "btn btn-primary btn-lg"}
    )
