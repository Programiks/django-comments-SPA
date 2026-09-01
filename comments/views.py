from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache

from .captcha import generate_captcha_code, generate_captcha_image
from .forms import CommentForm
from .models import Comment
from .services import resize_attachment_image
from .validators import sanitize_comment_html

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
            comment.text = comment.text.replace("\n", "<br>")

            if comment.attachment:
                resize_attachment_image(comment.attachment)

            comment.save()
            # Clear cache after creating a comment
            cache.clear()
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

    # Build a unique cache key for this request
    cache_key = f"comments_page_{request.GET.get('page', '1')}_{sort}_{direction}"

    # Try to get from cache
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        comments, paginator_count = cached_data
        # Rebuild paginator from cached data
        comments_qs = (
            Comment.objects
            .filter(parent__isnull=True, status=Comment.STATUS_PUBLISHED)
            .order_by(ordering)
        )
        paginator = Paginator(comments_qs, 25)
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

    # If not in cache, query the database
    comments_qs = (
        Comment.objects
        .filter(parent__isnull=True, status=Comment.STATUS_PUBLISHED)
        .order_by(ordering)
        .prefetch_related("replies")
    )

    paginator = Paginator(comments_qs, 25)
    page_number = request.GET.get("page")
    comments = paginator.get_page(page_number)

    # Cache the result (list of objects + count)
    cache.set(cache_key, (list(comments_qs), paginator.count), 60)  # 60 seconds

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


@require_http_methods(["POST"])
@csrf_exempt
def comment_preview(request):
    """
    Return sanitized HTML preview of the comment text.
    Expects 'text' in POST data, returns JSON with 'preview_html'.
    """
    text = request.POST.get("text", "")
    sanitized = sanitize_comment_html(text)
    return JsonResponse({"preview_html": sanitized})


def captcha_image(request):
    """Generate a CAPTCHA image and store its code in the session."""
    code = generate_captcha_code()
    request.session["captcha_code"] = code

    image = generate_captcha_image(code)
    return HttpResponse(image, content_type="image/png")
