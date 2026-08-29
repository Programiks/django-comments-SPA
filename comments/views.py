from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm
from .models import Comment


def comment_list(request):
    """Display comments and create top-level comments or replies."""
    parent_id = request.GET.get("parent")
    parent_comment = None

    if parent_id:
        parent_comment = get_object_or_404(Comment, pk=parent_id)

    if request.method == "POST":
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.parent = parent_comment
            comment.save()
            return redirect("comment_list")
    else:
        form = CommentForm()

    comments = (
        Comment.objects
        .filter(parent__isnull=True)
        .prefetch_related("replies")
    )

    return render(
        request,
        "comments/comment_list.html",
        {
            "comments": comments,
            "form": form,
            "parent_comment": parent_comment,
        },
    )