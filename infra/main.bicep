// minor changes to trigger infra workflow

@description('Deployment location')
param location string = resourceGroup().location

@description('Base name prefix for all resources')
param baseName string = 'commhub'

@description('Storage account name (must be globally unique)')
param storageName string = toLower('${baseName}store${uniqueString(resourceGroup().id)}')

@description('Azure Function App name')
param functionAppName string = '${baseName}-func'

@description('App Service plan SKU')
param sku string = 'Y1' // Y1 = Consumption

// ---------- Storage Account ----------
resource storage 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageName
  location: location
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
}

// ---------- App Service Plan (for Function App) ----------
resource plan 'Microsoft.Web/serverfarms@2022-09-01' = {
  name: '${baseName}-plan'
  location: location
  sku: {
    name: sku
    tier: sku == 'Y1' ? 'Dynamic' : 'ElasticPremium'
  }
  kind: 'functionapp'
}

// ---------- Function App ----------
resource functionApp 'Microsoft.Web/sites@2022-09-01' = {
  name: functionAppName
  location: location
  kind: 'functionapp'
  properties: {
    serverFarmId: plan.id
    siteConfig: {
      appSettings: [
        { name: 'FUNCTIONS_WORKER_RUNTIME', value: 'python' }
        { name: 'AzureWebJobsStorage', value: storage.properties.primaryEndpoints.blob }
        { name: 'WEBSITE_RUN_FROM_PACKAGE', value: '1' }
      ]
    }
  }
  identity: {
    type: 'SystemAssigned'
  }
  dependsOn: [ storage, plan ]
}

// ---------- Outputs ----------
output functionAppName string = functionApp.name
output storageAccount string = storage.name
