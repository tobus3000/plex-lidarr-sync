# Development Notes

## Docker Image Publishing

### Building

To build the image locally:

```bash
docker build -t tobotec/plex-lidarr-sync:tagname .
```

Replace `tagname` with your desired tag (e.g., `latest`, `v1.0.2`, etc.)

### Pushing to Docker Hub

1. **Log in to Docker Hub**:

```bash
docker login
```

1. **Tag the image** (if not already tagged):

```bash
docker tag plex-lidarr-sync:tagname tobotec/plex-lidarr-sync:tagname
```

1. **Push to Docker Hub**:

```bash
docker push tobotec/plex-lidarr-sync:tagname
```

To push multiple tags at once:

```bash
docker build -t tobotec/plex-lidarr-sync:tagname -t tobotec/plex-lidarr-sync:latest .
docker push tobotec/plex-lidarr-sync:tagname
docker push tobotec/plex-lidarr-sync:latest
```