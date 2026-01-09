az group create -n procguard-rg -l eastus

az deployment group create \
  -g procguard-rg \
  -f infra/main.bicep

az containerapp update \
  --name procguard-api \
  --resource-group procguard-rg \
  --image procguard:latest
