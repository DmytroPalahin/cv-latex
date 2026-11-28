"""Check that the links of the CV PDFs still open.

From the repository root:

    make links
    uv run scripts/check_links.py src/en/cv-dmytro-palahin-en-d.pdf

Every web link of each PDF (listed by Poppler: ``pdfinfo -url``) is requested once, the way
an anonymous visitor opens it. Links to the same site are requested one after the other, so
that the site does not take the check for an attack:

    ok       the page answers
    FAIL     the page does not exist: HTTP 404 or 410, or the host name is unknown
    warning  the link could not be verified: the site refuses automated requests
             (LinkedIn, Udemy...) or has a temporary problem

Exit status: 1 when at least one link fails, 0 otherwise. Warnings never fail the run.
"""

import argparse
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from http import HTTPStatus
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

USER_AGENT = "Mozilla/5.0 (compatible; link-check)"
PDFINFO_COLUMNS = 3  # page, type, URL
GONE: set[int] = {404, 410}  # the page does not exist
REFUSED: set[int] = {
    401,
    403,
    999,
}  # the site refuses automated requests: retrying does not help


@dataclass(frozen=True)
class Result:
    url: str
    status: str  # "ok", "fail" or "warning"
    detail: str


def parse_pdfinfo_urls(output: str) -> list[str]:
    """Links listed by ``pdfinfo -url``: a header row, then one "page type URL" row per link."""
    urls = []
    for line in output.splitlines():
        parts = line.split(None, 2)
        if len(parts) == PDFINFO_COLUMNS and parts[0].isdigit():
            urls.append(parts[2].strip())
    return urls


def links_of(pdf: Path) -> list[str]:
    done = subprocess.run(
        ["pdfinfo", "-url", str(pdf)], capture_output=True, text=True, check=True
    )
    return parse_pdfinfo_urls(done.stdout)


def classify(code: int) -> tuple[str, str]:
    """Status and detail for an HTTP status code."""
    if HTTPStatus.OK <= code < HTTPStatus.MULTIPLE_CHOICES:
        return "ok", str(code)
    if code in GONE:
        return "fail", f"HTTP {code}: the page does not exist"
    return "warning", f"HTTP {code}: not verified"


def check(url: str, timeout: float, retries: int) -> Result:
    """Request ``url`` once; try again only when the problem may be temporary.

    Only http and https links reach this function: see ``main``.
    """
    headers = {"User-Agent": USER_AGENT, "Accept": "*/*"}
    request = urllib.request.Request(url, headers=headers)  # noqa: S310
    detail = "no answer"
    for attempt in range(retries + 1):
        if attempt:
            time.sleep(3 * attempt)
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
                return Result(url, *classify(response.status))
        except urllib.error.HTTPError as error:
            status, detail = classify(error.code)
            if status == "fail" or error.code in REFUSED:
                return Result(url, status, detail)
        except urllib.error.URLError as error:
            if isinstance(error.reason, socket.gaierror):
                return Result(url, "fail", "unknown host name")
            detail = f"no answer ({error.reason})"
        except OSError as error:  # timeout or connection reset while reading the answer
            detail = f"no answer ({error})"
    return Result(url, "warning", detail)


def check_site(urls: list[str], timeout: float, retries: int) -> list[Result]:
    """Check the links of one site, one after the other."""
    results = []
    for index, url in enumerate(urls):
        if index:
            time.sleep(1)
        results.append(check(url, timeout, retries))
    return results


def hint(url: str) -> str:
    if url.startswith("https://github.com/"):
        return "on GitHub, a 404 also means a private or renamed repository"
    return ""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the links of the CV PDFs still open."
    )
    parser.add_argument("pdfs", nargs="+", type=Path, metavar="PDF")
    parser.add_argument(
        "--timeout", type=float, default=20, help="seconds per request (default 20)"
    )
    parser.add_argument(
        "--retries", type=int, default=3, help="extra tries on a temporary problem"
    )
    args = parser.parse_args()

    if shutil.which("pdfinfo") is None:
        print(
            "error: 'pdfinfo' not found: install Poppler (brew install poppler)",
            file=sys.stderr,
        )
        return 2

    where: dict[str, list[str]] = {}  # link -> the PDFs that contain it
    for pdf in args.pdfs:
        if not pdf.is_file():
            print(f"error: {pdf} not found", file=sys.stderr)
            return 2
        for url in links_of(pdf):
            if str(pdf) not in where.setdefault(url, []):
                where[url].append(str(pdf))

    web = sorted(url for url in where if url.startswith(("http://", "https://")))
    other = sorted({url.split(":", 1)[0] + ":" for url in where if url not in web})
    print(f"==> {len(web)} web links in {len(args.pdfs)} PDF(s)")
    if not web:
        return 0

    sites: dict[str, list[str]] = {}
    for url in web:
        sites.setdefault(urllib.parse.urlsplit(url).netloc, []).append(url)
    with ThreadPoolExecutor(max_workers=8) as pool:
        per_site = pool.map(
            lambda urls: check_site(urls, args.timeout, args.retries), sites.values()
        )
        results = [result for site in per_site for result in site]
    results.sort(key=lambda result: result.url)

    if all(
        result.status != "ok" and not result.detail.startswith("HTTP")
        for result in results
    ):
        print("error: no link answered: is the network available?", file=sys.stderr)
        return 2

    annotate = os.environ.get("GITHUB_ACTIONS") == "true"
    for label, status in (("ok", "ok"), ("warning", "warning"), ("FAIL", "fail")):
        for result in results:
            if result.status != status:
                continue
            print(f"    {label}: {result.detail}  {result.url}")
            if status == "fail":
                print(f"          in: {', '.join(where[result.url])}")
                if hint(result.url):
                    print(f"          {hint(result.url)}")
            if annotate and status != "ok":
                command = "error" if status == "fail" else "warning"
                print(
                    f"::{command} title=Link of the CV::{result.url} ({result.detail})"
                )
    if other:
        print(f"    not checked: {', '.join(other)} links")

    statuses = [result.status for result in results]
    fine, unverified, failing = (
        statuses.count(status) for status in ("ok", "warning", "fail")
    )
    print(f"{fine} fine, {unverified} not verified, {failing} failing")
    return 1 if failing else 0


if __name__ == "__main__":
    sys.exit(main())
