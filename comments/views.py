from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.http import HttpResponse

from .captcha import generate_captcha_code, generate_captcha_image
from .forms import CommentForm
from .models import Comment
from .services import resize_attachment_image


def comment_list(request):
    """Display comments and create top-level comments or replies."""
    parent_id = request.GET.get("parent")
    parent_comment = None

    if parent_id:
        parent_comment = get_object_or_404(Comment, pk=parent_id)

    if request.method == "POST":
        form = CommentForm(request.POST, request.FILES, request=request)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.parent = parent_comment

            if comment.attachment:
                resize_attachment_image(comment.attachment)

            comment.save()
            return redirect("comments:comment_list")
    else:
        form = CommentForm(request=request)

    sort = request.GET.get("sort", "created_at")
    direction = request.GET.get("direction", "desc")

    allowed_sort_fields = {
        "author_name": "author_name",
        "email": "email",
        "created_at": "created_at",
    }

    sort_field = allowed_sort_fields.get(sort, "created_at")
    ordering = sort_field if direction == "asc" else f"-{sort_field}"

    comments = (
        Comment.objects
        .filter(parent__isnull=True)
        .order_by(ordering)
        .prefetch_related("replies")
    )

    paginator = Paginator(comments, 25)
    page_number = request.GET.get("page")
    comments = paginator.get_page(page_number)

    return render(
        request,
        "comments/comment_list.html",
        {
            "comments": comments,
            "form": form,
            "parent_comment": parent_comment,
            "sort": sort,
            "direction": direction,
        },
    )


def captcha_image(request):
    """Generate a CAPTCHA image and store its code in the session."""
    code = generate_captcha_code()
    request.session["captcha_code"] = code

    image = generate_captcha_image(code)
    return HttpResponse(image, content_type="image/png")
