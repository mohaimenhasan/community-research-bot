@description('Deployment location')
param location string = resourceGroup().location

@description('Base name prefix for all resources')
param baseName string = 'commhub'

// ---------- Storage Account ----------
resource storage 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: take(toLower('${baseName}${uniqueString(resourceGroup().id)}'), 24)
  location: location
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
}

// ---------- Consumption Plan ----------
resource plan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: '${baseName}-plan'
  location: location
  sku: {
    name: 'Y1'
    tier: 'Dynamic'
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
