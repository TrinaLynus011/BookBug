$ErrorActionPreference = 'Stop'

Write-Host 'Stopping BookBug containers...'
docker compose down
Write-Host 'BookBug stack stopped.'
