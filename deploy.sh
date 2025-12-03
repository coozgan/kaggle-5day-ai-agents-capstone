#!/bin/bash

# Jarbest Deployment Script
# Deploys all 4 services to Google Cloud Run

# Exit on error
set -e

# Configuration
PROJECT_ID=$(gcloud config get-value project)
REGION="us-central1"
IMAGE_NAME="gcr.io/$PROJECT_ID/jarbest-unified"

# Check for required environment variable
if [ -z "$GOOGLE_API_KEY" ]; then
  echo "❌ Error: GOOGLE_API_KEY environment variable is required"
  echo "   Set it with: export GOOGLE_API_KEY='your-api-key'"
  exit 1
fi

echo "🚀 Starting deployment for Project: $PROJECT_ID in Region: $REGION"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "❌ Error: Docker is not running. Please start Docker and try again."
  exit 1
fi

# 1. Build the Unified Docker image
echo "🔨 Building Unified Docker image..."
docker build -t $IMAGE_NAME . --platform linux/amd64

# 2. Push the image to Google Container Registry
echo "pushing image to GCR..."
docker push $IMAGE_NAME

# 3. Deploy Bank MCP Server
echo "☁️  Deploying Bank MCP Server..."
gcloud run deploy jarbest-bank-mcp \
  --image $IMAGE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --command "python" \
  --args "simulated_environment/bank_mcp/server.py"

BANK_URL=$(gcloud run services describe jarbest-bank-mcp --platform managed --region $REGION --format 'value(status.url)')
echo "✅ Bank MCP deployed at: $BANK_URL"

# 4. Deploy Pizza Agent
echo "☁️  Deploying Pizza Agent..."
gcloud run deploy jarbest-pizza-agent \
  --image $IMAGE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars "MODEL=gemini-2.5-flash,GOOGLE_API_KEY=$GOOGLE_API_KEY" \
  --command "python" \
  --args "simulated_environment/pizza_shop_agent/pizza_shop/agent.py"

PIZZA_URL=$(gcloud run services describe jarbest-pizza-agent --platform managed --region $REGION --format 'value(status.url)')
echo "✅ Pizza Agent deployed at: $PIZZA_URL"

# Update Pizza Agent with A2A Host
echo "🔄 Updating Pizza Agent configuration..."
PIZZA_HOST=$(echo $PIZZA_URL | awk -F/ '{print $3}')
gcloud run services update jarbest-pizza-agent \
  --region $REGION \
  --set-env-vars "MODEL=gemini-2.5-flash,GOOGLE_API_KEY=$GOOGLE_API_KEY,A2A_HOST=$PIZZA_HOST,A2A_PROTOCOL=https,A2A_PORT=443"

# 5. Deploy Ecommerce Agent
echo "☁️  Deploying Ecommerce Agent..."
gcloud run deploy jarbest-ecommerce-agent \
  --image $IMAGE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars "MODEL=gemini-2.5-flash,GOOGLE_API_KEY=$GOOGLE_API_KEY" \
  --command "python" \
  --args "simulated_environment/ecommerce_agent/ecommerce_agent/agent.py"

ECOMMERCE_URL=$(gcloud run services describe jarbest-ecommerce-agent --platform managed --region $REGION --format 'value(status.url)')
echo "✅ Ecommerce Agent deployed at: $ECOMMERCE_URL"

# Update Ecommerce Agent with A2A Host
echo "🔄 Updating Ecommerce Agent configuration..."
ECOMMERCE_HOST=$(echo $ECOMMERCE_URL | awk -F/ '{print $3}')
gcloud run services update jarbest-ecommerce-agent \
  --region $REGION \
  --set-env-vars "MODEL=gemini-2.5-flash,GOOGLE_API_KEY=$GOOGLE_API_KEY,A2A_HOST=$ECOMMERCE_HOST,A2A_PROTOCOL=https,A2A_PORT=443"

# 6. Deploy Personal Agent UI
echo "☁️  Deploying Jarbest Personal Agent UI..."
uv run adk deploy cloud_run \
  --project=$PROJECT_ID \
  --region=$REGION \
  --service_name=jarbest-personal-agent-ui \
  --with_ui \
  personal_agent \
  -- \
  --set-env-vars="MODEL=gemini-3-pro-preview,GOOGLE_API_KEY=$GOOGLE_API_KEY,BANK_USER_ID=acc_12345,BANK_MCP_URL=$BANK_URL,PIZZA_AGENT_URL=$PIZZA_URL,ECOMMERCE_AGENT_URL=$ECOMMERCE_URL" \
  --allow-unauthenticated

UI_URL=$(gcloud run services describe jarbest-personal-agent-ui --platform managed --region $REGION --format 'value(status.url)')
echo "🎉 UI Deployment Complete!"
echo "🖥️  Jarbest UI is live at: $UI_URL"
