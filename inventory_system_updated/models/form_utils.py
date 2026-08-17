from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask import request


def get_positive_int(form_key):
    try:
        value = int(request.form[form_key])
    except (KeyError, TypeError, ValueError):
        return None
    return value if value > 0 else None


def get_optional_positive_int(form_key):
    try:
        value = int(request.form.get(form_key, ''))
    except (TypeError, ValueError):
        return None
    return value if value > 0 else None


def get_money_amount(form_key):
    try:
        value = Decimal(request.form.get(form_key, '0') or '0')
    except (InvalidOperation, ValueError):
        return None
    return value if value >= 0 else None


def get_report_date_filters():
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()

    for date_value in (start_date, end_date):
        if date_value:
            try:
                datetime.strptime(date_value, '%Y-%m-%d')
            except ValueError:
                return start_date, end_date, 'Please enter valid report dates.'

    if start_date and end_date and start_date > end_date:
        return start_date, end_date, 'Start date cannot be after end date.'

    return start_date, end_date, None
