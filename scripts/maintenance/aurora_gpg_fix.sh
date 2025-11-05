#!/bin/bash
# Aurora CloudBank GPG Fix Script
# Run this anytime you encounter 403 author invalid errors

echo "🔐 Aurora CloudBank GPG Persistent Fix"
echo "=================================="

# Disable GPG signing
git config --global commit.gpgsign false
git config commit.gpgsign false
git config --global tag.gpgsign false
git config tag.gpgsign false

# Configure user
git config --global user.name "Aurora CloudBank"
git config --global user.email "aurora@cloudbank.dev"
git config user.name "Aurora CloudBank"
git config user.email "aurora@cloudbank.dev"

# Fix other issues
git config --global --add safe.directory /workspaces/aurora-cloudbank-symbolic
git config --global core.editor nano

echo "✅ GPG fixes applied successfully!"
echo "🚀 You can now commit without 403 errors"
