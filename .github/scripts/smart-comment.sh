#!/bin/bash
# Smart Comment Handler - Updates existing comments instead of creating duplicates
# Usage: smart-comment.sh <pr_number> <marker> <comment_body_file>

set -e

PR_NUMBER=$1
MARKER=$2
COMMENT_FILE=$3

if [ -z "$PR_NUMBER" ] || [ -z "$MARKER" ] || [ -z "$COMMENT_FILE" ]; then
    echo "Usage: $0 <pr_number> <marker> <comment_body_file>"
    exit 1
fi

if [ ! -f "$COMMENT_FILE" ]; then
    echo "Error: Comment file not found: $COMMENT_FILE"
    exit 1
fi

# Add marker to comment body for future identification
COMMENT_BODY="<!-- ${MARKER} -->
$(cat "$COMMENT_FILE")"

# Find existing comment with this marker
EXISTING_COMMENT_ID=$(gh pr view "$PR_NUMBER" --json comments \
    --jq ".comments[] | select(.body | contains(\"<!-- ${MARKER} -->\")) | .id" \
    | head -n 1)

if [ -n "$EXISTING_COMMENT_ID" ]; then
    # Update existing comment
    echo "Updating existing comment (ID: $EXISTING_COMMENT_ID)"
    echo "$COMMENT_BODY" | gh api \
        -X PATCH \
        "/repos/{owner}/{repo}/issues/comments/$EXISTING_COMMENT_ID" \
        -f body=@- > /dev/null
    echo "✅ Comment updated"
else
    # Create new comment
    echo "Creating new comment with marker: $MARKER"
    echo "$COMMENT_BODY" | gh pr comment "$PR_NUMBER" --body-file - > /dev/null
    echo "✅ Comment created"
fi
