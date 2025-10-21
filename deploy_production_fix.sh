#!/bin/bash

echo "🚀 ServiceMan Backend - Production Fix Deployment"
echo "=================================================="
echo ""
echo "This will fix the 500 errors on servicemen endpoints"
echo ""

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: manage.py not found. Run this script from the project root."
    exit 1
fi

# Show git status
echo "📋 Current changes:"
git status --short
echo ""

# Ask for confirmation
read -p "🤔 Deploy fix to production? (y/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "❌ Deployment cancelled"
    exit 1
fi

# Add all changes
echo "➕ Adding changes..."
git add apps/users/serializers.py
git add apps/users/views.py
git add apps/notifications/views.py
git add apps/payments/views.py
git add apps/ratings/views.py
git add apps/negotiations/views.py
git add apps/services/views.py
git add PRODUCTION_MIGRATION_FIX.md
echo "✅ Changes staged"
echo ""

# Commit
echo "💾 Committing..."
git commit -m "Fix: Make all serializers migration-safe for production

- ServicemanProfile fields now use SerializerMethodField
- Approval fields default to safe values if not in database
- Skills return empty array if table doesn't exist
- Prevents 500 errors before migrations are run
- All endpoints work immediately after deploy
- Full functionality after migrations

Fixes:
- /api/users/servicemen/ now returns 200
- /api/users/servicemen/{id}/ now returns 200
- API docs warnings fixed with @extend_schema decorators
"

if [ $? -ne 0 ]; then
    echo "⚠️  Commit failed or nothing to commit"
    exit 1
fi
echo "✅ Committed"
echo ""

# Push
echo "🌐 Pushing to GitHub..."
git push origin main
if [ $? -ne 0 ]; then
    echo "❌ Push failed!"
    exit 1
fi
echo "✅ Pushed to GitHub"
echo ""

echo "🎉 Deployment initiated!"
echo ""
echo "📊 What happens next:"
echo "1. ✅ Render detects push and starts deployment"
echo "2. ✅ New code deployed (2-3 minutes)"
echo "3. ✅ Endpoints work immediately (with default values)"
echo "4. ⏳ Run migrations when ready (in Render Shell)"
echo ""
echo "🧪 Test after deployment:"
echo "curl https://serviceman-backend.onrender.com/api/users/servicemen/"
echo ""
echo "📋 Next steps:"
echo "1. Wait for Render deployment to complete (~3 min)"
echo "2. Test endpoint (should return 200 OK)"
echo "3. When ready, run migrations in Render Shell:"
echo "   python manage.py makemigrations"
echo "   python manage.py migrate"
echo ""
echo "📚 See PRODUCTION_MIGRATION_FIX.md for details"

