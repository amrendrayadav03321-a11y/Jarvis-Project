#!/bin/bash
# =======================================================
# 🚀 J.A.R.V.I.S. // GitHub Upload & Sync Helper
# Target Repository: amrendrayadav03321-a11y/Jarvis-Project
# =======================================================

set -e

REPO_NAME="amrendrayadav03321-a11y/Jarvis-Project"
DEFAULT_URL="https://github.com/${REPO_NAME}.git"

echo "======================================================="
echo "⚡ J.A.R.V.I.S. GITHUB UPLOAD HELPER"
echo "Target: https://github.com/${REPO_NAME}"
echo "======================================================="

# Ensure branch is main
git branch -M main

# Configure remote origin
git remote remove origin 2>/dev/null || true
git remote add origin "$DEFAULT_URL"
echo "✓ Git remote origin set to: $DEFAULT_URL"

echo ""
echo "📦 Staging and committing changes..."
git add .
git commit -m "Update Jarvis AI Assistant with ultra-fast response, strict wake-word shield, and complete macOS automations" 2>/dev/null || true

TOKEN="$1"

if [ -z "$TOKEN" ]; then
    echo ""
    echo "ℹ️  GitHub security requires a Personal Access Token to upload via terminal."
    echo "👉 Direct Link to generate token (repo permission auto-selected):"
    echo "   https://github.com/settings/tokens/new?scopes=repo&description=JarvisProject"
    echo ""
    echo "Enter your GitHub Token (starts with ghp_...) or press Enter to try system login:"
    read -r -s -p "Token: " TOKEN
    echo ""
fi

echo ""
echo "🚀 Pushing to GitHub (main branch)..."

if [ -n "$TOKEN" ]; then
    PUSH_URL="https://amrendrayadav03321-a11y:${TOKEN}@github.com/${REPO_NAME}.git"
    git push -u "$PUSH_URL" main --force
else
    git push -u origin main
fi

echo ""
echo "======================================================="
echo "🎉 SUCCESS! Your Jarvis repository is live on GitHub!"
echo "🔗 https://github.com/${REPO_NAME}"
echo "======================================================="
