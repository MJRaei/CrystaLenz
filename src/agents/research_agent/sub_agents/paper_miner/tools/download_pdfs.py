import pathlib, requests
from typing import List, Dict, Any


def download_pdfs(urls: List[str], output_dir: str = "papers/downloaded_pdfs",
                  timeout_sec: int = 20) -> Dict[str, Any]:
    """
    Download PDF files from a list of URLs into a local folder.

    Args:
        urls: List of HTTP/HTTPS links to check and download if they are PDFs.
        output_dir: Folder to save files into (created if missing).
        timeout_sec: Per-request timeout.

    Returns:
        dict with:
          - status: "ok"
          - saved: list of {"url","path"} for downloaded PDFs
          - skipped: list of {"url","reason"} for non-PDFs or failures
    """
    out = pathlib.Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    saved, skipped = [], []

    for idx, u in enumerate(urls, start=1):
        try:
            # Some servers don't support HEAD reliably; if HEAD fails, fall back to GET
            try:
                head = requests.head(u, allow_redirects=True, timeout=timeout_sec)
                ctype = head.headers.get("Content-Type", "").lower()
                is_pdf = "application/pdf" in ctype
            except Exception:
                is_pdf = False

            # If HEAD was inconclusive, try a small ranged GET and sniff header bytes
            if not is_pdf:
                r0 = requests.get(u, stream=True, timeout=timeout_sec,
                                  headers={"Range": "bytes=0-1023"})
                first_chunk = next(r0.iter_content(chunk_size=1024), b"")
                is_pdf = first_chunk.startswith(b"%PDF-")

            if not is_pdf:
                skipped.append({"url": u, "reason": "not a PDF"})
                continue

            # Download
            resp = requests.get(u, stream=True, timeout=timeout_sec)
            if resp.status_code != 200:
                skipped.append({"url": u, "reason": f"HTTP {resp.status_code}"})
                continue

            # Make a friendly filename
            name = f"paper_{idx}.pdf"
            path = out / name
            with open(path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            saved.append({"url": u, "path": str(path)})

        except Exception as e:
            skipped.append({"url": u, "reason": str(e)})

    return {"status": "ok", "saved": saved, "skipped": skipped}
