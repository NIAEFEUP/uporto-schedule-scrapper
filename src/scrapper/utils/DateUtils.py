from datetime import datetime

def get_scrapper_year():
    current_date = datetime.now()
    current_month = current_date.month
    current_year = current_date.year

    if current_month < 8:
        return current_year - 1

    return current_year
