from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ufcmsdb.models import Expense, CustomUser, Department, Role
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication


# Helper function to check user permissions
def has_permission(user, module, action):
    """
    Check if the user has permission for a specific module and action.
    """
    if not user or not user.role.exists():
        return False  # No role assigned
    
    # Get all roles assigned to the user
    user_roles = user.role.all()

    # Check if any assigned role has the required permission
    for role in user_roles:
        for permission in role.permissions.all():
            if permission.module == module and action in permission.action:
                return True
    return False


class GetAllExpenseView(APIView):
    """
    Retrieve all expenses.
    Only users with 'read' permission for 'financial_management' can access this.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not has_permission(request.user, "finance_management", "read"):
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

        expenses = Expense.objects.all()
        data = [
            {
                "id": expense.id,
                "date": expense.date,
                "amount": expense.amount,
                "description": expense.description,
                "user_id": expense.user.id,
                "user_name": expense.user.name,
                "department_id": expense.department.id,
                "department_name": expense.department.name,
                "user_role": ", ".join([role.name for role in expense.user.role.all()]),
                "expense_slip": expense.expense_slip.url if expense.expense_slip else None,
            }
            for expense in expenses
        ]
        return Response(data, status=status.HTTP_200_OK)


class AddExpenseView(APIView):
    """
    Create a new expense.
    Only users with 'create' permission for 'finance_management' can perform this action.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not has_permission(request.user, "finance_management", "create"):
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        required_fields = ['date', 'amount', 'description', 'user', 'department']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return Response(
                {"error": f"Missing required fields: {', '.join(missing_fields)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Validate date
            try:
                date = datetime.strptime(data['date'], "%Y-%m-%d").date()
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

            # Validate amount
            try:
                amount = float(data['amount'])
                if amount <= 0:
                    return Response({"error": "Amount must be greater than 0."}, status=status.HTTP_400_BAD_REQUEST)
            except ValueError:
                return Response({"error": "Amount must be a valid number."}, status=status.HTTP_400_BAD_REQUEST)

            # Validate user
            user = get_object_or_404(CustomUser, pk=data['user'])

            # Validate department
            department = get_object_or_404(Department, pk=data['department'])

            # Validate description length
            if len(data['description']) > 200:
                return Response({"error": "Description must be 200 characters or less."}, status=status.HTTP_400_BAD_REQUEST)

            # Handle optional expense_slip
            expense_slip = data.get('expense_slip', None)

            # Create the expense
            expense = Expense.objects.create(
                date=date,
                amount=amount,
                description=data['description'],
                user=user,
                department=department,
                expense_slip=expense_slip,
            )

            response_data = {
                "id": expense.id,
                "date": expense.date,
                "amount": expense.amount,
                "description": expense.description,
                "user_id": expense.user.id,
                "user_role": ", ".join([role.name for role in expense.user.role.all()]),
                "department_id": expense.department.id,
                "department_name": expense.department.name,
                "expense_slip": expense.expense_slip.url if expense.expense_slip else None,
            }
            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DeleteExpenseView(APIView):
    """
    Delete an expense.
    Only users with 'delete' permission for 'finance_management' can perform this action.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, expense_id):
        if not has_permission(request.user, "finance_management", "delete"):
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

        try:
            expense = get_object_or_404(Expense, id=expense_id)
            expense.delete()
            return Response(
                {"message": f"Expense with ID {expense_id} has been deleted successfully."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": f"An error occurred while deleting the expense: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
