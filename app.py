"""Flask web UI for the NLP search engine.

Loads (or builds) an index at process start and serves a search form at
``/``, a results page at ``/search``, an about page at ``/about``, plus
JSON endpoints under ``/api``.
"""

from __future__ import annotations

import json
import os
import time
from typing import Optional

from flask import Flask, jsonify, render_template, request

from src.cache import search_cache
from src.config import EngineConfig
from src.logger import logger
from src.search_engine import SearchEngine


AVAILABLE_MODELS = ("bm25", "tfidf")


def _build_engine(corpus_dir: str, model: str) -> SearchEngine:
    cfg = EngineConfig()
    engine = SearchEngine(cfg, model=model)
    engine.index_corpus(corpus_dir)
    return engine


def _select_model(engine: SearchEngine, requested: Optional[str]) -> str:
    """Switch the engine to `requested` if valid; return the active model."""
    if requested:
        try:
            engine.ranker.use_model(requested)
        except ValueError:
            pass
    return engine.ranker.model_name


def create_app(corpus: Optional[str] = None, model: str = "bm25") -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")
    corpus_dir = (
        corpus
        or os.environ.get("CORPUS_DIR")
        or os.path.join("data", "sample_docs")
    )
    engine = _build_engine(corpus_dir, model)

    # Initialize metrics
    metrics = engine._metrics

    # ------------------------------------------------------------------ HTML
    @app.route("/")
    def index():
        logger.info("Serving index page")
        return render_template(
            "index.html",
            active="home",
            stats=engine.stats(),
            available_models=AVAILABLE_MODELS,
            current_model=engine.ranker.model_name,
        )

    @app.route("/about")
    def about():
        logger.info("Serving about page")
        return render_template(
            "about.html",
            active="about",
            stats=engine.stats(),
        )

    @app.route("/search")
    def search():
        q = (request.args.get("q") or "").strip()
        model_name = _select_model(engine, request.args.get("model"))
        top_k = max(1, min(int(request.args.get("k", 10) or 10), 50))

        start_time = time.time()
        parsed = engine.parse(q) if q else None
        results = engine.search(q, top_k=top_k) if q else []
        suggestion = engine.suggest_query(q) if q and not results else None
        max_score = max((r.score for r in results), default=1.0) or 1.0
        elapsed = time.time() - start_time

        logger.info(f"Search query: '{q}' | Model: {model_name} | Results: {len(results)} | Time: {elapsed:.3f}s")

        return render_template(
            "results.html",
            active=None,
            query=q,
            model=model_name,
            parsed=parsed,
            results=results,
            max_score=max_score,
            suggestion=suggestion,
            available_models=AVAILABLE_MODELS,
            stats=engine.stats(),
        )

    # ------------------------------------------------------------------ JSON
    @app.route("/api/search")
    def api_search():
        q = (request.args.get("q") or "").strip()
        model_requested = request.args.get("model")
        if model_requested and model_requested not in AVAILABLE_MODELS:
            logger.warning(f"Unknown model requested: {model_requested}")
            return jsonify({"error": f"unknown model {model_requested!r}"}), 400
        model_name = _select_model(engine, model_requested)
        top_k = max(1, min(int(request.args.get("k", 10) or 10), 50))

        start_time = time.time()
        cache_hit = q and search_cache.get(q, model_name, top_k) is not None
        results = engine.search(q, top_k=top_k) if q else []
        elapsed = time.time() - start_time

        # Record metrics
        metrics.record_search(elapsed, cache_hit)
        
        logger.info(f"API search: '{q}' | Model: {model_name} | Results: {len(results)} | Time: {elapsed:.3f}s")

        return jsonify(
            {
                "query": q,
                "model": model_name,
                "top_k": top_k,
                "results": [r.to_dict() for r in results],
                "suggestion": engine.suggest_query(q) if q else None,
                "time_taken": round(elapsed, 3),
            }
        )

    @app.route("/api/stats")
    def api_stats():
        return jsonify(engine.stats())

    @app.route("/api/cache/clear", methods=["POST"])
    def api_clear_cache():
        """Clear the search cache."""
        search_cache.clear()
        logger.info("Search cache cleared")
        return jsonify({"status": "cache cleared"})

    @app.route("/healthz")
    def healthz():
        index_healthy = engine.index is not None and engine.index.num_documents > 0
        return jsonify({
            "status": "ok" if index_healthy else "degraded",
            "documents": engine.index.num_documents if engine.index else 0,
            "model": engine.ranker.model_name,
            "uptime_seconds": round(time.time() - engine._metrics._start_time),
            "index_healthy": index_healthy,
        }), 200 if index_healthy else 503

    @app.route("/readyz")
    def readyz():
        if engine.index and engine.index.num_documents > 0:
            return jsonify({"status": "ready"}), 200
        return jsonify({"status": "not ready"}), 503

    @app.route("/metrics")
    def prometheus_metrics():
        """Prometheus-compatible metrics endpoint."""
        return engine._metrics.get_prometheus_metrics(), 200, {"Content-Type": "text/plain"}

    @app.route("/api/metrics")
    def api_metrics():
        """JSON metrics for custom dashboards."""
        return jsonify(engine._metrics.get_json_metrics())

    # ------------------------------------------------------------------ New API endpoints

    @app.route("/api/search")
    def api_search():
        q = (request.args.get("q") or "").strip()
        model_requested = request.args.get("model")
        if model_requested and model_requested not in AVAILABLE_MODELS:
            logger.warning(f"Unknown model requested: {model_requested}")
            return jsonify({"error": f"unknown model {model_requested!r}"}), 400
        model_name = _select_model(engine, model_requested)
        top_k = max(1, min(int(request.args.get("k", 10) or 10), 50)

        # Filters
        filters = {}
        if request.args.get("domain"):
            filters["domain"] = request.args.get("domain")
        if request.args.get("source"):
            filters["source"] = request.args.get("source")
        if request.args.get("min_score"):
            filters["min_score"] = float(request.args.get("min_score"))

        # Sorting
        sort_by = request.args.get("sort", "relevance")

        start_time = time.time()
        cache_hit = q and search_cache.get(q, model_name, top_k) is not None
        results = engine.search_with_filters(
            q, top_k=top_k, filters=filters, sort_by=sort_by
        ) if q else []
        elapsed = time.time() - start_time

        # Record metrics
        metrics.record_search(elapsed, cache_hit)

        facets = engine.get_facets(results) if filters or sort_by != "relevance" else None

        logger.info(f"API search: '{q}' | Model: {model_name} | Results: {len(results)} | Time: {elapsed:.3f}s")

        return jsonify(
            {
                "query": q,
                "model": model_name,
                "top_k": top_k,
                "results": [r.to_dict() for r in results],
                "suggestion": engine.suggest_query(q) if q else None,
                "time_taken": round(elapsed, 3),
                "facets": facets,
            }
        )

    @app.route("/api/semantic-search")
    def api_semantic_search():
        """Semantic search using TF-IDF vectors."""
        q = (request.args.get("q") or "").strip()
        if not q:
            return jsonify({"error": "Query parameter 'q' is required"}), 400

        top_k = max(1, min(int(request.args.get("k", 10) or 10), 50))

        start_time = time.time()
        results = engine.semantic_search(q, top_k=top_k)
        elapsed = time.time() - start_time

        logger.info(f"Semantic search: '{q}' | Results: {len(results)} | Time: {elapsed:.3f}s")

        return jsonify({
            "query": q,
            "model": "semantic",
            "top_k": top_k,
            "results": [r.to_dict() for r in results],
            "time_taken": round(elapsed, 3),
        })

    @app.route("/api/autocomplete")
    def api_autocomplete():
        """Get autocomplete suggestions."""
        prefix = (request.args.get("prefix") or "").strip()
        limit = int(request.args.get("limit", 5) or 5)

        suggestions = engine.get_autocomplete_suggestions(prefix, limit=limit)

        return jsonify({
            "prefix": prefix,
            "suggestions": suggestions,
        })

    @app.route("/api/analytics")
    def api_analytics():
        """Get search analytics."""
        return jsonify(engine.get_analytics())

    @app.route("/api/top-queries")
    def api_top_queries():
        """Get top queries."""
        limit = int(request.args.get("limit", 10) or 10)
        return jsonify({
            "top_queries": engine.get_top_queries(limit=limit),
        })

    @app.route("/api/related-queries")
    def api_related_queries():
        """Get related queries."""
        q = (request.args.get("q") or "").strip()
        if not q:
            return jsonify({"error": "Query parameter 'q' is required"}), 400

        limit = int(request.args.get("limit", 5) or 5)
        related = engine.get_related_queries(q, limit=limit)

        return jsonify({
            "query": q,
            "related_queries": related,
        })

    @app.route("/api/documents", methods=["POST"])
    def api_add_document():
        """Add a new document to the index."""
        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON body required"}), 400

        required_fields = ["title", "text"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Generate a new doc_id
        doc_id = max(engine.index._documents.keys()) + 1 if engine.index._documents else 1

        from src.document import Document
        doc = Document(
            doc_id=doc_id,
            title=data["title"],
            text=data["text"],
            source=data.get("source", "API"),
            url=data.get("url"),
            metadata=data.get("metadata", {}),
        )

        try:
            engine.add_document(doc)
            logger.info(f"Added document: {doc_id} - {doc.title}")
            return jsonify({
                "status": "success",
                "doc_id": doc_id,
                "message": "Document added successfully",
            })
        except Exception as e:
            logger.error(f"Failed to add document: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/batch-search", methods=["POST"])
    def api_batch_search():
        """Search multiple queries at once."""
        data = request.get_json()
        if not data or "queries" not in data:
            return jsonify({"error": "JSON body with 'queries' array required"}), 400

        queries = data["queries"]
        if not isinstance(queries, list) or len(queries) > 20:
            return jsonify({"error": "Maximum 20 queries per batch"}), 400

        top_k = int(data.get("top_k", 10))
        model = data.get("model", "bm25")

        results = {}
        for q in queries:
            q = q.strip()
            if q:
                results[q] = [r.to_dict() for r in engine.search(q, top_k=top_k)]

        return jsonify({
            "results": results,
            "query_count": len(results),
        })

    @app.route("/api/export")
    def api_export():
        """Export search results in various formats."""
        q = (request.args.get("q") or "").strip()
        if not q:
            return jsonify({"error": "Query parameter 'q' is required"}), 400

        format = request.args.get("format", "json")
        top_k = int(request.args.get("k", 100))

        results = engine.search(q, top_k=top_k)

        if format == "csv":
            import csv
            from io import StringIO
            output = StringIO()
            writer = csv.DictWriter(output, fieldnames=["doc_id", "title", "score", "source", "url"])
            writer.writeheader()
            for r in results:
                writer.writerow(r.to_dict())
            response = app.response_class(
                response=output.getvalue(),
                status=200,
                mimetype='text/csv'
            )
            response.headers['Content-Disposition'] = f'attachment; filename=search_results_{q}.csv'
            return response

        return jsonify({
            "query": q,
            "results": [r.to_dict() for r in results],
            "exported_at": time.time(),
        })

    @app.route("/api/documents/<int:doc_id>", methods=["DELETE"])
    def api_remove_document(doc_id):
        """Remove a document from the index."""
        if engine.remove_document(doc_id):
            logger.info(f"Removed document: {doc_id}")
            return jsonify({
                "status": "success",
                "message": f"Document {doc_id} removed successfully",
            })
        return jsonify({"error": f"Document {doc_id} not found"}), 404

    return app


app = create_app()


if __name__ == "__main__":  # pragma: no cover
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="127.0.0.1", port=port, debug=debug)
