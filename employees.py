"""
Refactored Employee Management System
Following the architectural proposal from the Google Doc
"""

import os
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


# =============================================================================
# DOMAIN MODELS
# =============================================================================

class EmployeeType(Enum):
    SALARIED = "salaried"
    HOURLY = "hourly"
    FREELANCER = "freelancer"


class Role(Enum):
    INTERN = "intern"
    MANAGER = "manager"
    VICE_PRESIDENT = "vice_president"


@dataclass
class Project:
    """Project for freelancer employees."""
    name: str
    amount: float
    delivered: bool = False


@dataclass
class Employee:
    """Base employee following the domain model specification."""
    name: str
    role: Role
    employee_type: EmployeeType
    vacation_days: int = 25
    salary: Optional[float] = None
    hourly_rate: Optional[float] = None
    hours_worked: Optional[int] = None
    projects: List[Project] = field(default_factory=list)

    def add_project(self, project: Project):
        """Add project for freelancer employees."""
        self.projects.append(project)

    def get_delivered_projects(self) -> List[Project]:
        """Get all delivered projects."""
        return [p for p in self.projects if p.delivered]


@dataclass
class Freelancer(Employee):
    """Specific freelancer employee type."""

    def __post_init__(self):
        self.employee_type = EmployeeType.FREELANCER


# =============================================================================
# STRATEGY PATTERN - Payment Strategies
# =============================================================================

class PaymentStrategy(ABC):
    """Abstract strategy for payment calculation."""

    @abstractmethod
    def calculate_payment(self, employee: Employee) -> float:
        """Calculate payment for employee."""
        pass


class SalariedPayment(PaymentStrategy):
    """Payment strategy for salaried employees."""

    def calculate_payment(self, employee: Employee) -> float:
        return employee.salary


class HourlyPayment(PaymentStrategy):
    """Payment strategy for hourly employees."""

    def calculate_payment(self, employee: Employee) -> float:
        return employee.hourly_rate * employee.hours_worked


class FreelancePayment(PaymentStrategy):
    """Payment strategy for freelancer employees."""

    def calculate_payment(self, employee: Employee) -> float:
        delivered_projects = employee.get_delivered_projects()
        return sum(project.amount for project in delivered_projects)


# =============================================================================
# STRATEGY PATTERN - Vacation Policies
# =============================================================================

class VacationPolicy(ABC):
    """Abstract strategy for vacation policies."""

    @abstractmethod
    def calculate_vacation_days(self, employee: Employee) -> int:
        """Calculate available vacation days."""
        pass

    @abstractmethod
    def can_take_vacation(self, employee: Employee, days: int) -> bool:
        """Check if employee can take vacation days."""
        pass

    @abstractmethod
    def can_payout_vacation(self, employee: Employee, days: int) -> bool:
        """Check if employee can get vacation payout."""
        pass


class BasicVacation(VacationPolicy):
    """Basic vacation policy - standard rules."""

    def calculate_vacation_days(self, employee: Employee) -> int:
        return employee.vacation_days

    def can_take_vacation(self, employee: Employee, days: int) -> bool:
        return employee.vacation_days >= days

    def can_payout_vacation(self, employee: Employee, days: int) -> bool:
        return employee.vacation_days >= days and days <= 5


class ManagerVacation(VacationPolicy):
    """Vacation policy for managers - up to 10 days payout."""

    def calculate_vacation_days(self, employee: Employee) -> int:
        return employee.vacation_days

    def can_take_vacation(self, employee: Employee, days: int) -> bool:
        return employee.vacation_days >= days

    def can_payout_vacation(self, employee: Employee, days: int) -> bool:
        return employee.vacation_days >= days and days <= 10


class VPVacation(VacationPolicy):
    """Vacation policy for VPs - unlimited vacations, max 5 days per request."""

    def calculate_vacation_days(self, employee: Employee) -> int:
        return float('inf')  # Unlimited

    def can_take_vacation(self, employee: Employee, days: int) -> bool:
        return days <= 5

    def can_payout_vacation(self, employee: Employee, days: int) -> bool:
        return days <= 5


class InternVacation(VacationPolicy):
    """Vacation policy for interns - no vacations allowed."""

    def calculate_vacation_days(self, employee: Employee) -> int:
        return 0

    def can_take_vacation(self, employee: Employee, days: int) -> bool:
        return False

    def can_payout_vacation(self, employee: Employee, days: int) -> bool:
        return False


