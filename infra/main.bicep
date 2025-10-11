@description('Deployment location')
param location string = resourceGroup().location

@description('Base name prefix for all resources')
param baseName string = 'commhub'

// ---------- Storage Account ----------
resource storage 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: toLower('${baseName}store${uniqueString(resourceGroup().id)}')
  location: location
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
}

// ---------- App Service Plan (Elastic Premium) ----------
resource plan 'Microsoft.Web/serverfarms@2022-09-01' = {
  name: '${baseName}-plan'
  location: location
  sku: {
    name: 'EP1'
    tier: 'ElasticPremium'
    size: 'EP1'
    capacity: 1
  }
  kind: 'functionapp'
}

// ---------- Function App ----------
resource functionApp 'Microsoft.Web/sites@2022-09-01' = {
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
        { name: 'SCM_DO_BUILD_DURING_DEPLOYMENT', value: '1' }
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
