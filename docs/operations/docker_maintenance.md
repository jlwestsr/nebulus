# Docker Maintenance Guide

To prevent high CPU usage (Daemon "death spirals") and disk bloat, we recommend periodic maintenance of the Docker environment.

## The Script

A maintenance script is available at `scripts/docker_maintain.sh`.

It performs the following safe actions:

1. **Prunes Dangling Images**: Removes intermediate layers that are no longer referenced by any tagged image. This resolves the `snapshotter.Stat` recursion bugs.
2. **Prunes Build Cache**: Removes build cache entries older than 48 hours.

## Manual Execution

You can run the script manually at any time:

```bash
./scripts/docker_maintain.sh
```

## Scheduled Maintenance (Recommended)

To run this automatically (e.g., weekly), you can add it to your user's crontab.

1. Open crontab:

    ```bash
    crontab -e
    ```

2. Add the following line (adjust path to match your project location):

    ```cron
    # Run Docker maintenance every Sunday at 3 AM
    0 3 * * 0 /home/jlwestsr/projects/west_ai_labs/nebulus/scripts/docker_maintain.sh >> /tmp/nebulus_docker_maintain.log 2>&1
    ```
