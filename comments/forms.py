"""
Django forms for the comment system.

This module provides form classes for:
- Comment creation with CAPTCHA validation
- File attachment handling
- User input sanitization
"""

from django import forms

from .models import Comment


class CommentForm(forms.ModelForm):
    """
    Form for creating and submitting comments.

    This form includes:
    - Standard comment fields (author, email, text, etc.)
    - CAPTCHA validation for spam prevention
    - File attachment support

    Attributes:
        captcha: CAPTCHA field for bot protection (6 characters).
    """

    captcha = forms.CharField(
        label="CAPTCHA",
        max_length=6,
        min_length=6,
        help_text="Enter the characters shown in the image.",
        widget=forms.TextInput(
            attrs={
                "autocomplete": "off",  # Prevent browser autocomplete
                "placeholder": "Enter CAPTCHA",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        """
        Initialize form and store request for CAPTCHA validation.

        Args:
            *args: Positional arguments passed to ModelForm.
            **kwargs: Keyword arguments including 'request' for session access.

        Notes:
            - 'request' is popped from kwargs to prevent passing to parent
            - Request is used to access session-stored CAPTCHA codes
        """
        # Store the request to access the CAPTCHA code in the session
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    def clean_captcha(self):
        """
        Validate the user-entered CAPTCHA against the session value.

        This method retrieves the expected CAPTCHA code from the session
        using the token submitted with the form, and compares it with
        the user's input (case-insensitive).

        Returns:
            str: Validated CAPTCHA code (uppercase).

        Raises:
            forms.ValidationError: If CAPTCHA is missing, expired,
            or incorrect.

        Notes:
            - CAPTCHA codes are stored in session as 'captcha_{token}'
            - Comparison is case-insensitive (input is uppercased)
        """
        captcha = self.cleaned_data["captcha"].upper()

        # Retrieve expected CAPTCHA code from session using form token
        expected_code = (
            self.request.session.get(
                f"captcha_{self.data.get('captcha_token', '')}"
            )
            if self.request
            else None
        )

        if not expected_code or captcha != expected_code:
            raise forms.ValidationError("Incorrect CAPTCHA. Please try again.")

        return captcha

    class Meta:
        """
        Meta configuration for CommentForm.

        Specifies the model and fields to include in the form,
        along with custom widget configurations.
        """

        model = Comment
        fields = [
            "author_name",
            "email",
            "home_page",
            "text",
            "attachment",
        ]
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "rows": 6,
                    "placeholder": "Write your comment...",
                }
            ),
        }
