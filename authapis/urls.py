from django.urls import path
from .views import LoginView , ForgotPasswordView , ResetPasswordView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),  # Login endpoint
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot'),  # Login endpoint
    path('reset-password/', ResetPasswordView.as_view(), name='reset'),  # Login endpoint
]
