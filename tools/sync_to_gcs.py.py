#!/usr/bin/env python3
"""
Sync local 'stormlight_short/' tree to a GCS bucket with identical paths.

- Skips files whose MD5 matches the GCS object's md5_hash (no re-upload).
- Creates missing folders implicitly via object prefixes.
- Optional --delete removes remote objects that no longer exist locally.
- Respects simple exclude globs (e.g., *.tmp, *.DS_Store).
- Writes a sync log you can keep in 00_docs/sync_logs/.

Auth: uses Application Default Credentials (gcloud auth application-default login)
"""

import argparse
import base64
import fnmatch
import hashlib
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterable, List

from google.cloud import storage

DEFAULT_EXCLUDES = ["*.tmp", "*.temp", "*.DS_Store", "Thumbs.db", "*.crdownload"]

def b64_md5(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return base64.b64encode(h.digest()).decode("utf-8")

def iter_files(root: Path, excludes: List[str]) -> Iterable[Path]:
    for p in root.rglob("*"):
        if p.is_file():
            rel = p.relative_to(root).as_posix()
            if any(fnmatch.fnmatch(rel, pat) for pat in excludes):
                continue
            yield p

def should_exclude(rel: str, excludes: List[str]) -> bool:
    return any(fnmatch.fnmatch(rel, pat) for pat in excludes)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--local", required=True, help="Local root (e.g., ~/Google Drive/stormlight_short)")
    ap.add_argument("--bucket", required=True, help="GCS bucket name (e.g., stormlight_short)")
    ap.add_argument("--prefix", default="", help="Optional prefix inside bucket (e.g., 'prod/' or 'dev/').")
    ap.add_argument("--delete", action="store_true", help="Delete remote objects not present locally.")
    ap.add_argument("--dry-run", action="store_true", help="Show actions without uploading/deleting.")
    ap.add_argument("--exclude", action="append", default=[], help="Glob to exclude (repeatable).")
    ap.add_argument("--logdir", default="00_docs/sync_logs", help="Where to write a sync log (relative to local root).")
    args = ap.parse_args()

    local_root = Path(os.path.expanduser(args.local)).resolve()
    if not local_root.exists():
        print(f"Local root not found: {local_root}", file=sys.stderr)
        sys.exit(1)

    excludes = DEFAULT_EXCLUDES + args.exclude

    client = storage.Client()  # ADC
    bucket = client.bucket(args.bucket)

    # Prepare logging
    logdir = (local_root / args.logdir)
    logdir.mkdir(parents=True, exist_ok=True)
    log_path = logdir / f"sync_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.log"
    def log(msg: str):
        print(msg)
        with log_path.open("a", encoding="utf-8") as f:
            f.write(msg + "\n")

    # Upload / update
    uploaded, skipped = 0, 0
    for path in iter_files(local_root, excludes):
        rel = path.relative_to(local_root).as_posix()
        blob_name = f"{args.prefix}{rel}" if args.prefix else rel
        blob = bucket.blob(blob_name)

        local_md5 = b64_md5(path)
        remote_md5 = None
        if blob.exists(client):
            blob.reload()
            remote_md5 = blob.md5_hash

        if remote_md5 == local_md5:
            skipped += 1
            log(f"SKIP  {rel} (unchanged)")
            continue

        action = "UPLOAD" if remote_md5 is None else "UPDATE"
        log(f"{action} {rel}")
        if not args.dry_run:
            blob.upload_from_filename(str(path))
        uploaded += 1

    # Optional delete: remote objects not present locally
    deleted = 0
    if args.delete:
        prefix = args.prefix or ""
        local_set = set(p.relative_to(local_root).as_posix() for p in iter_files(local_root, excludes))
        for blob in client.list_blobs(args.bucket, prefix=prefix):
            rel = blob.name[len(prefix):] if prefix and blob.name.startswith(prefix) else blob.name
            if not rel or rel.endswith("/"):
                continue
            if should_exclude(rel, excludes):
                continue
            if rel not in local_set:
                log(f"DELETE {rel}")
                if not args.dry_run:
                    blob.delete()
                deleted += 1

    log(f"Done. uploaded/updated={uploaded}, skipped={skipped}, deleted={deleted}")
    log(f"Log saved: {log_path}")

if __name__ == "__main__":
    main()