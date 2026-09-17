"""API view exposing every report under one dynamic ``/reports/{name}/`` route."""

from decimal import Decimal

from django.db.models import DateField
from django.http import Http404
from rest_framework.response import Response
from rest_framework.views import APIView

from reporting.services import (
    ReportDateTooEarly,
    average_bonus_by_department,
    average_salary_by_country,
    average_salary_by_department,
    headcount_by_country,
    headcount_by_department,
    total_payroll_cost,
)

REPORTS = {
    "total_payroll_cost": total_payroll_cost,
    "headcount_by_department": headcount_by_department,
    "average_salary_by_department": average_salary_by_department,
    "average_salary_by_country": average_salary_by_country,
    "average_bonus_by_department": average_bonus_by_department,
    "headcount_by_country": headcount_by_country,
}


def _stringify_decimals(value):
    if isinstance(value, Decimal):
        return str(value.quantize(Decimal("0.01")))
    if isinstance(value, dict):
        return {key: _stringify_decimals(v) for key, v in value.items()}
    return value


class ReportView(APIView):
    """Dispatches to one of ``REPORTS`` by name and stringifies money before responding."""

    def get(self, request, name):
        report_func = REPORTS.get(name)
        if report_func is None:
            raise Http404

        as_of = request.query_params.get("as_of")
        if as_of:
            as_of = DateField().to_python(as_of)

        try:
            result = report_func(as_of=as_of)
        except ReportDateTooEarly as exc:
            return Response(
                {"detail": str(exc), "earliest_available_date": exc.earliest_date},
                status=400,
            )

        return Response(_stringify_decimals(result))
