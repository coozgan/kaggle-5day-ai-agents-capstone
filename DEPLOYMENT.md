# Cloud Run Deployment Guide

## Prerequisites

1. **Google Cloud Project** with billing enabled
2. **gcloud CLI** installed and authenticated
3. **Docker** installed and running
4. **Google API Key** from [Google AI Studio](https://aistudio.google.com/)

## Pre-Deployment Setup

### 1. Authenticate with Google Cloud
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### 2. Configure Docker for GCR
```bash
gcloud auth configure-docker
```

### 3. Set Required Environment Variable
```bash
export GOOGLE_API_KEY='your-google-api-key-here'
```

**Important**: This API key will be passed to all services and is required for Gemini API access.

## Deploy to Cloud Run

### Single Command Deployment
```bash
chmod +x deploy.sh
./deploy.sh
```

This will:
1. Build a unified Docker image for all services
2. Push it to Google Container Registry (GCR)
3. Deploy 4 services:
   - Bank MCP Server
   - Pizza Agent (with A2A configuration)
   - Ecommerce Agent (with A2A configuration)
   - Personal Agent UI (ADK web interface)

### Expected Output
```
🚀 Starting deployment for Project: your-project-id in Region: us-central1
🔨 Building Unified Docker image...
☁️  Deploying Bank MCP Server...
✅ Bank MCP deployed at: https://jarbest-bank-mcp-xxx.run.app
☁️  Deploying Pizza Agent...
✅ Pizza Agent deployed at: https://jarbest-pizza-agent-xxx.run.app
🔄 Updating Pizza Agent configuration...
☁️  Deploying Ecommerce Agent...
✅ Ecommerce Agent deployed at: https://jarbest-ecommerce-agent-xxx.run.app
🔄 Updating Ecommerce Agent configuration...
☁️  Deploying Jarbest Personal Agent UI...
🎉 UI Deployment Complete!
🖥️  Jarbest UI is live at: https://jarbest-personal-agent-ui-xxx.run.app
```

## What Changed from Local Docker Compose?

### Environment Variables
- **Local**: Uses service names like `http://bank-mcp:8888`
- **Cloud Run**: Uses full HTTPS URLs like `https://jarbest-bank-mcp-xxx.run.app`

### A2A Configuration
- **Local**: `A2A_HOST=pizza-agent`, `A2A_PROTOCOL=http`, `A2A_PORT=8080` (or agent specific port)
- **Cloud Run**: `A2A_HOST=jarbest-pizza-agent-xxx.run.app`, `A2A_PROTOCOL=https`, `A2A_PORT=443`

### Port Configuration
- **Local**: Different ports (8888, 10000, 11000, 8080)
- **Cloud Run**: All services use port 8080 (Cloud Run standard)

### Authentication
- **Local**: Uses mounted Google credentials file
- **Cloud Run**: Uses `GOOGLE_API_KEY` environment variable

## Testing Your Deployment

### 1. Test Bank MCP
```bash
curl https://jarbest-bank-mcp-YOUR-URL.run.app/health
```

### 2. Test Pizza Agent A2A Card
```bash
curl https://jarbest-pizza-agent-YOUR-URL.run.app/.well-known/agent-card.json
```

### 3. Access Personal Agent UI
Open the UI URL in your browser:
```
https://jarbest-personal-agent-ui-YOUR-URL.run.app
```

Try these queries:
- "What's my bank balance?"
- "Order a pepperoni pizza"
- "Find a gaming laptop"
- "Order a pizza if I can afford it"

## Troubleshooting

### Check Service Logs
```bash
# Bank MCP logs
gcloud run services logs read jarbest-bank-mcp --region us-central1

# Pizza Agent logs
gcloud run services logs read jarbest-pizza-agent --region us-central1

# Ecommerce Agent logs
gcloud run services logs read jarbest-ecommerce-agent --region us-central1

# Personal Agent logs
gcloud run services logs read jarbest-personal-agent-ui --region us-central1
```

### Common Issues

#### "GOOGLE_API_KEY not set"
```bash
export GOOGLE_API_KEY='your-api-key'
./deploy.sh
```

#### "Docker is not running"
Start Docker Desktop and try again.

#### "Permission denied" when running deploy.sh
```bash
chmod +x deploy.sh
```

#### Services failing with authentication errors
Verify your API key is valid:
```bash
echo $GOOGLE_API_KEY
```

#### A2A agent card not found
The A2A host configuration happens in a second update step. Wait for the update to complete.

## Updating Services

### Update a Single Service
```bash
# Update Pizza Agent
gcloud run deploy jarbest-pizza-agent \
  --image gcr.io/YOUR_PROJECT_ID/jarbest-unified:latest \
  --region us-central1
```

### Update Environment Variables Only
```bash
gcloud run services update jarbest-personal-agent-ui \
  --region us-central1 \
  --set-env-vars "MODEL=gemini-2.5-flash"
```

## Cleanup

### Delete All Services
```bash
gcloud run services delete jarbest-bank-mcp --region us-central1 --quiet
gcloud run services delete jarbest-pizza-agent --region us-central1 --quiet
gcloud run services delete jarbest-ecommerce-agent --region us-central1 --quiet
gcloud run services delete jarbest-personal-agent-ui --region us-central1 --quiet
```

### Delete Docker Images
```bash
gcloud container images delete gcr.io/YOUR_PROJECT_ID/jarbest-unified --quiet
```

## Cost Considerations

Cloud Run pricing is based on:
- **Requests**: First 2 million requests/month are free
- **Compute time**: Billed per 100ms of execution time
- **Memory**: Based on allocated memory

For this demo project with moderate usage, costs should be minimal (likely within free tier).

## Security Notes

1. **API Keys**: Currently passed as environment variables. For production, use Secret Manager.
2. **Authentication**: Services are deployed with `--allow-unauthenticated` for demo purposes.
3. **HTTPS**: All Cloud Run services automatically use HTTPS.

## Next Steps

1. Add Secret Manager integration for API keys
2. Set up Cloud Run authentication (remove `--allow-unauthenticated`)
3. Configure custom domains
4. Set up monitoring and alerts
5. Implement persistent storage (replace InMemoryMemoryService)
