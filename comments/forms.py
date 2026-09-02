from django import forms

from .models import Comment


class CommentForm(forms.ModelForm):
    captcha = forms.CharField(
        label="CAPTCHA",
        max_length=6,
        min_length=6,
        help_text="Enter the characters shown in the image.",
        widget=forms.TextInput(
            attrs={
                "autocomplete": "off",
                "placeholder": "Enter CAPTCHA",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        """Store the request to access the CAPTCHA code in the session."""
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    def clean_captcha(self):
        """Validate the user-entered CAPTCHA against the session value."""
        captcha = self.cleaned_data["captcha"].upper()

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
