targetScope = 'resourceGroup'

param location string = resourceGroup().location
param adminPassword string

module storage 'storage.bicep' = {
  name: 'storage-deploy'
  params: {
    location: location
  }
}

module postgres 'postgres.bicep' = {
  name: 'postgres-deploy'
  params: {
    location: location
    administratorLoginPassword: adminPassword
  }
}

module containerApp 'container.bicep' = {
  name: 'container-deploy'
  params: {
    location: location
    dbHost: postgres.outputs.host
    storageAccountName: storage.outputs.accountName
  }
}
