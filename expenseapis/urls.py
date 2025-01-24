from django.urls import path
from .views import AddExpenseView , GetAllExpenseView , DeleteExpenseView

urlpatterns = [
    path('create/', AddExpenseView.as_view(), name='add_expense'),  # Endpoint to create a role
    path('get-all/', GetAllExpenseView.as_view(), name='get_all_expense'), 
    path('<int:expense_id>/delete/',DeleteExpenseView.as_view(), name = 'delete-expense' ) # Endpoint to fetch all roles

]
