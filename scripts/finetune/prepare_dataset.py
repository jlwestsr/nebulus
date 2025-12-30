#!/usr/bin/env python3
import argparse
import json
import os
import sys


def prepare_dataset(input_file, output_file):
    """
    Converts raw Open WebUI chat logs to ShareGPT format for fine-tuning.
    """
    print(f"Processing {input_file}...")

    if not os.path.exists(input_file):
        print(f"Input file {input_file} not found.")
        sys.exit(1)

    processed_count = 0
    skipped_count = 0

    data_buffer = []

    with open(input_file, "r") as f:
        for line in f:
            try:
                raw_entry = json.loads(line)

                # Check if it has messages
                chat_content = raw_entry.get("chat", {})
                messages = chat_content.get("messages", [])

                if not messages:
                    skipped_count += 1
                    continue

                # Format for ShareGPT:
                # {"conversations": [{"from": "human", "value": "..."},
                #                    {"from": "gpt", "value": "..."}]}
                conversations = []

                for msg in messages:
                    role = msg.get("role")
                    content = msg.get("content")

                    if not content:
                        continue

                    if role == "user":
                        conversations.append({"from": "human", "value": content})
                    if role == "assistant":
                        conversations.append({"from": "gpt", "value": content})
                    # Skip system prompts for now, or map to 'system' if supported

                if len(conversations) >= 2:  # At least one turn
                    data_buffer.append({"conversations": conversations})
                    processed_count += 1
                else:
                    skipped_count += 1

            except json.JSONDecodeError:
                continue

    # Save output
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        for entry in data_buffer:
            f.write(json.dumps(entry) + "\n")

    print(f"Processed {processed_count} conversations.")
    print(f"Skipped {skipped_count} invalid/empty items.")
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare dataset for fine-tuning.")
    parser.add_argument(
        "--input",
        "-i",
        default="data/datasets/raw_chats.jsonl",
        help="Input raw JSONL file",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="data/datasets/finetune_ready.jsonl",
        help="Output training JSONL file",
    )

    args = parser.parse_args()
    prepare_dataset(args.input, args.output)
