# Git Workflow

## Branch model

- `main`: production-ready branch
- `develop`: integration branch for upcoming release
- `feature/<name>`: isolated feature work

## Suggested flow (solo or team)

1. `git checkout develop`
2. `git pull origin develop`
3. `git checkout -b feature/recommendation-history-ui`
4. Commit using meaningful prefixes:
   - `feat: add weighted recommendation endpoint`
   - `fix: handle unknown genre with 404`
   - `chore: update ci cache keys`
5. Open Pull Request from `feature/*` to `develop`
6. Squash or merge after checks pass
7. Raise PR from `develop` to `main` for release

## Pull request checklist

- [ ] Tests pass (backend + frontend)
- [ ] Lint passes
- [ ] Docker builds locally
- [ ] Kubernetes manifests still valid
- [ ] README updated if behavior changed