class HourlyVacation(VacationPolicy):
    """Vacation policy for hourly employees."""

    def calculate_vacation_days(self, employee: Employee) -> int:
        return employee.vacation_days

    def can_take_vacation(self, employee: Employee, days: int) -> bool:
        return employee.vacation_days >= days

    def can_payout_vacation(self, employee: Employee, days: int) -> bool:
        return employee.vacation_days >= days and days <= 5


# =============================================================================
# FACTORY PATTERN - Strategy Creation
# =============================================================================

class StrategyFactory:
    """Factory for creating strategies as specified in the document."""

    @staticmethod
    def create_payment_strategy(employee_type: EmployeeType) -> PaymentStrategy:
        """Create payment strategy based on employee type."""
        if employee_type == EmployeeType.SALARIED:
            return SalariedPayment()
        elif employee_type == EmployeeType.HOURLY:
            return HourlyPayment()
        elif employee_type == EmployeeType.FREELANCER:
            return FreelancePayment()
        else:
            raise ValueError(f"Unknown employee type: {employee_type}")

    @staticmethod
    def create_vacation_policy(role: Role, employee_type: EmployeeType) -> VacationPolicy:
        """Create vacation policy based on role and type."""
        if role == Role.INTERN:
            return InternVacation()
        elif role == Role.MANAGER:
            return ManagerVacation()
        elif role == Role.VICE_PRESIDENT:
            return VPVacation()
        elif employee_type == EmployeeType.HOURLY:
            return HourlyVacation()
        else:
            return BasicVacation()


# =============================================================================
# FACTORY PATTERN - Employee Creation
# =============================================================================

class EmployeeFactory:
    """Factory for creating employees with appropriate strategies."""

    @staticmethod
    def create_employee(data: dict) -> Employee:
        """Create employee based on provided data."""
        name = data["name"]
        role = Role(data["role"])
        employee_type = EmployeeType(data["type"])

        if employee_type == EmployeeType.SALARIED:
            return Employee(
                name=name,
                role=role,
                employee_type=employee_type,
                salary=data["salary"]
            )
        elif employee_type == EmployeeType.HOURLY:
            return Employee(
                name=name,
                role=role,
                employee_type=employee_type,
                hourly_rate=data["hourly_rate"],
                hours_worked=data["hours_worked"]
            )
        elif employee_type == EmployeeType.FREELANCER:
            return Freelancer(
                name=name,
                role=role,
                employee_type=employee_type
            )
        else:
            raise ValueError(f"Unknown employee type: {employee_type}")


# =============================================================================
# OPERATION LOG - Audit System
# =============================================================================

class OperationLog:
    """Centralized operation logging system as specified."""

    _operations: List[Dict[str, Any]] = []

    @classmethod
    def record(cls, operation: str, employee_name: str = None, amount: float = None, details: str = None):
        """Record an operation in the audit log."""
        log_entry = {
            "timestamp": datetime.now(),
            "operation": operation,
            "employee_name": employee_name,
            "amount": amount,
            "details": details
        }
        cls._operations.append(log_entry)

    @classmethod
    def get_operations(cls, employee_name: str = None) -> List[Dict[str, Any]]:
        """Get operations, optionally filtered by employee."""
        if employee_name:
            return [op for op in cls._operations if op["employee_name"] == employee_name]
        return cls._operations.copy()

    @classmethod
    def clear_log(cls):
        """Clear all operations (for testing)."""
        cls._operations.clear()


# =============================================================================
# COMMAND PATTERN - Operations with Audit
# =============================================================================

class PayEmployeeCommand:
    """Command to pay an employee with audit logging."""

    def __init__(self, employee: Employee, payment_strategy: PaymentStrategy, config: Dict[str, Any]):
        self.employee = employee
        self.payment_strategy = payment_strategy
        self.config = config

    def execute(self) -> float:
        """Execute payment and log operation."""
        base_payment = self.payment_strategy.calculate_payment(self.employee)
        bonus = self._calculate_bonus(base_payment)
        total_payment = base_payment + bonus

        details = f"Base: ${base_payment:.2f}"
        if bonus > 0:
            details += f", Bonus: ${bonus:.2f}"

        OperationLog.record(
            operation="PAYMENT",
            employee_name=self.employee.name,
            amount=total_payment,
            details=details
        )

        return total_payment

    def _calculate_bonus(self, base_payment: float) -> float:
        """Calculate performance bonus based on role and type."""
        if self.employee.role == Role.INTERN:
            return 0.0

        if self.employee.employee_type == EmployeeType.SALARIED:
            return base_payment * self.config.get("salaried_bonus_percentage", 0.1)
        elif self.employee.employee_type == EmployeeType.HOURLY:
            threshold = self.config.get("hourly_bonus_threshold", 160)
            bonus_amount = self.config.get("hourly_bonus_amount", 100)
            return bonus_amount if self.employee.hours_worked > threshold else 0.0

        return 0.0


