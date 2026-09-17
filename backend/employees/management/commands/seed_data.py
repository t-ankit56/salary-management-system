import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from faker import Faker

from accounts.models import User
from employees.models import Country, Department, Employee, Role
from employees.services import create_employee, deactivate_employee
from salary.models import SalaryPeriod
from salary.services import correct_salary_period, record_salary_change

DEMO_EMPLOYEE_COUNT = 4

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

            _seed_demo_cases(departments[0], roles[0], countries[0], today)

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(departments)} departments, {len(roles)} roles, "
                f"{len(countries)} countries, {count} employees, "
                f"{DEMO_EMPLOYEE_COUNT} demo cases (DEMO001-{DEMO_EMPLOYEE_COUNT:03d})."
            )
        )


def _seed_demo_cases(department: Department, role: Role, country: Country, today) -> None:
    demo_user, _ = User.objects.get_or_create(
        email="seed-demo@example.com", defaults={"is_staff": False}
    )
    demo_user.set_unusable_password()
    demo_user.save()

    common = {"department": department, "role": role, "country": country}

    full_history_hire_date = today - timedelta(days=365 * 5)
    full_history = create_employee(
        employee_code="DEMO001",
        first_name="Demo",
        last_name="FullHistory",
        email="demo.fullhistory@example.com",
        hire_date=full_history_hire_date,
        base=Decimal(60000),
        allowance=Decimal(2000),
        yearly_bonus=Decimal(5000),
        salary_effective_from=full_history_hire_date,
        **common,
    )
    for years_ago in (4, 3, 2, 1):
        record_salary_change(
            employee=full_history,
            base=Decimal(60000) + Decimal(years_ago) * Decimal(5000),
            allowance=Decimal(2000),
            yearly_bonus=Decimal(5000) + Decimal(years_ago) * Decimal(1000),
            effective_from=today - timedelta(days=365 * years_ago),
        )

    future_raise_hire_date = today - timedelta(days=365 * 2)
    future_raise = create_employee(
        employee_code="DEMO002",
        first_name="Demo",
        last_name="FutureRaise",
        email="demo.futureraise@example.com",
        hire_date=future_raise_hire_date,
        base=Decimal(70000),
        allowance=Decimal(1500),
        yearly_bonus=Decimal(4000),
        salary_effective_from=future_raise_hire_date,
        **common,
    )
    record_salary_change(
        employee=future_raise,
        base=Decimal(85000),
        allowance=Decimal(2000),
        yearly_bonus=Decimal(6000),
        effective_from=today + timedelta(days=30),
    )

    corrected_hire_date = today - timedelta(days=365 * 3)
    corrected = create_employee(
        employee_code="DEMO003",
        first_name="Demo",
        last_name="Correction",
        email="demo.correction@example.com",
        hire_date=corrected_hire_date,
        base=Decimal(50000),
        allowance=Decimal(1000),
        yearly_bonus=Decimal(3000),
        salary_effective_from=corrected_hire_date,
        **common,
    )
    open_period = SalaryPeriod.objects.get(employee=corrected, effective_to__isnull=True)
    correct_salary_period(
        salary_period=open_period,
        base=Decimal(52000),
        allowance=Decimal(1000),
        yearly_bonus=Decimal(3000),
        reason="Payroll entry error at hire — base salary was recorded incorrectly.",
        created_by=demo_user,
    )

    deactivated_hire_date = today - timedelta(days=365 * 4)
    deactivated = create_employee(
        employee_code="DEMO004",
        first_name="Demo",
        last_name="Deactivated",
        email="demo.deactivated@example.com",
        hire_date=deactivated_hire_date,
        base=Decimal(65000),
        allowance=Decimal(1000),
        yearly_bonus=Decimal(2000),
        salary_effective_from=deactivated_hire_date,
        **common,
    )
    deactivate_employee(employee=deactivated, effective_date=today - timedelta(days=90))
