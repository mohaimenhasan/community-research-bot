#!/bin/bash

# Test script for Azure AI Foundry Agent with real internet search
# This tests the actual agent endpoint to verify it's doing real research

echo "🧪 Testing Azure AI Foundry Research Agent with Real Internet Search"
echo "=================================================================="
echo ""

# Test 1: Simple location query
echo "Test 1: Simple location query (Vancouver)"
echo "-------------------------------------------"
curl -X POST "https://commhub-func-cnbkczf6a4ctdhcz.westus2-01.azurewebsites.net/api/research_agent" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "Vancouver, British Columbia"
  }' | jq '.metadata.status, .agent_response.data_source, .agent_response.content | .[0:200]'

echo ""
echo ""

# Test 2: Location with user interests
echo "Test 2: Location with user interests (Bellevue, WA)"
echo "---------------------------------------------------"
curl -X POST "https://commhub-func-cnbkczf6a4ctdhcz.westus2-01.azurewebsites.net/api/research_agent" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "Bellevue, Washington",
    "preferences": {
      "interests": ["city council", "community events"]
    }
  }' | jq '.metadata.status, .agent_response.data_source'

echo ""
echo ""
echo "✅ Tests complete!"
echo ""
echo "💰 Cost Optimization Applied:"
echo "- Max tokens limited to 800 per request"
echo "- Concise prompts to reduce token usage"
echo "- Temperature 0.3 for focused responses"
echo "- No mock data fallbacks (all real research)"
echo ""
echo "📊 Expected cost per request: ~$0.02-0.05"
echo "   (Based on 800 completion tokens + ~200 prompt tokens + search calls)"
