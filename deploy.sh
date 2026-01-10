echo "Please enter the admin password for the PostgreSQL database:"
read -s adminPassword

registryPassword=$(az acr credential show --name procguardacr --query "passwords[0].value" -o tsv)

az group create -n procguard-rg -l eastus

az deployment group create \
  -g procguard-rg \
  -f infra/main.bicep \
  --parameters adminPassword=$adminPassword registryPassword=$registryPassword