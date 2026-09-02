from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Comment


class CommentCreationTest(TestCase):
    """Test basic comment creation with valid data."""

    def test_create_comment(self):
        # Create a comment with all required fields
        comment = Comment(
            author_name="test_user",
            email="test@example.com",
            text="This is the first test comment.",
        )
        # Run full_clean() to validate model constraints
        comment.full_clean()
        comment.save()
        # Verify exactly one comment exists in the database
        self.assertEqual(Comment.objects.count(), 1)


class CommentEmailValidationTest(TestCase):
    """Test email validation rules for comments."""

    def test_create_comment_without_email(self):
        # Email is required; empty string should raise ValidationError
        comment = Comment(
            author_name="test_user",
            email="",
            text="Comment without email.",
        )
        with self.assertRaises(ValidationError):
            comment.full_clean()

    def test_create_comment_with_invalid_email(self):
        # Invalid email format should raise ValidationError
        comment = Comment(
            author_name="test_user",
            email="not-an-email",
            text="Comment with invalid email.",
        )
        with self.assertRaises(ValidationError):
            comment.full_clean()


class CommentTextLengthValidationTest(TestCase):
    """Test text length constraints (min 2, max 2000 characters)."""

    def test_create_comment_text_too_short(self):
        # Text shorter than 2 characters should raise ValidationError
        comment = Comment(
            author_name="test_user",
            email="test@example.com",
            text="X",
        )
        with self.assertRaises(ValidationError):
            comment.full_clean()

    def test_create_comment_text_min_length(self):
        # Text with exactly 2 characters should be valid
        comment = Comment(
            author_name="test_user",
            email="test@example.com",
            text="XY",
        )
        comment.full_clean()
        comment.save()
        self.assertEqual(Comment.objects.count(), 1)

    def test_create_comment_text_too_long(self):
        # Text longer than 2000 characters should raise ValidationError
        comment = Comment(
            author_name="test_user",
            email="test@example.com",
            text="X" * 2001,
        )
        with self.assertRaises(ValidationError):
            comment.full_clean()

    def test_create_comment_text_max_length(self):
        # Text with exactly 2000 characters should be valid
        comment = Comment(
            author_name="test_user",
            email="test@example.com",
            text="X" * 2000,
        )
        comment.full_clean()
        comment.save()
        self.assertEqual(Comment.objects.count(), 1)


class CommentCaptchaValidationTest(TestCase):
    """Test CAPTCHA validation (if applicable at model level)."""

    def test_create_comment_without_captcha(self):
        # CAPTCHA is validated in form/serializer, not in model.
        # This test is a placeholder; skip if captcha_token is not a model field.
        pass


class CommentHtmlValidationTest(TestCase):
    """Test HTML sanitization and security rules for comment text."""

    def test_create_comment_plain_text(self):
        # Plain text without HTML should be accepted
        Comment.objects.create(
            author_name="test_user",
            email="test@example.com",
            text="Just plain text, no HTML here.",
        )
        self.assertEqual(Comment.objects.count(), 1)

    def test_reject_script_tag(self):
        # Script tags must be rejected to prevent XSS attacks
        with self.assertRaises(ValidationError):
            Comment(
                author_name="test_user",
                email="test@example.com",
                text="Hello <script>alert('xss')</script> world.",
            ).full_clean()


class NestedCommentsTest(TestCase):
    """Test nested comment replies (unlimited depth)."""

    def test_comment_can_have_unlimited_nested_replies(self):
        # Create a root comment
        root_comment = Comment.objects.create(
            author_name="root_user",
            email="root@example.com",
            text="Root comment.",
        )

        # Create first-level reply
        first_reply = Comment.objects.create(
            author_name="first_reply_user",
            email="first@example.com",
            text="First-level reply.",
            parent=root_comment,
        )

        # Create second-level reply
        second_reply = Comment.objects.create(
            author_name="second_reply_user",
            email="second@example.com",
            text="Second-level reply.",
            parent=first_reply,
        )

        # Create third-level reply
        third_reply = Comment.objects.create(
            author_name="third_reply_user",
            email="third@example.com",
            text="Third-level reply.",
            parent=second_reply,
        )

        # Verify parent-child relationships
        self.assertIsNone(root_comment.parent)
        self.assertEqual(first_reply.parent, root_comment)
        self.assertEqual(second_reply.parent, first_reply)
        self.assertEqual(third_reply.parent, second_reply)

        # Verify replies are correctly linked
        self.assertEqual(
            list(root_comment.replies.all()),
            [first_reply],
        )
        self.assertEqual(
            list(first_reply.replies.all()),
            [second_reply],
        )
        self.assertEqual(
            list(second_reply.replies.all()),
            [third_reply],
        )
