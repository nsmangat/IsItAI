"""
Image upload pipeline

Pushes already-fetched images to Supabase: file bytes go to bucket Storage, metadata
to the 'images' table, and Gemini analysis results (if present) to 'analyses'.
Requires each image to have a '.meta.json' file from fetch_images.py which should
be populated on image retrieval.
Once uploaded, this script adds 'image_id' and 'analysis_uploaded' fields to that same
file to track which files have been uploaded to Storage.

Test commands:

    python upload_images.py                # upload anything not yet uploaded
    python upload_images.py --limit 2       # upload at most 2 new images
"""

import argparse
import json
from pathlib import Path

import config
from supabase_client import get_client

# Getting file paths for images, their metadata JSON files, and analysis JSON files for AI images
def _get_image_paths() -> list[Path]:
    return sorted(config.AI_POLLINATIONS_DIR.glob("*.jpg")) + sorted(config.REAL_UNSPLASH_DIR.glob("*.jpg"))


def _meta_path(filepath: Path) -> Path:
    return filepath.with_suffix(".meta.json")


def _analysis_path(filepath: Path) -> Path:
    return filepath.with_suffix(".json")


def _load_json(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def _save_json(path: Path, data: dict) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


# Uploads image bytes to Supabase buckets and inserts the images row
# Returns the new row's id to then add to the meta data, which is a flag to let us know it's been uploaded
def _upload_image(client, filepath: Path, meta: dict) -> str:

    # Mimicing local path to bucket path i.e. ai/pollinations/ai_image_abc.jpg
    # Windows uses \\, object storage uses / so need to replace
    storage_path = str(filepath.relative_to(config.IMAGE_DIR)).replace("\\", "/")
    image_bytes = filepath.read_bytes()

    client.storage.from_(config.SUPABASE_IMAGES_BUCKET).upload(
        storage_path,
        image_bytes,
        file_options={"content-type": "image/jpeg", "upsert": "true"},
    )

    # Bucket is public, so once uploaded, can get its public url which can be referenced whenever
    public_url = client.storage.from_(config.SUPABASE_IMAGES_BUCKET).get_public_url(storage_path)

    # Result is response object from Postgres, data is the rows that were inserted as a list of dicts
    result = client.table("images").insert({
        "source": meta["source"],
        "is_ai": meta["is_ai"],
        "attribution": meta["attribution"],
        "public_url": public_url,
    }).execute()

    return result.data[0]["id"]


def _upload_analysis(client, image_id: str, analysis: dict) -> None:

    client.table("analyses").insert({
        "image_id": image_id,
        "confidence": analysis["confidence"],
        "signals": analysis["signals"],
    }).execute()


def upload_images(limit: int | None = None) -> int:

    client = get_client()
    image_paths = _get_image_paths()

    uploaded_count = 0
    analyses_uploaded_count = 0

    for filepath in image_paths:

        if limit is not None and uploaded_count >= limit:
            break

        meta_path = _meta_path(filepath)
        if not meta_path.exists():
            print(f"Skipping {filepath.name} - no .meta.json found (fetch again to generate one)")
            continue

        meta = _load_json(meta_path)

        # If image_id isn't in the metadata, then it hasn't been uploaded yet
        if "image_id" not in meta:
            print(f"Uploading {filepath.name}...")
            try:
                meta["image_id"] = _upload_image(client, filepath, meta)
            except Exception as e:
                print(f"Failed to upload {filepath.name}: {e}")
                continue

            meta["analysis_uploaded"] = False
            # Re-write the meta data file to add the image_id and analysis_uploaded fields
            _save_json(meta_path, meta)
            uploaded_count += 1

        # Uploading analysis if there is one for the an AI image
        analysis_path = _analysis_path(filepath)

        if analysis_path.exists() and not meta.get("analysis_uploaded", False):
            print(f"Uploading analysis for AI image - {filepath.name}...")
            try:
                analysis = _load_json(analysis_path)
                _upload_analysis(client, meta["image_id"], analysis)
            except Exception as e:
                print(f"Failed to upload analysis for {filepath.name}: {e}")
                continue

            meta["analysis_uploaded"] = True
            _save_json(meta_path, meta)
            analyses_uploaded_count += 1

    print("-" * 50)
    print(f"Finished. Uploaded {uploaded_count} new image(s), {analyses_uploaded_count} new analysis result(s).")

    return uploaded_count


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Upload fetched images and analysis results to Supabase")
    parser.add_argument("--limit", type=int, default=None, help="Upload at most this many new images")
    args = parser.parse_args()

    upload_images(limit=args.limit)
