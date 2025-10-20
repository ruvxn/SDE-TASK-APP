# Jenkins (local) with Docker Desktop

Run Jenkins locally in Docker with access to your host's Docker engine.

## Start
```bash
cd jenkins-local
docker compose build
docker compose up -d
```
Unlock Jenkins at http://localhost:8080 using the admin password:
```bash
docker logs jenkins 2>&1 | grep -A 2 "Please use the following password"
# or
docker exec -it jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

## Recommended plugins
Git, Pipeline, Blue Ocean (optional), Credentials Binding, JUnit, GitHub Branch Source.

## Create Pipeline job
- New Item → Pipeline → Pipeline script from SCM → Git repo URL → Branch (e.g., */main) → Script Path: Jenkinsfile → Save → Build Now.

## Troubleshooting
- If docker permission error, restart the container (group membership refresh).
- If port 8080 is busy, map to 8090: `"8090:8080"`.
