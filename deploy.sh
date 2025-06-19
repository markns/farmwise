# Set environment variables for clarity
PROJECT_ID="farmwise-462814"
REGION="europe-west4"
FARMBASE_IMAGE="europe-west4-docker.pkg.dev/$PROJECT_ID/farmwise/farmbase:1.0.0"
FARMWISE_IMAGE="europe-west4-docker.pkg.dev/$PROJECT_ID/farmwise/farmwise:1.0.0"
FARMBASE_SERVICE_ACCOUNT="farmbase-sa@$PROJECT_ID.iam.gserviceaccount.com" # The SA you created
DB_CONNECTION_NAME="$PROJECT_ID:$REGION:farmbase"
GCS_BUCKET=gs://farmbase_data

# First, create the API service account
gcloud iam service-accounts create farmbase-sa \
  --display-name="API Service Account" \
  --description="Service account for the FarmBase API to connect to Cloud SQL"

# Grant the Cloud SQL Client role to the API service account
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:farmbase-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"

gcloud storage buckets add-iam-policy-binding $GCS_BUCKET \
    --member="serviceAccount:farmbase-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"

# Second, create the Chatbot service account
gcloud iam service-accounts create farmwise-sa \
  --display-name="Chatbot Service Account" \
  --description="Service account for the chatbot to invoke the API service"

gcloud storage buckets add-iam-policy-binding $GCS_BUCKET \
    --member="serviceAccount:farmwise-sa@farmwise-462814.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"

#--allow-unauthenticated: This makes the API public so your React app (running in users' browsers)
# and your chatbot can access it. You will secure it with CORS and IAM.

# --add-cloudsql-instances: This is the magic flag. It automatically injects the Cloud SQL Auth Proxy
# as a sidecar container and configures it to listen on localhost.

# Deploy command
gcloud run deploy farmbase \
  --image=$FARMBASE_IMAGE \
  --allow-unauthenticated \
  --region=$REGION \
  --service-account=$FARMBASE_SERVICE_ACCOUNT \
  --add-cloudsql-instances=$DB_CONNECTION_NAME \
  --project=$PROJECT_ID

# TODO: Important: Your API must implement CORS (Cross-Origin Resource Sharing) so that your
#   React app, served from its Firebase domain, is allowed to make requests to your API domain.

# Grant the Cloud Run Invoker role to the chatbot service account ON the farmbase service
gcloud run services add-iam-policy-binding farmbase \
  --member="serviceAccount:farmwise-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.invoker" \
  --region=$REGION \
  --project=$PROJECT_ID

  
CHATBOT_SA="chatbot-sa@$PROJECT_ID.iam.gserviceaccount.com"

gcloud run deploy chatbot-service \
  --image=$FARMWISE_IMAGE \
  --ingress=internal-and-cloud-load-balancing `# Or 'all' if it needs a public webhook` \
  --region=$REGION \
  --service-account=$CHATBOT_SA \
  --project=$PROJECT_ID  