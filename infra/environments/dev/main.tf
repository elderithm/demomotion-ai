terraform {
  required_version = ">= 1.6.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.40.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

locals {
  apis = [
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "storage.googleapis.com",
    "aiplatform.googleapis.com",
    "texttospeech.googleapis.com",
    "cloudbuild.googleapis.com",
    "iam.googleapis.com",
    "iamcredentials.googleapis.com",
    "sts.googleapis.com",
    "logging.googleapis.com"
  ]
}

resource "google_project_service" "apis" {
  for_each           = toset(local.apis)
  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

resource "google_artifact_registry_repository" "repo" {
  location      = var.region
  repository_id = var.name
  description   = "DemoMotion AI containers"
  format        = "DOCKER"
  depends_on    = [google_project_service.apis]
}

resource "google_storage_bucket" "outputs" {
  name                        = "${var.project_id}-${var.name}-outputs"
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = true

  lifecycle_rule {
    condition { age = 14 }
    action { type = "Delete" }
  }

  depends_on = [google_project_service.apis]
}

resource "google_service_account" "runtime" {
  account_id   = "${var.name}-runtime"
  display_name = "DemoMotion AI runtime"
}

resource "google_project_iam_member" "runtime_vertex" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.runtime.email}"
}

# Cloud Text-to-Speech has no method-level IAM roles: any authenticated identity
# in a project with the API enabled can call it. No dedicated binding is needed
# for the runtime service account (add roles/serviceusage.serviceUsageConsumer
# only if synthesis calls return 403).

resource "google_storage_bucket_iam_member" "runtime_storage" {
  bucket = google_storage_bucket.outputs.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.runtime.email}"
}

# Let the runtime service account sign V4 URLs for private bucket objects via the
# IAM signBlob API (self-impersonation), so the API can hand the browser a
# time-limited playable URL without making the bucket public.
resource "google_service_account_iam_member" "runtime_sign" {
  service_account_id = google_service_account.runtime.name
  role               = "roles/iam.serviceAccountTokenCreator"
  member             = "serviceAccount:${google_service_account.runtime.email}"
}

# --- Keyless CI: Workload Identity Federation for GitHub Actions ---------------
# Lets this repo's GitHub Actions impersonate the runtime service account using a
# short-lived OIDC token, so CI can run vertex/TTS with no long-lived key. This
# only trusts var.github_repository; OSS consumers set up their own WIF.

resource "google_iam_workload_identity_pool" "github" {
  workload_identity_pool_id = "github"
  display_name              = "GitHub Actions"
  description               = "OIDC federation for GitHub Actions CI"
  depends_on                = [google_project_service.apis]
}

resource "google_iam_workload_identity_pool_provider" "github" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.github.workload_identity_pool_id
  workload_identity_pool_provider_id = "github"
  display_name                       = "GitHub"
  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.repository" = "assertion.repository"
  }
  # Only accept tokens minted for our repository.
  attribute_condition = "assertion.repository == \"${var.github_repository}\""
  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}

resource "google_service_account_iam_member" "github_ci_impersonation" {
  service_account_id = google_service_account.runtime.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github.name}/attribute.repository/${var.github_repository}"
}

# serviceusage.services.use is required to set a billing/quota project on API
# calls (e.g. Text-to-Speech, and the impersonation call itself) — needed when
# the credentials don't natively carry one, as with federated/impersonated CI
# identities. Grant it to both the federated principal (which performs the
# impersonation) and the runtime SA (which then calls the APIs).
resource "google_project_iam_member" "ci_principal_serviceusage" {
  project = var.project_id
  role    = "roles/serviceusage.serviceUsageConsumer"
  member  = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github.name}/attribute.repository/${var.github_repository}"
}

resource "google_project_iam_member" "runtime_serviceusage" {
  project = var.project_id
  role    = "roles/serviceusage.serviceUsageConsumer"
  member  = "serviceAccount:${google_service_account.runtime.email}"
}
# ------------------------------------------------------------------------------

resource "google_cloud_run_v2_service" "api" {
  name     = "${var.name}-api"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.runtime.email
    scaling {
      min_instance_count = 0
      # Jobs run as in-process FastAPI BackgroundTasks against an in-memory
      # store, so all requests for a job (create + poll + download) must land on
      # the same instance. Cap at 1 until the pipeline moves to a shared store
      # and a real queue.
      max_instance_count = 1
    }
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${var.name}/api:latest"
      resources {
        limits = { cpu = "2", memory = "2Gi" }
        # CPU must stay allocated after the HTTP response returns, otherwise the
        # background video pipeline is starved of CPU.
        cpu_idle = false
      }
      env {
        name  = "APP_ENV"
        value = "cloud"
      }
      env {
        name  = "AI_PROVIDER"
        value = "vertex"
      }
      env {
        name  = "TTS_PROVIDER"
        value = "google"
      }
      env {
        name  = "STORAGE_PROVIDER"
        value = "gcs"
      }
      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }
      env {
        name  = "GCP_LOCATION"
        value = var.region
      }
      env {
        name  = "GCS_BUCKET"
        value = google_storage_bucket.outputs.name
      }
      # Allow the browser dashboard's origin through CORS. Referencing the web
      # service's URL here (and not referencing the api URL from the web service)
      # keeps the dependency one-directional and avoids a cycle.
      env {
        name  = "CORS_ORIGINS"
        value = google_cloud_run_v2_service.web.uri
      }
    }
  }

  depends_on = [google_project_service.apis]
}

resource "google_cloud_run_v2_service_iam_member" "api_public" {
  location = google_cloud_run_v2_service.api.location
  name     = google_cloud_run_v2_service.api.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}


resource "google_cloud_run_v2_service" "web" {
  name     = "${var.name}-web"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    scaling {
      min_instance_count = 0
      max_instance_count = 2
    }
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${var.name}/web:latest"
      resources {
        limits   = { cpu = "1", memory = "512Mi" }
        cpu_idle = true
      }
      # NEXT_PUBLIC_API_BASE_URL is inlined into the web bundle at build time
      # (passed as a Docker build arg), so no runtime env is needed here. Keeping
      # this service free of any reference to the api URL also avoids a
      # dependency cycle with the api service's CORS_ORIGINS.

      # HTTP Basic auth gate, read by the Next.js middleware at runtime.
      env {
        name  = "BASIC_AUTH_USER"
        value = var.basic_auth_user
      }
      env {
        name  = "BASIC_AUTH_PASS"
        value = var.basic_auth_pass
      }
    }
  }

  depends_on = [google_project_service.apis]
}

resource "google_cloud_run_v2_service_iam_member" "web_public" {
  location = google_cloud_run_v2_service.web.location
  name     = google_cloud_run_v2_service.web.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

output "api_url" {
  value = google_cloud_run_v2_service.api.uri
}

output "web_url" {
  value = google_cloud_run_v2_service.web.uri
}

output "bucket" {
  value = google_storage_bucket.outputs.name
}

# Feed these to google-github-actions/auth in this repo's CI (not secrets).
output "wif_provider" {
  description = "workload_identity_provider for google-github-actions/auth"
  value       = google_iam_workload_identity_pool_provider.github.name
}

output "ci_service_account" {
  description = "service_account to impersonate from CI"
  value       = google_service_account.runtime.email
}
