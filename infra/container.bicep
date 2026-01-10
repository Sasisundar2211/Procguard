param location string
param dbHost string
param storageAccountName string
param registryPassword string
param adminPassword string

resource containerAppEnvironment 'Microsoft.App/managedEnvironments@2022-03-01' = {
  name: 'procguard-env'
  location: location
}

resource containerApp 'Microsoft.App/containerApps@2022-03-01' = {
  name: 'procguard-api'
  location: location
  properties: {
    managedEnvironmentId: containerAppEnvironment.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
      }
      secrets: [
        {
          name: 'registry-password'
          value: registryPassword
        }
      ]
      registries: [
        {
          server: 'procguardacr.azurecr.io'
          username: 'procguardacr'
          passwordSecretRef: 'registry-password'
        }
      ]
    }
    template: {
      containers: [
        {
          image: 'procguardacr.azurecr.io/procguard-api:latest'
          name: 'procguard-api'
          env: [
            {
              name: 'DATABASE_URL'
              value: 'postgresql://postgres:${adminPassword}@${dbHost}/postgres'
            }
          ]
          resources: {
            cpu: json('0.5')
            memory: '1.0Gi'
          }
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 1
      }
    }
  }
}
