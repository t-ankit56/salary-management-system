from django.contrib.postgres.fields import DateRangeField
from django.db.models import Func


class DateRangeFunc(Func):
    function = "daterange"
    output_field = DateRangeField()
