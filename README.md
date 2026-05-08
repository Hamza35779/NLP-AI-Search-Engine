# NLP Search Engine

A production-grade Natural Language Processing search engine built in pure Python. Features advanced web crawling, intelligent caching, PageRank-like authority scoring, comprehensive logging, and a stunning modern web interface with glassmorphism effects.

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0+-lightgrey?style=flat&logo=flask)

![License](https://img.shields.io/badge/License-MIT-green?style=flat)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success?style=flat)

---

## 🚀 Features

### Core NLP & Search Capabilities
- **Advanced Text Preprocessing**: Tokenization, case folding, stop-word removal, and Porter stemming
- **Inverted Index**: Efficient postings lists with term frequencies and positions
- **Multiple Ranking Models**: 
  - TF-IDF with cosine similarity
  - Okapi BM25 with tunable parameters (k1, b)
  - **Semantic Search** with TF-IDF vector embeddings
- **Smart Query Parsing**: Supports quoted phrases, required/excluded terms, and boolean operators
- **Intelligent Snippets**: Best-window selection with highlighted query terms
- **Spell Checker**: Damerau-Levenshtein edit distance for query suggestions
- **Query Autocomplete**: Real-time search suggestions as you type
- **Related Queries**: Discover related search terms
- **Search Analytics**: Track and analyze search patterns

### 🌐 Web Crawling & Real-World Search
- **Web Crawler**: Breadth-first crawling with domain filtering
- **URL Support**: Full URL tracking with clickable result links
- **Domain Extraction**: Automatic domain parsing from URLs
- **Single Page Loading**: Fetch and index individual web pages
- **Link Authority**: PageRank-like scoring based on inbound links

### ⚡ Performance & Scalability
- **Smart Caching Layer**: LRU cache with disk persistence and TTL support
- **Authority Boosting**: PageRank-like algorithm for result ranking
- **Optimized Index**: Efficient data structures for fast retrieval
- **Performance Logging**: Query timing and system monitoring

### 📊 Monitoring & Reliability
- **Comprehensive Logging**: Console and file-based logging
- **Performance Tracking**: Search time measurement and logging
- **Cache Management API**: Clear cache via API endpoint
- **Health Checks**: `/healthz` endpoint for monitoring
- **Graceful Error Handling**: Robust error recovery throughout

### 🎨 Modern Web Interface
- **Stunning Dark Theme**: Beautiful gradient backgrounds with glassmorphism effects
- **Smooth Animations**: Fade-in, slide-up, pulse, and shimmer effects
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Interactive Components**: Animated cards, glowing buttons, dynamic search form
- **Real-time Stats**: Live index statistics in the header
- **Model Toggle**: Switch between BM25 and TF-IDF ranking instantly
- **Clickable Results**: Direct links to original sources with domain display

---

## 📦 Quick Start

### Prerequisites
- Python 3.11+
- pip (Python package manager)

### Installation

```bash
# Clone the repository
git clone https://github.com/AbdulGhani002/nlp-search-engine.git
cd nlp-search-engine

# Install dependencies (includes Flask, requests, beautifulsoup4)
pip install -r requirements.txt

# Build the search index with sample documents
python scripts/build_index.py
```

### Running the Application

**🌐 Web Interface:**
```bash
python app.py
# Open http://127.0.0.1:5000 in your browser
```

**💻 Command Line Interface:**
```bash
# One-off query
python cli.py "machine learning"

# Use specific model
python cli.py --model tfidf "neural networks"

# Interactive mode
python cli.py
```

**🐳 Using Docker:**
```bash
make docker    # Build Docker image
# Runs with gunicorn on port 5000
```

**🛠️ Using Make:**
```bash
make install    # Install dependencies
make run        # Start Flask app (debug mode)
make repl       # CLI interactive mode
make index      # Rebuild index
make test       # Run tests
```

---

## 🔍 Usage

### Web Search Syntax

The search engine supports powerful query syntax:

| Syntax | Description | Example |
|---------|-------------|---------|
| `"phrase"` | Exact phrase search | `"natural language"` |
| `+term` | Required term | `+bm25` |
| `-term` | Excluded term | `-neural` |
| `AND` | All terms required | `search AND retrieval` |
| `OR` | Any term matches | `bm25 OR tfidf` |

**Example Queries:**
```bash
information retrieval
"natural language" +processing -neural
ranking +bm25 OR +tfidf
```

### Web Crawling

```python
from src.document_loader import crawl_web, load_web_page

# Crawl a website (respects robots.txt in production)
docs = crawl_web(["https://example.com"], max_pages=50)

# Load a single page
doc = load_web_page("https://example.com/page")
```

### JSON API

**Search Endpoint:**
```bash
curl "http://127.0.0.1:5000/api/search?q=machine+learning&model=bm25&k=5"
```

**Semantic Search Endpoint:**
```bash
curl "http://127.0.0.1:5000/api/semantic-search?q=machine+learning&k=5"
```

**Autocomplete Endpoint:**
```bash
curl "http://127.0.0.1:5000/api/autocomplete?prefix=ma"
```

**Analytics Endpoints:**
```bash
# Get analytics stats
curl "http://127.0.0.1:5000/api/analytics"

# Get top queries
curl "http://127.0.0.1:5000/api/top-queries"

# Get related queries
curl "http://127.0.0.1:5000/api/related-queries?q=machine+learning"
```

**Document Management:**
```bash
# Add a document (POST)
curl -X POST "http://127.0.0.1:5000/api/documents" \
  -H "Content-Type: application/json" \
  -d '{"title": "New Doc", "text": "Document content here"}'

# Remove a document (DELETE)
curl -X DELETE "http://127.0.0.1:5000/api/documents/1"
```

**Other Endpoints:**
```bash
# Index statistics
curl "http://127.0.0.1:5000/api/stats"

# Health check
curl "http://127.0.0.1:5000/healthz"

# Clear search cache (POST)
curl -X POST "http://127.0.0.1:5000/api/cache/clear"
```

---

## 📁 Project Structure

```
nlp-search-engine/
├── app.py                      # Flask web application (with logging)
├── cli.py                      # Command-line interface
├── requirements.txt            # Python dependencies (Flask, requests, bs4)
├── pyproject.toml             # Project configuration
├── Dockerfile                  # Container definition
├── Makefile                   # Build automation
├── README.md                  # This file
├── LICENSE                    # MIT License
│
├── src/                       # Core source code
│   ├── search_engine.py       # Main facade (with caching & PageRank)
│   ├── document.py           # Document class (with URL/domain support)
│   ├── document_loader.py     # Corpus loading + web crawling
│   ├── indexer.py            # Inverted index
│   ├── ranker.py             # Ranking model wrapper
│   ├── bm25.py               # BM25 implementation
│   ├── tfidf.py              # TF-IDF implementation
│   ├── preprocessing.py      # Tokenization, stemming, stopwords
│   ├── query_processor.py   # Query parsing
│   ├── snippet.py            # Snippet generation
│   ├── spell_check.py        # Spell checker
│   ├── cache.py              # Search result caching layer
│   ├── logger.py             # Logging configuration
│   ├── metrics.py            # IR evaluation metrics
│   ├── config.py             # Configuration
│   └── utils.py              # Helper functions
│
├── templates/                 # Jinja2 HTML templates
│   ├── base.html             # Base layout with modern UI
│   ├── index.html            # Home page with hero section
│   ├── results.html          # Search results (with URLs)
│   ├── about.html            # Project information
│   └── _partials/           # Reusable components
│
├── static/                    # CSS and images
│   ├── css/
│   │   ├── base.css          # Design tokens, typography, layout
│   │   ├── components.css    # Search form, cards, badges
│   │   ├── home.css          # Hero, features, steps
│   │   └── results.css      # Results page layout
│   └── img/                 # Logos and favicons
│
├── tests/                     # pytest test suite (25 tests)
├── scripts/                   # Build/indexing scripts
├── examples/                  # Usage examples
└── data/                      # Sample corpus
    └── sample_docs/           # 7 NLP/IR documents
```

---

## ⚙️ Configuration

Edit `src/config.py` to customize the search engine:

```python
@dataclass
class EngineConfig:
    # Preprocessing
    use_stemming: bool = True
    remove_stopwords: bool = True
    min_token_length: int = 2
    
    # BM25 Parameters
    bm25_k1: float = 1.5        # Saturation parameter
    bm25_b: float = 0.75        # Length normalization
    
    # Snippets
    snippet_window: int = 12     # Words in snippet
    max_snippets: int = 1
    
    # Spell Checker
    spell_max_distance: int = 2  # Edit distance
    spell_top_k: int = 3
    
    # Persistence
    index_path: str = "index_data/engine.pkl"
```

---

## 🛠️ Technologies Used

### Backend
- **Python 3.11+**: Core language
- **Flask 3.0+**: Web framework
- **Requests**: HTTP library for web crawling
- **BeautifulSoup4**: HTML parsing for web crawling

### NLP & Search
- **NLTK**: Optional extended stopwords
- **Custom Porter Stemmer**: Lightweight stemming algorithm
- **NumPy**: Numerical computations

### Frontend
- **HTML5**: Modern semantic markup
- **CSS3**: Custom properties, Grid, Flexbox, animations
- **Inter Font**: Google Fonts for typography
- **Jinja2**: Template engine

### DevOps & Quality
- **pytest**: Testing framework (25 tests)
- **ruff**: Fast Python linter
- **black**: Code formatter
- **pre-commit**: Git hooks
- **GitHub Actions**: CI/CD pipeline
- **Docker**: Containerization

---

## 📊 Performance Features

### Caching Layer (`src/cache.py`)
- LRU-like cache with configurable size
- Disk persistence for cache durability
- TTL (Time To Live) support
- Automatic cache invalidation

### PageRank-like Scoring
- Authority boosting based on inbound links
- Configurable damping factor
- Iterative convergence algorithm
- Integrated with BM25/TF-IDF scores

### Logging (`src/logger.py`)
- Dual output (console + file)
- Configurable log levels
- Performance metrics tracking
- Search query logging with timing

---

## 👥 Team Members

1. **Hamza Abdul Karim** - F23607046
2. **M. Ahad Imran** - F23607034
3. **Syed Zain-ul-Abidin** - F23607031
4. **M. Usman Nasir** - F23607004

---

## 🧪 Development

```bash
# Install development dependencies
make dev

# Run tests (25 tests)
make test

# Lint code
make lint

# Format code
make format

# Run with coverage
pytest --cov=src tests/
```

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Coursework project for NLP/Information Retrieval
- Inspired by classical IR techniques and modern web design principles
- Built with pure Python - no external search libraries used
- Web crawling respects standard practices (implement robots.txt checking in production)

---

## 🔗 Links

- **Live Demo**: [http://127.0.0.1:5000](http://127.0.0.1:5000)
- **Source Code**: [GitHub Repository](https://github.com/AbdulGhani002/nlp-search-engine)
- **Issue Tracker**: [GitHub Issues](https://github.com/AbdulGhani002/nlp-search-engine/issues)

---

**⚠️ Disclaimer**: The web crawling feature is for educational purposes. Always respect website terms of service, robots.txt, and rate limits when crawling. Use responsibly.