class GrantVacationCommand:
    """Command to grant vacation with audit logging."""

    def __init__(self, employee: Employee, vacation_policy: VacationPolicy, days: int, payout: bool = False):
        self.employee = employee
        self.vacation_policy = vacation_policy
        self.days = days
        self.payout = payout

    def execute(self):
        """Execute vacation grant and log operation."""
        if self.payout:
            if not self.vacation_policy.can_payout_vacation(self.employee, self.days):
                raise ValueError(f"Cannot payout {self.days} vacation days for {self.employee.name}")

            if self.employee.role != Role.VICE_PRESIDENT:
                self.employee.vacation_days -= self.days

            OperationLog.record(
                operation="VACATION_PAYOUT",
                employee_name=self.employee.name,
                amount=self.days,
                details=f"Paid out {self.days} vacation days"
            )
        else:
            if not self.vacation_policy.can_take_vacation(self.employee, self.days):
                raise ValueError(f"Cannot take {self.days} vacation days for {self.employee.name}")

            if self.employee.role != Role.VICE_PRESIDENT:
                self.employee.vacation_days -= self.days

            OperationLog.record(
                operation="VACATION_TAKEN",
                employee_name=self.employee.name,
                amount=self.days,
                details=f"Took {self.days} vacation days"
            )


# =============================================================================
# SERVICES LAYER
# =============================================================================

class PayrollService:
    """Service for payroll operations."""

    def __init__(self, config_manager):
        self.config_manager = config_manager

    def pay_employee(self, employee: Employee) -> float:
        """Pay an employee using strategy pattern."""
        payment_strategy = StrategyFactory.create_payment_strategy(employee.employee_type)
        command = PayEmployeeCommand(employee, payment_strategy, self.config_manager.get_config())
        return command.execute()

    def pay_all_employees(self, employees: List[Employee]) -> Dict[str, float]:
        """Pay all employees and return payment summary."""
        payments = {}
        for employee in employees:
            payments[employee.name] = self.pay_employee(employee)
        return payments


class VacationService:
    """Service for vacation operations."""

    def grant_vacation(self, employee: Employee, days: int, payout: bool = False):
        """Grant vacation to employee."""
        vacation_policy = StrategyFactory.create_vacation_policy(employee.role, employee.employee_type)
        command = GrantVacationCommand(employee, vacation_policy, days, payout)
        command.execute()


# =============================================================================
# CONFIGURATION MANAGEMENT
# =============================================================================

class ConfigurationManager:
    """Manages dynamic configuration for business rules."""

    DEFAULT_CONFIG = {
        "salaried_bonus_percentage": 0.1,
        "hourly_bonus_threshold": 160,
        "hourly_bonus_amount": 100
    }

    def __init__(self, config_file: str = "payroll_config.json"):
        self.config_file = config_file
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self.DEFAULT_CONFIG.copy()

    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        return self._config.copy()

    def update_config(self, updates: Dict[str, Any]):
        """Update configuration and save to file."""
        self._config.update(updates)
        with open(self.config_file, 'w') as f:
            json.dump(self._config, f, indent=2)


# =============================================================================
# COMPANY MANAGEMENT
# =============================================================================

