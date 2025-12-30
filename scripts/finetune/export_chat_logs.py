#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
import os


def export_logs(output_file, volume_name="webui_data"):
    """
    Exports chat logs from the running WebUI docker volume using a temporary container.
    """
    print(f"Exporting chat logs from volume '{volume_name}'...")

    # Inner script content
    inner_script = r"""
import sqlite3
import json
import os
import sys

try:
    if not os.path.exists('/data/webui.db'):
        print(json.dumps({'error': 'Database file /data/webui.db not found'}))
        sys.exit(0)

    conn = sqlite3.connect('/data/webui.db')
    cursor = conn.cursor()

    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [r[0] for r in cursor.fetchall()]

    results = []

    # Extract from 'chat' table (standard Open WebUI structure)
    if 'chat' in tables:
        cursor.execute("SELECT id, user_id, title, chat, created_at FROM chat")
        rows = cursor.fetchall()
        for row in rows:
            try:
                chat_data = json.loads(row[3]) if row[3] else {}
                results.append({
                    'id': row[0],
                    'user_id': row[1],
                    'title': row[2],
                    'chat': chat_data,
                    'created_at': row[4]
                })
            except:
                pass

    print(json.dumps(results))

except Exception as e:
    print(json.dumps({'error': str(e)}))
"""

    # Write inner script to temp file
    temp_script_path = os.path.join(os.getcwd(), "temp_export_script.py")
    with open(temp_script_path, "w") as f:
        f.write(inner_script)

    cmd = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{volume_name}:/data",  # noqa: E231
        "-v",
        f"{temp_script_path}:/script.py",  # noqa: E231
        "python:3.11-slim",
        "python",
        "/script.py",
    ]

    try:
        # Run docker command
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # Cleanup temp file
        if os.path.exists(temp_script_path):
            os.remove(temp_script_path)

        try:
            data = json.loads(result.stdout.strip())
        except json.JSONDecodeError:
            print(f"Failed to parse output: {result.stdout}")
            sys.exit(1)

        if isinstance(data, dict) and "error" in data:
            print(f"Error from internal script: {data['error']}")
            sys.exit(1)

        # Save to file
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w") as f:
            for entry in data:
                f.write(json.dumps(entry) + "\n")

        print(f"Successfully exported {len(data)} chats to {output_file}")

    except subprocess.CalledProcessError as e:
        print(f"Docker command failed: {e.stderr}")
        if os.path.exists(temp_script_path):
            os.remove(temp_script_path)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export Open WebUI chat logs.")
    parser.add_argument(
        "--output",
        "-o",
        default="data/datasets/raw_chats.jsonl",
        help="Output JSONL file",
    )
    parser.add_argument(
        "--volume", "-v", default="nebulus_webui_data", help="Docker volume name"
    )

    args = parser.parse_args()
    export_logs(args.output, args.volume)
