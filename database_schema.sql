-- Database Schema for Django Comment System
-- PostgreSQL compatible
-- Generated for test assignment

-- Table: comments_comment
-- Stores all comments with nested reply support
CREATE TABLE comments_comment (
    id BIGSERIAL PRIMARY KEY,
    author_name VARCHAR(255) NOT NULL,
    email VARCHAR(254) NOT NULL,
    home_page VARCHAR(200),
    text TEXT NOT NULL,
    attachment VARCHAR(100),
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    parent_id BIGINT REFERENCES comments_comment(id) ON DELETE CASCADE
);

-- Comments for documentation
COMMENT ON TABLE comments_comment IS 'Comment system with nested replies and moderation queue';
COMMENT ON COLUMN comments_comment.author_name IS 'Comment author name (Latin letters and digits only)';
COMMENT ON COLUMN comments_comment.email IS 'Author email address (required, validated format)';
COMMENT ON COLUMN comments_comment.home_page IS 'Optional author website URL (http/https only)';
COMMENT ON COLUMN comments_comment.text IS 'Comment text with allowed HTML tags (a, code, i, strong)';
COMMENT ON COLUMN comments_comment.attachment IS 'File path to attachment (JPG, PNG, GIF, or TXT)';
COMMENT ON COLUMN comments_comment.status IS 'Comment status: pending or published';
COMMENT ON COLUMN comments_comment.parent_id IS 'Reference to parent comment for nested replies';

-- Indexes for performance
CREATE INDEX idx_comments_status ON comments_comment(status);
CREATE INDEX idx_comments_created_at ON comments_comment(created_at);
CREATE INDEX idx_comments_parent ON comments_comment(parent_id);

-- Notes:
-- - Self-referencing foreign key enables unlimited nesting depth
-- - Status field supports moderation queue (pending -> published)
-- - Indexes optimize sorting and filtering operations
-- - ON DELETE CASCADE ensures child comments are removed with parent
-- - BIGSERIAL provides auto-incrementing 64-bit integer primary key
