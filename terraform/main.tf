resource "kubernetes_namespace" "bookbug" {
  metadata {
    name = var.namespace
  }
}

resource "kubernetes_deployment" "backend" {
  metadata {
    name      = "bookbug-backend"
    namespace = kubernetes_namespace.bookbug.metadata[0].name
    labels = {
      app = "bookbug-backend"
    }
  }

  spec {
    replicas = 2

    selector {
      match_labels = {
        app = "bookbug-backend"
      }
    }

    template {
      metadata {
        labels = {
          app = "bookbug-backend"
        }
      }

      spec {
        container {
          image = "${var.dockerhub_username}/bookbug-backend:latest"
          name  = "backend"

          port {
            container_port = 8000
          }

          liveness_probe {
            http_get {
              path = "/health"
              port = 8000
            }
            initial_delay_seconds = 10
            period_seconds        = 10
          }

          readiness_probe {
            http_get {
              path = "/health"
              port = 8000
            }
            initial_delay_seconds = 5
            period_seconds        = 10
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "backend" {
  metadata {
    name      = "bookbug-backend-service"
    namespace = kubernetes_namespace.bookbug.metadata[0].name
  }

  spec {
    selector = {
      app = "bookbug-backend"
    }

    type = "NodePort"

    port {
      port        = 8000
      target_port = 8000
      node_port   = 30080
    }
  }
}

resource "kubernetes_deployment" "frontend" {
  metadata {
    name      = "bookbug-frontend"
    namespace = kubernetes_namespace.bookbug.metadata[0].name
    labels = {
      app = "bookbug-frontend"
    }
  }

  spec {
    replicas = 2

    selector {
      match_labels = {
        app = "bookbug-frontend"
      }
    }

    template {
      metadata {
        labels = {
          app = "bookbug-frontend"
        }
      }

      spec {
        container {
          image = "${var.dockerhub_username}/bookbug-frontend:latest"
          name  = "frontend"

          port {
            container_port = 80
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "frontend" {
  metadata {
    name      = "bookbug-frontend-service"
    namespace = kubernetes_namespace.bookbug.metadata[0].name
  }

  spec {
    selector = {
      app = "bookbug-frontend"
    }

    type = "NodePort"

    port {
      port        = 80
      target_port = 80
      node_port   = 30081
    }
  }
}
