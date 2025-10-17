#!/bin/bash

echo "🔧 ServiceMan Backend - Production Fix Deployment"
echo "=================================================="
echo ""

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: manage.py not found. Run this script from the project root."
    exit 1
fi

# Create migrations
echo "📦 Step 1: Creating migrations..."
python manage.py makemigrations
if [ $? -ne 0 ]; then
    echo "❌ Migration creation failed!"
    exit 1
fi
echo "✅ Migrations created"
echo ""

# Check git status
echo "📝 Step 2: Checking git status..."
git status
echo ""

# Add all changes
echo "➕ Step 3: Adding changes to git..."
git add apps/users/
git add templates/
git add *.md
echo "✅ Changes staged"
echo ""

# Show what will be committed
echo "📋 Files to be committed:"
git status --short
echo ""

# Ask for confirmation
read -p "🤔 Proceed with commit and deploy? (y/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "❌ Deployment cancelled"
    exit 1
fi

# Commit
echo "💾 Step 4: Committing changes..."
git commit -m "Fix: Make serializers migration-safe to prevent 500 errors in production

- Updated ServicemanProfileSerializer to use SerializerMethodField for skills
- Added try-except blocks to handle missing skills table gracefully
- Skills will return empty array if migrations haven't run yet
- Prevents 500 errors on /api/users/servicemen/{id}/ endpoint"

if [ $? -ne 0 ]; then
    echo "⚠️  Nothing to commit or commit failed"
    echo "Checking if there are uncommitted changes..."
    git status
fi
echo ""

# Push to trigger Render deploy
echo "🌐 Step 5: Pushing to GitHub..."
git push origin main
if [ $? -ne 0 ]; then
    echo "❌ Push failed! Check your git configuration."
    exit 1
fi
echo "✅ Pushed to GitHub"
echo ""

echo "🎉 Deployment initiated!"
echo ""
echo "📊 Next steps:"
echo "1. Go to https://dashboard.render.com"
echo "2. Select your ServiceMan Backend service"
echo "3. Watch the deployment logs"
echo "4. After deployment, run migrations in Render Shell:"
echo "   python manage.py migrate"
echo ""
echo "5. Test the endpoint:"
echo "   curl https://serviceman-backend.onrender.com/api/users/servicemen/1/"
echo ""
echo "📚 For detailed instructions, see: PRODUCTION_500_ERROR_FIX.md"

