"""
Django views for the comment system.

This module handles:
- Displaying and paginating comments
- Creating new comments and replies
- CAPTCHA image generation
- Live comment preview (AJAX)
- WebSocket notifications for real-time updates
"""

import uuid

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.cache import cache
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .captcha import generate_captcha_code, generate_captcha_image
from .forms import CommentForm
from .models import Comment
from .services import resize_attachment_image
from .validators import sanitize_comment_html


def comment_list(request):
    """
    Display paginated comments and handle comment creation.

    This view supports:
    - GET: Display list of published top-level comments with sorting
        and pagination
    - POST: Create new top-level comments or replies to existing comments
    - Caching: Server-side caching of comment queries for performance
    - WebSocket: Real-time notification when new comments are created

    Args:
        request: Django HTTP request object.

    Returns:
        HttpResponse: Rendered comment list template or JSON response for AJAX.

    Query Parameters:
        parent: ID of parent comment for replies (optional)
        sort: Sort field (author_name, email, created_at)
        direction: Sort direction (asc, desc)
        page: Page number for pagination

    Notes:
        - Cache is cleared after new comment creation
        - Supports both AJAX and traditional form submission
        - Attachments are resized if they exceed maximum dimensions
    """
    parent_id = request.GET.get("parent")
    parent_comment = None

    if parent_id:
        parent_comment = get_object_or_404(Comment, pk=parent_id)

    if request.method == "POST":
        form = CommentForm(request.POST, request.FILES, request=request)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.parent = parent_comment
            # Convert line breaks to HTML <br> tags
            comment.text = comment.text.replace("\n", "<br>")

            # Resize image attachment if present
            if comment.attachment:
                resize_attachment_image(comment.attachment)

            comment.save()

            # Clear cache after creating a comment to ensure fresh data
            cache.clear()

            # Send WebSocket notification for real-time updates
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "comments",
                {
                    "type": "comment.created",
                    "message": "new_comment",
                },
            )

            # For AJAX requests, return JSON instead of redirect
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'ok'})

            return redirect("comments:comment_list")

        # Form is invalid
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'errors': form.errors}, status=400)

        # For non-AJAX, re-render the page with errors
        # (existing code below will handle this)
    else:
        form = CommentForm(request=request)

    # Get sorting parameters from query string
    sort = request.GET.get("sort", "created_at")
    direction = request.GET.get("direction", "desc")

    # Whitelist of allowed sort fields to prevent SQL injection
    allowed_sort_fields = {
        "author_name": "author_name",
        "email": "email",
        "created_at": "created_at",
    }

    sort_field = allowed_sort_fields.get(sort, "created_at")
    ordering = sort_field if direction == "asc" else f"-{sort_field}"

    # Build a unique cache key for this request (page + sort + direction)
    cache_key = (f"comments_page_{request.GET.get('page', '1')}"
                 f"_{sort}_{direction}")

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
        .prefetch_related("replies")  # Optimize nested reply queries
    )

    paginator = Paginator(comments_qs, 25)
    page_number = request.GET.get("page")
    comments = paginator.get_page(page_number)

    # Cache the result (list of objects + count) for 60 seconds
    cache.set(cache_key, (list(comments_qs), paginator.count), 60)

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

    This AJAX endpoint allows users to see a live preview of their comment
    before submission, with all HTML sanitized for security.

    Args:
        request: Django HTTP request object (POST only).

    Returns:
        JsonResponse: JSON object with 'preview_html'
        key containing sanitized HTML.

    POST Data:
        text: Raw comment text from user input.
    """
    text = request.POST.get("text", "")
    sanitized = sanitize_comment_html(text)
    return JsonResponse({"preview_html": sanitized})


def captcha_image(request):
    """
    Generate a CAPTCHA image and store its code under a form token.

    This endpoint creates a new CAPTCHA image with a random code,
    stores the code in the session for later validation, and returns
    the image as a PNG response.

    Args:
        request: Django HTTP request object.

    Returns:
        HttpResponse: PNG image with X-Captcha-Token header
        for form association.

    Query Parameters:
        token: Optional form token (generated if not provided).

    Notes:
        - CAPTCHA code is stored in session as 'captcha_{token}'
        - Token is returned in X-Captcha-Token header for form submission
    """
    token = request.GET.get("token") or uuid.uuid4().hex
    code = generate_captcha_code()

    # Store CAPTCHA code in session for validation
    request.session[f"captcha_{token}"] = code
    request.session.modified = True

    # Generate and return CAPTCHA image
    image = generate_captcha_image(code)
    response = HttpResponse(image, content_type="image/png")
    response["X-Captcha-Token"] = token
    return response
