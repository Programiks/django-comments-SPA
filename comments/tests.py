from django.test import TestCase
from .models import Comment


class CommentCreationTest(TestCase):
    def test_create_comment(self):
        Comment.objects.create(
            author_name="test_user",
            text="This is the first test comment.",
        )
        self.assertEqual(Comment.objects.count(), 1)


class CommentHtmlValidationTest(TestCase):
    def test_create_comment_plain_text(self):
        Comment.objects.create(
            author_name="test_user",
            email="test@example.com",
            text="Just plain text, no HTML here.",
        )
        self.assertEqual(Comment.objects.count(), 1)


    def test_reject_script_tag(self):
        from django.core.exceptions import ValidationError

        with self.assertRaises(ValidationError):
            Comment(
                author_name="test_user",
                email="test@example.com",
                text="Hello <script>alert('xss')</script> world.",
            ).full_clean()


class NestedCommentsTest(TestCase):
    def test_comment_can_have_unlimited_nested_replies(self):
        root_comment = Comment.objects.create(
            author_name="root_user",
            email="root@example.com",
            text="Root comment.",
        )

        first_reply = Comment.objects.create(
            author_name="first_reply_user",
            email="first@example.com",
            text="First-level reply.",
            parent=root_comment,
        )

        second_reply = Comment.objects.create(
            author_name="second_reply_user",
            email="second@example.com",
            text="Second-level reply.",
            parent=first_reply,
        )

        third_reply = Comment.objects.create(
            author_name="third_reply_user",
            email="third@example.com",
            text="Third-level reply.",
            parent=second_reply,
        )

        self.assertIsNone(root_comment.parent)
        self.assertEqual(first_reply.parent, root_comment)
        self.assertEqual(second_reply.parent, first_reply)
        self.assertEqual(third_reply.parent, second_reply)

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