class Company:
    """Main company class with separated responsibilities."""

    def __init__(self):
        self.employees: List[Employee] = []
        self.config_manager = ConfigurationManager()
        self.payroll_service = PayrollService(self.config_manager)
        self.vacation_service = VacationService()

    def add_employee(self, employee_data: Dict[str, Any]) -> Employee:
        """Add employee to company."""
        employee = EmployeeFactory.create_employee(employee_data)
        self.employees.append(employee)
        return employee

    def find_employees_by_role(self, role: Role) -> List[Employee]:
        """Find employees by role using unified method."""
        return [emp for emp in self.employees if emp.role == role]

    def find_employees_by_type(self, employee_type: EmployeeType) -> List[Employee]:
        """Find employees by type."""
        return [emp for emp in self.employees if emp.employee_type == employee_type]

    def pay_all_employees(self) -> Dict[str, float]:
        """Pay all employees using payroll service."""
        return self.payroll_service.pay_all_employees(self.employees)

    def grant_vacation_to_employee(self, employee: Employee, days: int, payout: bool = False):
        """Grant vacation using vacation service."""
        self.vacation_service.grant_vacation(employee, days, payout)

    def add_project_to_freelancer(self, employee: Employee, project_name: str, amount: float):
        """Add project to freelancer employee."""
        if employee.employee_type != EmployeeType.FREELANCER:
            raise ValueError("Only freelancers can have projects")

        project = Project(name=project_name, amount=amount, delivered=True)
        employee.add_project(project)

    def get_employee_history(self, employee: Employee) -> List[Dict[str, Any]]:
        """Get operation history for employee."""
        return OperationLog.get_operations(employee.name)


# =============================================================================
# USER INTERFACE LAYER
# =============================================================================

