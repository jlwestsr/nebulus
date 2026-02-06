#!/usr/bin/env python3
"""
Model Downloader for Nebulus Prime (TabbyAPI)
Downloads specific revisions (quantizations) of models from Hugging Face.
"""

import sys
import argparse
from pathlib import Path
from huggingface_hub import snapshot_download

MODELS_DIR = Path(
    "/home/jlwestsr/projects/west_ai_labs/nebulus/data/models"
)  # Mapped to models_data volume?
# Wait, docker volume is 'models_data'. If we want to download from host, we need to know where docker stores it
# OR we update docker-compose to bind mount a host directory.
# Strategy: Bind mount ./models to /app/models in docker-compose for easy access.
# I will adhere to the plan but I need to make sure I update docker-compose to bind mount if I want this script to work easily from host.
# OR I can run this script inside a container.
# BETTER: Update docker-compose to bind mount ./models -> /app/models.


def download_model(repo_id: str, revision: str = None):
    print(f"Downloading {repo_id} (Revision: {revision or 'main'})...")

    # Extract model name for local directory
    model_name = repo_id.split("/")[-1]
    if revision:
        model_name += f"-{revision}"

    local_dir = Path("models") / model_name

    try:
        snapshot_download(
            repo_id=repo_id,
            revision=revision,
            local_dir=local_dir,
            local_dir_use_symlinks=False,
            resume_download=True,
        )
        print(f"\nSuccessfully downloaded to {local_dir}")
        print("You can now load this model in TabbyAPI/OpenWebUI.")
    except Exception as e:
        print(f"\nError downloading model: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download EXL2 models for TabbyAPI")
    parser.add_argument(
        "repo_id",
        help="Hugging Face Repo ID (e.g., turboderp/Llama-3-8B-Instruct-exl2)",
    )
    parser.add_argument(
        "--revision", "-r", help="Specific branch/revision (e.g., 6.0bpw)", default=None
    )

    args = parser.parse_args()
    download_model(args.repo_id, args.revision)
