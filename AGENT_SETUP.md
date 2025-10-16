# Azure AI Foundry Agent Configuration Guide

## 🎯 Critical: Enable Internet Search in Your Agent

Your agent needs internet search capabilities to find real data. Follow these steps:

## Step-by-Step Configuration

### 1. Access Azure AI Foundry
1. Go to https://ai.azure.com
2. Sign in with your Azure account
3. Select your project: `community-research`

### 2. Navigate to Your Agent
1. Click "Agents" in left navigation
2. Find agent ID: `asst_Ij5hGoGiriNuG7VGLGIAZ0zi`
3. Click to open agent configuration

### 3. Enable Bing Search Tool
1. In agent configuration, look for "Tools" section
2. Check the box for "**Bing Search**" or "**Web Search**"
3. This allows the agent to search the internet for current information
4. Click "Save" or "Update"

### 4. Verify Agent Instructions
Your agent should have instructions similar to:
```
You are a community research assistant that helps users discover local events, 
town hall meetings, and community news. Use internet search to find current, 
accurate information from official sources like city government websites, 
local news outlets, and community event calendars.
```

### 5. Test the Agent in Azure AI Foundry
Before deploying, test in the Azure AI Foundry playground:

**Test Query**:
```
Find current city council meetings and community events in Bellevue, Washington.
```

**Expected Behavior**:
- Agent should use Bing search tool
- Agent should return REAL information with sources
- Response should include actual URLs and specific dates

**Red Flags** (means search is NOT working):
- Generic/vague responses
- No source URLs
- Dates like "TBD" or "Various dates"
- Same response for different cities

## 🔧 Environment Variables to Set

In your Azure Function App (`commhub-func`), ensure these are set:

```bash
# Set via Azure CLI
az functionapp config appsettings set \
  --name commhub-func \
  --resource-group community-research \
  --settings \
    "AGENT_ID=asst_Ij5hGoGiriNuG7VGLGIAZ0zi" \
    "RESOURCE_NAME=community-research" \
    "AZURE_OPENAI_KEY=<your-api-key>"
```

## 🧪 Verification Steps

### 1. Check Agent Configuration
```bash
# Use Azure CLI to verify agent exists
az cognitiveservices account show \
  --name community-research \
  --resource-group community-research
```

### 2. Test Function Locally
```bash
cd function_app

# Set environment variables locally
export AGENT_ID="asst_Ij5hGoGiriNuG7VGLGIAZ0zi"
export RESOURCE_NAME="community-research"
export AZURE_OPENAI_KEY="<your-key>"

# Start local function
func start

# Test in another terminal
curl -X POST http://localhost:7071/api/research_agent \
  -H "Content-Type: application/json" \
  -d '{"location": "Bellevue, WA"}'
```

### 3. Test Deployed Function
```bash
./test-real-agent.sh
```

## 📊 Cost Monitoring

### Check Agent Usage
1. Go to Azure Portal
2. Navigate to your Azure AI resource: `community-research`
3. Click "Metrics" in left menu
4. Add metric: "Token Usage"
5. Set time range: Last 24 hours

### Expected Token Usage Per Request
- Prompt tokens: ~100-200
- Completion tokens: ~400-800
- Search API calls: 2-5 per request
- **Total cost**: $0.02-0.05 per request

### Set Cost Alerts
1. In Azure Portal, go to "Cost Management + Billing"
2. Create budget for Azure AI service
3. Set alert at $50/month (covers ~1000-2500 requests)
4. Get email when approaching limit

## 🔍 Troubleshooting

### Problem: Agent returns "Tool 'bing_search' not found"
**Solution**: 
1. Go to Azure AI Foundry agent settings
2. Enable "Bing Search" tool
3. Save and redeploy

### Problem: Agent response doesn't include sources
**Solution**:
1. Check agent instructions include "cite sources"
2. Verify Bing search tool is actually enabled
3. Test agent in Azure AI Foundry playground first

### Problem: "Cannot access attribute 'call_agent_with_search'"
**Solution**:
1. Ensure you deployed the latest code
2. Check GitHub Actions deployment succeeded
3. Restart Function App:
```bash
az functionapp restart --name commhub-func --resource-group community-research
```

### Problem: High costs / too many tokens
**Solution**:
1. Reduce `max_tokens` in `foundry_client.py` (currently 800, can go to 400)
2. Implement response caching for repeated queries
3. Add rate limiting (max 5 requests per user per hour)
4. Consider GPT-3.5-turbo for simpler queries (10x cheaper)

## 📝 Agent Configuration Best Practices

### 1. Clear, Concise Instructions
❌ Bad:
```
You are an amazing AI that does incredible research and provides wonderful 
content with lots of details and comprehensive information about everything...
```

✅ Good:
```
Search internet for current events in the specified location. Return 3-5 items 
per category with dates, times, locations, and source URLs. Be concise.
```

### 2. Specify Output Format
```
Format each item as:
**Title** - Brief description (date, time, location)
Source: [URL]
```

### 3. Enable Only Necessary Tools
- ✅ Bing Search (required for internet research)
- ❌ Code Interpreter (not needed, adds cost)
- ❌ File Search (not needed, adds cost)

### 4. Set Token Limits
```python
"max_completion_tokens": 800  # Enough for 10-15 events
```

### 5. Use Lower Temperature
```python
"temperature": 0.3  # More focused = fewer tokens = lower cost
```

## 🎉 Success Criteria

Your agent is working correctly when:
- ✅ Returns real, current information
- ✅ Includes source URLs (e.g., vancouver.ca, bellevuewa.gov)
- ✅ Provides specific dates and times
- ✅ Different responses for different cities
- ✅ Response includes "data_source": "azure_ai_foundry_internet_search"
- ✅ Cost per request is $0.02-0.05

## 🚀 Next: Deploy and Test

1. **Enable Bing Search** in Azure AI Foundry agent
2. **Deploy updated code**: `git push origin main`
3. **Wait for deployment**: ~2-3 minutes
4. **Run test script**: `./test-real-agent.sh`
5. **Verify real data**: Check response has actual URLs and specific dates
6. **Monitor costs**: Azure Portal > Cost Management

---

**Questions?** See `REAL_DATA_FIX.md` for detailed troubleshooting and cost optimization strategies.
