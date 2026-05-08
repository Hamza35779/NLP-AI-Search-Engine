"""Load corpora from disk or the web into `Document` objects.

Supports:
* Directory of plain-text files
* JSON files with document objects
* Web crawling (optional, requires requests/beautifulsoup4)
"""

from __future__ import annotations

import json
import os
import re
from typing import Iterable, Iterator, List, Optional
from urllib.parse import urljoin, urlparse

from .document import Document


def _read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def load_directory(root: str, extensions: Iterable[str] = (".txt",)) -> List[Document]:
    """Load every file under `root` whose suffix is in `extensions`."""
    if not os.path.isdir(root):
        raise FileNotFoundError(f"Corpus directory not found: {root}")
    exts = tuple(e.lower() for e in extensions)
    docs: List[Document] = []
    next_id = 0
    for dirpath, _dirs, files in os.walk(root):
        for name in sorted(files):
            if not name.lower().endswith(exts):
                continue
            full = os.path.join(dirpath, name)
            text = _read_text(full)
            title = os.path.splitext(name)[0].replace("_", " ").replace("-", " ")
            docs.append(
                Document(
                    doc_id=next_id,
                    title=title.strip() or name,
                    text=text,
                    source=os.path.relpath(full, root),
                )
            )
            next_id += 1
    return docs


def load_json(path: str) -> List[Document]:
    """Load a JSON file shaped like ``[{"title": "...", "text": "..."}, ...]``."""
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise ValueError("JSON corpus must be a list of objects")
    docs: List[Document] = []
    for i, raw in enumerate(data):
        if not isinstance(raw, dict):
            raise ValueError(f"Entry {i} is not a JSON object")
        text = raw.get("text") or raw.get("body") or raw.get("content") or ""
        docs.append(
            Document(
                doc_id=i,
                title=str(raw.get("title", f"Document {i}")),
                text=str(text),
                source=raw.get("source") or path,
                url=raw.get("url"),
                metadata={k: v for k, v in raw.items() if k not in {"title", "text", "body", "content", "source", "url"}},
            )
        )
    return docs


def load_web_page(url: str, max_chars: int = 50000) -> Optional[Document]:
    """Fetch a single web page and extract title/text.
    
    Requires: requests, beautifulsoup4
    """
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        raise ImportError("Web crawling requires: pip install requests beautifulsoup4")
    
    try:
        resp = requests.get(url, timeout=10, headers={"User-Agent": "NLP-Search-Engine/1.0"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "html.parser")
        
        # Remove script/style
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        
        title = soup.title.string if soup.title else urlparse(url).path.strip("/") or "Home"
        text = soup.get_text(separator=" ", strip=True)[:max_chars]
        
        return Document(
            doc_id=0,
            title=title.strip(),
            text=text,
            source=url,
            url=url,
            metadata={"domain": urlparse(url).netloc},
        )
    except Exception as e:
        print(f"Error loading {url}: {e}")
        return None


def crawl_web(start_urls: List[str], max_pages: int = 50) -> List[Document]:
    """Simple breadth-first web crawler.
    
    Warning: Use responsibly and respect robots.txt
    """
    docs: List[Document] = []
    visited = set()
    queue = list(start_urls)
    next_id = 0
    
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        raise ImportError("Web crawling requires: pip install requests beautifulsoup4")
    
    while queue and len(docs) < max_pages:
        url = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)
        
        doc = load_web_page(url)
        if doc:
            doc.doc_id = next_id
            docs.append(doc)
            next_id += 1
            
            # Extract links for further crawling
            try:
                resp = requests.get(url, timeout=5)
                soup = BeautifulSoup(resp.content, "html.parser")
                base = urlparse(url)
                for link in soup.find_all("a", href=True):
                    full = urljoin(url, link["href"])
                    parsed = urlparse(full)
                    if parsed.scheme in ("http", "https") and parsed.netloc == base.netloc:
                        clean = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                        if clean not in visited:
                            queue.append(clean)
            except Exception:
                pass
    
    return docs


def iter_documents(path: str) -> Iterator[Document]:
    """Convenience: dispatch on whether `path` is a dir, JSON file, or URL."""
    if path.startswith(("http://", "https://")):
        doc = load_web_page(path)
        if doc:
            yield doc
    elif os.path.isdir(path):
        yield from load_directory(path)
    elif path.lower().endswith(".json"):
        yield from load_json(path)
    else:
        raise ValueError(f"Unsupported corpus path: {path}")
