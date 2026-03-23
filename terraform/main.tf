resource "kubernetes_namespace" "bookbee" {
  metadata {
    name = var.namespace
  }
}

resource "kubernetes_deployment" "backend" {
  metadata {
    name      = "bookbee-backend"
    namespace = kubernetes_namespace.bookbee.metadata[0].name
    labels = {
      app = "bookbee-backend"
    }
  }

  spec {
    replicas = 2

    selector {
      match_labels = {
        app = "bookbee-backend"
      }
    }

    template {
      metadata {
        labels = {
          app = "bookbee-backend"
        }
      }

      spec {
        container {
          image = "${var.dockerhub_username}/bookbee-backend:latest"
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
    name      = "bookbee-backend-service"
    namespace = kubernetes_namespace.bookbee.metadata[0].name
  }

  spec {
    selector = {
      app = "bookbee-backend"
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
    name      = "bookbee-frontend"
    namespace = kubernetes_namespace.bookbee.metadata[0].name
    labels = {
      app = "bookbee-frontend"
    }
  }

  spec {
    replicas = 2

    selector {
      match_labels = {
        app = "bookbee-frontend"
      }
    }

    template {
      metadata {
        labels = {
          app = "bookbee-frontend"
        }
      }

      spec {
        container {
          image = "${var.dockerhub_username}/bookbee-frontend:latest"
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
    name      = "bookbee-frontend-service"
    namespace = kubernetes_namespace.bookbee.metadata[0].name
  }

  spec {
    selector = {
      app = "bookbee-frontend"
    }

    type = "NodePort"

    port {
      port        = 80
      target_port = 80
      node_port   = 30081
    }
  }
}
