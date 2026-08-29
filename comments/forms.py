from django import forms

from .models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = [
            "author_name",
            "email",
            "home_page",
            "text",
        ]
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "rows": 6,
                    "placeholder": "Write your comment...",
                }
            ),
        }