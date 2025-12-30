# Backup and Restore Procedures

This document outlines the backup and restore strategies for the Nebulus project.

## Overview
Nebulus uses persistent Docker volumes to store data for:
- **Ollama**: Models and configuration.
- **ChromaDB**: Vector database embeddings.
- **Open WebUI**: User accounts, chats, and settings.

To ensure data safety, we employ an automated script that creates compressed tarballs of these volumes.

## Backup Process

### Automated Backups
Run the backup command via the Nebulus CLI:

```bash
nebulus backup
```

Or manually using the script:

```bash
./scripts/backup.sh
```

**What it does:**
1.  Creates a directory `backups/` in the project root.
2.  Stops running containers (transiently) or pauses I/O if configured (currently using `docker run` to mount volumes alongside).
3.  Tars the contents of `nebulus_ollama_data`, `nebulus_chroma_data`, and `nebulus_webui_data`.
4.  Saves files as `volumename_YYYYMMDD_HHMMSS.tar.gz`.
5.  **Retention Policy**: Automatically deletes backups older than **30 days**.

## Restore Process

### Restoration
To restore a specific backup, use the Nebulus CLI:

```bash
nebulus restore
```

This interactive command will:
1.  List available backups.
2.  Ask which backup to restore.
3.  Ask which volume to restore it to.

Or run manually:

```bash
./scripts/restore.sh <backup_filename> <volume_name>
```

**Example:**
```bash
./scripts/restore.sh nebulus_webui_data_20230101_120000.tar.gz nebulus_webui_data
```

> [!WARNING]
> Restoring a backup will **OVERWRITE** all existing data in the target volume. It is recommended to perform a backup of the current state before restoring.

## Troubleshooting

### "Volume in use" Error
If you cannot restore because the volume is in use, ensure all services are stopped:

```bash
nebulus down
```

Then run the restore script.
