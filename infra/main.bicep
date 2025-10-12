@description('Deployment location')
param location string = 'eastus'

@description('Base name prefix for all resources')
param baseName string = 'commhub'

// ---------- Storage Account ----------
resource storage 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: toLower('${baseName}store${uniqueString(resourceGroup().id)}')
  location: location
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
}

// ---------- Flex Consumption Plan ----------
resource plan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: '${baseName}-flexplan'
  location: location
  sku: {
    name: 'FC1'
    tier: 'FlexConsumption'
  }
  kind: 'functionapp'
}

// ---------- Function App ----------
resource functionApp 'Microsoft.Web/sites@2023-01-01' = {
  name: '${baseName}-func'
  location: location
  kind: 'functionapp'
  properties: {
    serverFarmId: plan.id
    siteConfig: {
      appSettings: [
        { name: 'FUNCTIONS_WORKER_RUNTIME', value: 'python' }
        { name: 'FUNCTIONS_EXTENSION_VERSION', value: '~4' }
        { name: 'AzureWebJobsStorage', value: storage.listKeys().keys[0].value }
        { name: 'WEBSITE_RUN_FROM_PACKAGE', value: '1' }
      ]
    }
    httpsOnly: true
  }
  identity: {
    type: 'SystemAssigned'
  }
}

// ---------- Outputs ----------
output functionAppName string = functionApp.name
output functionAppUrl string = 'https://${functionApp.properties.defaultHostName}'
