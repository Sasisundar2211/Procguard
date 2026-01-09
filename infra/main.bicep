module postgres './postgres.bicep' = {
  name: 'postgres'
}

module storage './storage.bicep' = {
  name: 'storage'
}

module app './containerapp.bicep' = {
  name: 'app'
}
