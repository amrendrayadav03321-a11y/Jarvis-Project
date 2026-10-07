#!/bin/bash
# =======================================================
# 🚀 J.A.R.V.I.S. // GitHub Upload & Sync Helper
# =======================================================

set -e

echo "======================================================="
echo "⚡ J.A.R.V.I.S. GITHUB UPLOAD HELPER"
echo "======================================================="

# Ensure branch is main
git branch -M main

# Check if origin remote exists
REMOTE_URL=$(git remote get-url origin 2>/dev/null || true)

if [ -z "$REMOTE_URL" ]; then
    if [ -n "$1" ]; then
        REMOTE_URL="$1"
        git remote add origin "$REMOTE_URL"
        echo "✓ Added remote origin: $REMOTE_URL"
    else
        echo ""
        echo "Please enter your GitHub repository URL:"
        echo "(Example: https://github.com/your-username/Jarvis.git)"
        read -p "> " REMOTE_URL
        if [ -z "$REMOTE_URL" ]; then
            echo "❌ No URL provided. Aborting."
            exit 1
        fi
        git remote add origin "$REMOTE_URL"
        echo "✓ Added remote origin: $REMOTE_URL"
    fi
else
    echo "✓ Existing remote origin found: $REMOTE_URL"
    if [ -n "$1" ]; then
        git remote set-url origin "$1"
        REMOTE_URL="$1"
        echo "✓ Updated remote origin to: $REMOTE_URL"
    fi
fi

echo ""
echo "📦 Staging and committing changes..."
git add .
git commit -m "Update Jarvis AI Assistant with ultra-fast response, strict wake-word shield, and complete macOS automations" 2>/dev/null || true

echo ""
echo "🚀 Pushing to GitHub (main branch)..."
git push -u origin main

echo ""
echo "======================================================="
echo "🎉 SUCCESS! Your Jarvis repository is live on GitHub!"
echo "🔗 $REMOTE_URL"
echo "======================================================="
