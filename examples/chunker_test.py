import os
import sys
import json
import argparse
from typing import List, Dict, Any, Tuple

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.sub_agents.research_agent.tools.create_vector_store import _split_text

CHUNK_SIZE = 4000
CHUNK_OVERLAP = 600


def load_structured_json_files(target_path: str) -> List[Tuple[str, Dict[str, Any]]]:
    """
    Load a single structured JSON file or all JSON files in a directory.
    Returns a list of (path, data) tuples.
    """
    files: List[Tuple[str, Dict[str, Any]]] = []
    if os.path.isdir(target_path):
        for name in sorted(os.listdir(target_path)):
            if name.endswith(".json"):
                p = os.path.join(target_path, name)
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        files.append((p, json.load(f)))
                except Exception as e:
                    print(f"Skipping {p}: {e}")
    else:
        # Treat as a single file
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                files.append((target_path, json.load(f)))
        except Exception as e:
            print(f"Failed to load {target_path}: {e}")
    return files


def iter_chunks_for_file(file_path: str, data: Dict[str, Any]):
    title = (data.get("title") or "").strip()
    doi = (data.get("doi") or "").strip()
    sections = [
        ("abstract", (data.get("abstract") or "").strip()),
        ("introduction", (data.get("introduction") or "").strip()),
        ("experimental", (data.get("experimental") or "").strip()),
        ("results_and_discussion", (data.get("results_and_discussion") or "").strip()),
        ("conclusion", (data.get("conclusion") or "").strip()),
    ]
    for section_name, section_text in sections:
        if not section_text:
            continue
        chunks = _split_text(section_text, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
        for idx, chunk in enumerate(chunks):
            yield {
                "file": os.path.basename(file_path),
                "path": file_path,
                "title": title,
                "doi": doi,
                "section": section_name,
                "index": idx,
                "size": len(chunk),
                "text": chunk,
            }


def main():
    parser = argparse.ArgumentParser(description="Interactive chunk viewer for structured paper JSONs.")
    parser.add_argument(
        "target",
        nargs="?",
        default=os.path.join(PROJECT_ROOT, "papers", "structured_papers"),
        help="Path to a structured JSON file or a directory containing JSON files. Defaults to papers/structured_papers.",
    )
    args = parser.parse_args()

    files = load_structured_json_files(args.target)
    if not files:
        print("No JSON files found to process.")
        return

    total = 0
    for file_path, data in files:
        print(f"\n=== File: {file_path} ===")
        for chunk in iter_chunks_for_file(file_path, data):
            total += 1
            header = (
                f"[Chunk {total}] file={chunk['file']} section={chunk['section']} "
                f"idx={chunk['index']} size={chunk['size']} title={chunk['title']!r} doi={chunk['doi']!r}"
            )
            print("\n" + header)
            print("-" * len(header))
            print(chunk["text"])
            user_in = input("\nPress Enter for next chunk, or 'q' to quit: ").strip().lower()
            if user_in == "q":
                print("Exiting.")
                return

    print(f"\nDone. Displayed {total} chunks.")


if __name__ == "__main__":
    main()


