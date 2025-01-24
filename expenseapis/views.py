from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ufcmsdb.models import Expense, User, Department
from datetime import datetime



class GetAllExpenseView(APIView):
    def get(self, request):
        expenses = Expense.objects.all()
        data = [
            {
                "id": expense.id,
                "date": expense.date,
                "amount": expense.amount,
                "description": expense.description,
                "user_id": expense.user.id,
                "user_name": expense.user.name,  # User name
                "department_id": expense.department.id,
                "department_name": expense.department.name,  # Department name
                "user_role": ", ".join([role.name for role in expense.user.role.all()]),  # User roles
                "expense_slip": expense.expense_slip.url if expense.expense_slip else None,
            }
            for expense in expenses
        ]
        return Response(data, status=status.HTTP_200_OK)


class AddExpenseView(APIView):
    """
    View for adding a new expense with validation.
    """
    def post(self, request):
        data = request.data
        # Validate required fields
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
            user = get_object_or_404(User, pk=data['user'])

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

            

            
            # Prepare response data including user_name, user_role, and department_name
            response_data = {
                "id": expense.id,
                "date": expense.date,
                "amount": expense.amount,
                "description": expense.description,
                "user_id": expense.user.id,
                "user_name": expense.user.name,  # User name
                "user_role": ", ".join([role.name for role in expense.user.role.all()]),  # User roles
                "department_id": expense.department.id,
                "department_name": expense.department.name,  # Department name
                "expense_slip": expense.expense_slip.url if expense.expense_slip else None,
            }
            
            # Success response
            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DeleteExpenseView(APIView):
 
    def delete(self, request, expense_id):
        try:
            # Get the expense or return a 404 if not found
            expense = get_object_or_404(Expense, id=expense_id)
            
            # Delete the expense
            expense.delete()
            
            # Return success response
            return Response(
                {"message": f"Expense with ID {expense_id} has been deleted successfully."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            # Handle unexpected errors
            return Response(
                {"error": f"An error occurred while deleting the expense: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
