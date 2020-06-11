from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class SpecialSymbol:
    """Custom validator: checks for the symbols, that differ from the letters and numbers."""
    def __init__(self):
        pass

    def validate(self, password, user=None):
        if str(password).isalnum():
            raise ValidationError(
                _("Password must contain at least one special symbol."),
                code='no_special_symbols',
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least one special symbol."
        )
