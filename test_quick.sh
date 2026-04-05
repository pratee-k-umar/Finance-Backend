#!/bin/bash

# Quick test script for role-based access control
# Run this to quickly test the key features

BASE_URL="http://localhost:8000/api/v1"

echo "================================"
echo "QUICK ROLE-BASED ACCESS TEST"
echo "================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Test: Viewer cannot create users
echo "1️⃣  TEST: Viewer tries to list users (should be FORBIDDEN)"
curl -s http://$BASE_URL/users/ -u viewer_user:viewer123 | head -5
echo ""

# Test: Admin can list users
echo "2️⃣  TEST: Admin lists users (should work)"
curl -s http://$BASE_URL/users/ -u admin_user:admin123 | head -10
echo ""

# Test: Viewer can read records
echo "3️⃣  TEST: Viewer can read financial records"
curl -s http://$BASE_URL/financial-records/ -u viewer_user:viewer123 | head -10
echo ""

# Test: Viewer cannot create records
echo "4️⃣  TEST: Viewer tries to create record (should FAIL)"
curl -s -X POST http://$BASE_URL/financial-records/ \
  -u viewer_user:viewer123 \
  -H "Content-Type: application/json" \
  -d '{"amount":"100","record_type":"expense","category":"Test","date":"2026-04-05"}'
echo ""

# Test: Analyst can create records
echo "5️⃣  TEST: Analyst can create financial records (should succeed)"
curl -s -X POST http://$BASE_URL/financial-records/ \
  -u analyst_user:analyst123 \
  -H "Content-Type: application/json" \
  -d '{"amount":"100","record_type":"expense","category":"Test","date":"2026-04-05"}'
echo ""

# Test: All can access dashboard
echo "6️⃣  TEST: All roles can access dashboard"
echo "Viewer:"
curl -s http://$BASE_URL/dashboard/summary/ -u viewer_user:viewer123 | head -3
echo ""
echo "Analyst:"
curl -s http://$BASE_URL/dashboard/summary/ -u analyst_user:analyst123 | head -3
echo ""
echo "Admin:"
curl -s http://$BASE_URL/dashboard/summary/ -u admin_user:admin123 | head -3
echo ""

echo "================================"
echo "✅ QUICK TEST COMPLETE"
echo "================================"
