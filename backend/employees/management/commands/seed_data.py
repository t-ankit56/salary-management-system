import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from faker import Faker

from employees.models import Country, Department, Employee, Role
from employees.services import create_employee, deactivate_employee
from salary.services import record_salary_change

DEPARTMENTS = [
    "Engineering",
    "Sales",
    "Marketing",
    "Finance",
    "Human Resources",
    "Operations",
    "Legal",
    "Customer Support",
    "Product",
    "Design",
]

ROLES = [
    "Manager",
    "Senior Engineer",
    "Engineer",
    "Analyst",
    "Director",
    "Coordinator",
    "Specialist",
    "Associate",
    "Lead",
    "Consultant",
]

COUNTRY_COUNT = 8
DEACTIVATE_EVERY_NTH = 7
MIN_PERIOD_GAP_DAYS = 180


class Command(BaseCommand):
    help = "Seed reference data and employees with salary history for local development."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=200)

    def handle(self, *args, **options):
        count = options["count"]
        fake = Faker()
        today = timezone.localdate()

        with transaction.atomic():
            Employee.objects.all().delete()
            Department.objects.all().delete()
            Role.objects.all().delete()
            Country.objects.all().delete()

            departments = [Department.objects.create(name=name) for name in DEPARTMENTS]
            roles = [Role.objects.create(name=name) for name in ROLES]
            countries = [
                Country.objects.create(name=fake.unique.country()) for _ in range(COUNTRY_COUNT)
            ]

            for i in range(count):
                first_name = fake.first_name()
                last_name = fake.last_name()
                hire_date = fake.date_between(start_date="-8y", end_date="-1y")

                employee = create_employee(
                    employee_code=f"E{i + 1:05d}",
                    first_name=first_name,
                    last_name=last_name,
                    email=f"{first_name.lower()}.{last_name.lower()}{i + 1}@example.com",
                    department=random.choice(departments),
                    role=random.choice(roles),
                    country=random.choice(countries),
                    hire_date=hire_date,
                    base=Decimal(random.randrange(30_000, 150_000)),
                    allowance=Decimal(random.randrange(0, 10_000)),
                    yearly_bonus=Decimal(random.randrange(0, 20_000)),
                    salary_effective_from=hire_date,
                )

                period_start = hire_date
                for _ in range(random.randint(0, 2)):
                    earliest_next = period_start + timedelta(days=MIN_PERIOD_GAP_DAYS)
                    if earliest_next >= today:
                        break
                    next_date = fake.date_between(start_date=earliest_next, end_date=today)
                    record_salary_change(
                        employee=employee,
                        base=Decimal(random.randrange(30_000, 150_000)),
                        allowance=Decimal(random.randrange(0, 10_000)),
                        yearly_bonus=Decimal(random.randrange(0, 20_000)),
                        effective_from=next_date,
                    )
                    period_start = next_date

                if (i + 1) % DEACTIVATE_EVERY_NTH == 0:
                    earliest_deactivate = hire_date + timedelta(days=30)
                    if earliest_deactivate < today:
                        deactivate_date = fake.date_between(
                            start_date=earliest_deactivate, end_date=today
                        )
                        deactivate_employee(employee=employee, effective_date=deactivate_date)

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(departments)} departments, {len(roles)} roles, "
                f"{len(countries)} countries, {count} employees."
            )
        )