class EmployeeManagementUI:
    """Presentation layer completely separated from business logic."""

    def __init__(self):
        self.company = Company()

    def clear_screen(self):
        """Clear console screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_menu(self):
        """Display main menu."""
        print("--- Employee Management Menu ---")
        print("1. Create employee")
        print("2. View employees")
        print("3. Grant vacation to an employee")
        print("4. Pay employees")
        print("5. Add project (Freelancers)")
        print("6. View employee history")
        print("7. Update payroll configuration")
        print("8. Exit")

    def create_employee_menu(self):
        """Handle employee creation."""
        try:
            name = input("Employee name: ")

            print("Available roles: intern, manager, vice_president")
            role = input("Role: ").lower()

            print("Available types: salaried, hourly, freelancer")
            emp_type = input("Employee type: ").lower()

            employee_data = {
                "name": name,
                "role": role,
                "type": emp_type
            }

            if emp_type == "salaried":
                salary = float(input("Monthly salary: "))
                employee_data["salary"] = salary
            elif emp_type == "hourly":
                rate = float(input("Hourly rate: "))
                hours = int(input("Hours worked: "))
                employee_data["hourly_rate"] = rate
                employee_data["hours_worked"] = hours

            employee = self.company.add_employee(employee_data)
            print(f"Employee {employee.name} created successfully.")

        except (ValueError, KeyError) as e:
            print(f"Error creating employee: {e}")

        input("Press Enter to continue...")

    def view_employees_menu(self):
        """Handle employee viewing."""
        while True:
            self.clear_screen()
            print("--- View Employees Submenu ---")
            print("1. View managers")
            print("2. View interns")
            print("3. View vice presidents")
            print("4. View freelancers")
            print("0. Return to main menu")

            choice = input("Select an option: ")

            if choice == "1":
                employees = self.company.find_employees_by_role(Role.MANAGER)
            elif choice == "2":
                employees = self.company.find_employees_by_role(Role.INTERN)
            elif choice == "3":
                employees = self.company.find_employees_by_role(Role.VICE_PRESIDENT)
            elif choice == "4":
                employees = self.company.find_employees_by_type(EmployeeType.FREELANCER)
            elif choice == "0":
                break
            else:
                print("Invalid option.")
                input("Press Enter to continue...")
                continue

            self._display_employees(employees)
            input("Press Enter to continue...")

    def _display_employees(self, employees: List[Employee]):
        """Display list of employees."""
        if not employees:
            print("No employees found.")
            return

        for emp in employees:
            print(f"{emp.name} ({emp.role.value}) - {emp.employee_type.value} - {emp.vacation_days} vacation days")
            if emp.employee_type == EmployeeType.FREELANCER:
                delivered_projects = emp.get_delivered_projects()
                print(f"  Projects: {len(delivered_projects)}, Total value: ${sum(p.amount for p in delivered_projects):.2f}")

    def grant_vacation_menu(self):
        """Handle vacation granting."""
        if not self.company.employees:
            print("No employees available.")
            input("Press Enter to continue...")
            return

        print("Available employees:")
        for idx, emp in enumerate(self.company.employees):
            print(f"{idx}. {emp.name} ({emp.role.value}) - {emp.vacation_days} vacation days")

        try:
            idx = int(input("Select employee index: "))
            employee = self.company.employees[idx]

            days = int(input("Number of days: "))
            payout = input("Payout instead of time off? (y/n): ").lower() == "y"

            self.company.grant_vacation_to_employee(employee, days, payout)
            print(f"Vacation granted to {employee.name}. Remaining days: {employee.vacation_days}")

        except (IndexError, ValueError) as e:
            print(f"Error: {e}")

        input("Press Enter to continue...")

    def pay_employees_menu(self):
        """Handle employee payment."""
        payments = self.company.pay_all_employees()

        for employee_name, amount in payments.items():
            print(f"Paid {employee_name}: ${amount:.2f}")

        input("Press Enter to continue...")

    def add_project_menu(self):
        """Handle project addition for freelancers."""
        freelancers = self.company.find_employees_by_type(EmployeeType.FREELANCER)

        if not freelancers:
            print("No freelancers available.")
            input("Press Enter to continue...")
            return

        print("Available freelancers:")
        for idx, emp in enumerate(freelancers):
            print(f"{idx}. {emp.name}")

        try:
            idx = int(input("Select freelancer index: "))
            freelancer = freelancers[idx]

            project_name = input("Project name: ")
            amount = float(input("Project amount: "))

            self.company.add_project_to_freelancer(freelancer, project_name, amount)
            print(f"Project '{project_name}' added to {freelancer.name}.")

        except (IndexError, ValueError) as e:
            print(f"Error: {e}")

        input("Press Enter to continue...")

    def view_employee_history_menu(self):
        """Handle employee history viewing."""
        if not self.company.employees:
            print("No employees available.")
            input("Press Enter to continue...")
            return

        print("Available employees:")
        for idx, emp in enumerate(self.company.employees):
            print(f"{idx}. {emp.name}")

        try:
            idx = int(input("Select employee index: "))
            employee = self.company.employees[idx]

            history = self.company.get_employee_history(employee)

            if not history:
                print(f"No transaction history for {employee.name}.")
            else:
                print(f"\nTransaction history for {employee.name}:")
                for operation in history:
                    print(f"{operation['timestamp'].strftime('%Y-%m-%d %H:%M')} - "
                          f"{operation['operation']} - ${operation['amount']:.2f} - "
                          f"{operation['details']}")

        except (IndexError, ValueError) as e:
            print(f"Error: {e}")

        input("Press Enter to continue...")

    def update_config_menu(self):
        """Handle configuration updates."""
        config = self.company.config_manager.get_config()

        print("Current configuration:")
        for key, value in config.items():
            print(f"{key}: {value}")

        print("\nWhat would you like to update?")
        print("1. Salaried bonus percentage")
        print("2. Hourly bonus threshold")
        print("3. Hourly bonus amount")

        try:
            choice = int(input("Select option: "))

            if choice == 1:
                new_value = float(input("New salaried bonus percentage (0.1 = 10%): "))
                self.company.config_manager.update_config({"salaried_bonus_percentage": new_value})
            elif choice == 2:
                new_value = int(input("New hourly bonus threshold: "))
                self.company.config_manager.update_config({"hourly_bonus_threshold": new_value})
            elif choice == 3:
                new_value = float(input("New hourly bonus amount: "))
                self.company.config_manager.update_config({"hourly_bonus_amount": new_value})
            else:
                print("Invalid option.")
                input("Press Enter to continue...")
                return

            print("Configuration updated successfully.")

        except ValueError as e:
            print(f"Error: {e}")

        input("Press Enter to continue...")

    def run(self):
        """Main application loop."""
        while True:
            self.clear_screen()
            self.display_menu()

            choice = input("Select an option: ")

            if choice == "1":
                self.create_employee_menu()
            elif choice == "2":
                self.view_employees_menu()
            elif choice == "3":
                self.grant_vacation_menu()
            elif choice == "4":
                self.pay_employees_menu()
            elif choice == "5":
                self.add_project_menu()
            elif choice == "6":
                self.view_employee_history_menu()
            elif choice == "7":
                self.update_config_menu()
            elif choice == "8":
                print("Goodbye!")
                break
            else:
                print("Invalid option.")
                input("Press Enter to continue...")


# =============================================================================
# MAIN APPLICATION
# =============================================================================

def main():
    """Main application entry point."""
    app = EmployeeManagementUI()
    app.run()


if __name__ == "__main__":
    main()