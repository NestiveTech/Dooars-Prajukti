"""
Apps Configuration for Accounts App
"""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """
    Configuration for the Accounts application
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = 'User Accounts'
    
    def ready(self):
        """
        Import signals or perform other initialization when app is ready
        """
        # Import signals here if needed
        # import accounts.signals
        pass