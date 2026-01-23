#!/usr/bin/env powershell

Write-Host "=== Git Push Script ===" -ForegroundColor Green
Write-Host ""

# Navigate to project
cd c:\AI

# Remove old git and reinitialize
Write-Host "Cleaning up old git repository..." -ForegroundColor Yellow
Remove-Item -Path .git -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "Git cleaned" -ForegroundColor Green
Write-Host ""

# Initialize git
Write-Host "Initializing new git repository..." -ForegroundColor Yellow
git init
Write-Host "Git initialized" -ForegroundColor Green
Write-Host ""

# Configure git
Write-Host "Configuring git user..." -ForegroundColor Yellow
git config user.email "admin@example.com"
git config user.name "Admin User"
Write-Host "Git configured" -ForegroundColor Green
Write-Host ""

# Add files
Write-Host "Adding all files..." -ForegroundColor Yellow
git add -A
Write-Host "Files added" -ForegroundColor Green
Write-Host ""

# Check what's staged
Write-Host "Files to be committed:" -ForegroundColor Cyan
git diff --cached --name-only | Select-Object -First 30
Write-Host ""

# Commit
Write-Host "Creating commit..." -ForegroundColor Yellow
git commit -m "Initial commit: All project files"
Write-Host "Commit created" -ForegroundColor Green
Write-Host ""

# Add remote
Write-Host "Adding GitHub remote..." -ForegroundColor Yellow
git remote add origin "git@github.com:MahalakshmiSenthilkumar03/WILD_VISION_PROJECT.git"
Write-Host "Remote added" -ForegroundColor Green
Write-Host ""

# Verify remote
Write-Host "Remote configuration:" -ForegroundColor Cyan
git remote -v
Write-Host ""

# Rename branch to main
Write-Host "Renaming branch to main..." -ForegroundColor Yellow
git branch -M main
Write-Host "Branch renamed" -ForegroundColor Green
Write-Host ""

# Push to GitHub
Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
git push -u origin main --force
Write-Host "Push complete!" -ForegroundColor Green
Write-Host ""

Write-Host "=== Script Complete ===" -ForegroundColor Green
