output "frontend_node_port" {
  value = kubernetes_service.frontend.spec[0].port[0].node_port
}

output "backend_node_port" {
  value = kubernetes_service.backend.spec[0].port[0].node_port
}
