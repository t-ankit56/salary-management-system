import datetime


class ReportDateTooEarly(ValueError):
    def __init__(self, earliest_date: datetime.date):
        self.earliest_date = earliest_date
        super().__init__(f"No salary data available before {earliest_date}")


def total_payroll_cost(as_of: datetime.date | None = None) -> dict:
    pass


def headcount_by_department(as_of: datetime.date | None = None) -> dict:
    pass
