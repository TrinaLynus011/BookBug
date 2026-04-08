$ErrorActionPreference = 'Stop'

Write-Host 'Building and starting BookBug containers...'
docker compose up --build -d

$maxAttempts = 20
$attempt = 0
$backendReady = $false

while (-not $backendReady -and $attempt -lt $maxAttempts) {
  $attempt++
  try {
    $response = Invoke-WebRequest -Uri 'http://localhost:8000/health' -UseBasicParsing -TimeoutSec 3
    if ($response.StatusCode -eq 200) {
      $backendReady = $true
      break
    }
  } catch {
    Start-Sleep -Seconds 2
  }
}

if (-not $backendReady) {
  throw 'Backend health check failed after startup.'
}

Write-Host 'BookBug is running.'
Write-Host 'Frontend: http://localhost:3000'
Write-Host 'Backend: http://localhost:8000'
Write-Host 'Health: http://localhost:8000/health'
