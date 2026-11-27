#!/usr/bin/env pwsh
# push-to-github.ps1
# Run this ONCE from inside the project folder to link it to your GitHub repo.
# Edit the REPO_URL line before running.

$REPO_URL = "https://github.com/YOUR_USERNAME/AI-Subtitle-Studio.git"

git remote add origin $REPO_URL
git branch -M main
git push -u origin main

Write-Host ""
Write-Host "✅ Project pushed to GitHub!"
Write-Host "🌐 Visit: $REPO_URL"
