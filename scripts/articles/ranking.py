"""Content for `docs/ranking-models.pdf` — TF-IDF and BM25 in detail."""

from __future__ import annotations

from .._pdf_blocks import (  # type: ignore[import-not-found]
    abstract, body, body_tight, bullet_list,
    equation_block, section, small_gap, styled_table,
    subsection, title_block,
)


def build(styles) -> list:
    flow: list = []

    flow += title_block(
        styles,
        title="Sparse Ranking Models for the NLP Search Engine",
        subtitle="A formal treatment of TF&minus;IDF and Okapi BM25",
        author="Hamza Abdul Karim &middot; F23607046",
        date="May 2026",
    )
    flow += abstract(
        styles,
        "We document the two interchangeable ranking functions implemented "
        "in the engine. Both are unsupervised, depend only on corpus "
        "statistics, and produce strong baselines without any training "
        "data. We give the formal definitions used by the implementation, "
        "discuss the role of each parameter, and offer guidance on when "
        "to prefer one model over the other. Each formula is reproduced "
        "below as it is computed by the code.",
    )

    # 1. Notation
    flow.append(section(styles, "1", "Notation"))
    flow.append(body(
        styles,
        "Throughout this document we use the following symbols. Let "
        "<i>D</i> denote the indexed corpus and <i>N</i>=|<i>D</i>| its size. "
        "For a term <i>t</i> and a document <i>d</i>, "
        "<i>tf</i>(<i>t</i>,<i>d</i>) is the number of occurrences of "
        "<i>t</i> in <i>d</i>; <i>df</i>(<i>t</i>) is the number of "
        "documents containing <i>t</i>; |<i>d</i>| is the document length "
        "in tokens after preprocessing; and <i>avgdl</i> is the average "
        "document length over the corpus.",
    ))

    # 2. TF-IDF
    flow.append(section(styles, "2", "TF&minus;IDF and Cosine Similarity"))
    flow.append(body(
        styles,
        "Each document is represented as a sparse vector indexed by "
        "terms. The weight of term <i>t</i> in document <i>d</i> uses "
        "logarithmic term&#8209;frequency weighting:",
    ))
    flow.append(equation_block(
        styles,
        r"\mathrm{tf\_weight}(t, d) \,=\, 1 + \log(\mathrm{tf}(t, d)) "
        r"\quad \mathrm{if} \;\; \mathrm{tf}(t, d) > 0",
        label="(2.1)",
    ))
    flow.append(body_tight(
        styles,
        "and a smoothed inverse document frequency:",
    ))
    flow.append(equation_block(
        styles,
        r"\mathrm{idf}(t) \,=\, \log\left(\frac{N + 1}{\mathrm{df}(t) + 1}\right) + 1",
        label="(2.2)",
    ))
    flow.append(body(
        styles,
        "The composite weight is the product of the two:",
    ))
    flow.append(equation_block(
        styles,
        r"w(t, d) \,=\, \mathrm{tf\_weight}(t, d) \cdot \mathrm{idf}(t)",
        label="(2.3)",
    ))
    flow.append(body(
        styles,
        "A query <i>q</i> is mapped into the same vector space using "
        "Eq.&nbsp;(2.3). Documents are ranked by cosine similarity:",
    ))
    flow.append(equation_block(
        styles,
        r"\cos(q, d) \,=\, \frac{\sum_{t} q[t]\, d[t]}{\sqrt{\sum_{t} q[t]^{2}} \cdot \sqrt{\sum_{t} d[t]^{2}}}",
        label="(2.4)",
    ))
    flow.append(body(
        styles,
        "Cosine values lie in [0,&nbsp;1] and are insensitive to "
        "absolute term counts, which makes TF&minus;IDF a predictable "
        "baseline that is easy to debug. The implementation in "
        "<font face='Courier'>src/tfidf.py</font> caches every "
        "document vector at construction time so each query only "
        "recomputes the query vector and a sparse dot product.",
    ))

    # 3. BM25
    flow.append(section(styles, "3", "Okapi BM25"))
    flow.append(body(
        styles,
        "BM25 fixes two empirical weaknesses of plain TF&minus;IDF: "
        "it saturates the contribution of repeated terms, and it "
        "normalizes for document length. The score for a "
        "query&ndash;document pair is",
    ))
    flow.append(equation_block(
        styles,
        r"\mathrm{BM25}(q, d) \,=\, \sum_{t \in q} \mathrm{IDF}(t) \cdot "
        r"\frac{\mathrm{tf}(t, d) \, (k_{1} + 1)}{\mathrm{tf}(t, d) + k_{1} "
        r"\left(1 - b + b \, \frac{|d|}{\mathrm{avgdl}}\right)}",
        label="(3.1)",
    ))
    flow.append(body_tight(styles,
        "with the Robertson&ndash;Sp&auml;rck Jones smoothed IDF",
    ))
    flow.append(equation_block(
        styles,
        r"\mathrm{IDF}(t) \,=\, \log\left(\frac{N - \mathrm{df}(t) + 0.5}{\mathrm{df}(t) + 0.5} + 1\right)",
        label="(3.2)",
    ))

    flow.append(subsection(styles, "3.1", "Parameters"))
    flow.append(small_gap(0.1))
    flow.append(styled_table(
        styles,
        header=("Parameter", "Default", "Effect"),
        rows=[
            ("k1", "1.5",
             "Term-frequency saturation. Smaller values saturate faster."),
            ("b", "0.75",
             "Length normalization. b=0 ignores |d|; b=1 fully penalizes long docs."),
        ],
        col_widths=[2.4 * 28.35, 2.0 * 28.35, 11.6 * 28.35],
    ))

    # 4. Spell correction
    flow.append(section(styles, "4", "Damerau&ndash;Levenshtein Suggestions"))
    flow.append(body(
        styles,
        "When a query term is not present in the index vocabulary, the "
        "engine suggests near&#8209;matches using Damerau&ndash;Levenshtein "
        "distance &mdash; the minimum number of insertions, deletions, "
        "substitutions, and transpositions to transform one string into "
        "another. The standard recurrence used by "
        "<font face='Courier'>src/spell_check.py</font> is",
    ))
    flow.append(equation_block(
        styles,
        r"d_{i,j} \,=\, \min \{\, d_{i-1,j} + 1, \; d_{i,j-1} + 1, \; "
        r"d_{i-1,j-1} + \mathbf{1}_{a_i \neq b_j}, \; d_{i-2,j-2} + 1 \,\}",
        label="(4.1)",
    ))
    flow.append(body(
        styles,
        "The transposition term (the last alternative inside the brackets) "
        "applies only when the last two characters of the prefixes are "
        "swapped, i.e. <i>a</i><sub>i</sub>=<i>b</i><sub>j-1</sub> and "
        "<i>a</i><sub>i-1</sub>=<i>b</i><sub>j</sub>.",
    ))

    # 5. Evaluation metrics
    flow.append(section(styles, "5", "Evaluation Metrics"))
    flow.append(body(
        styles,
        "The engine ships with the standard ranked&#8209;retrieval "
        "metrics in <font face='Courier'>src/metrics.py</font>. Let "
        "<i>R</i><sub>q</sub> be the set of documents relevant to a "
        "query <i>q</i>, let <i>L</i><sub>q</sub>(k) be the top&#8209;k "
        "ranked documents returned for <i>q</i>, and let "
        "<i>r</i><sub>i</sub>=1 if the document at rank <i>i</i> is "
        "relevant and 0 otherwise. We define",
    ))
    flow.append(equation_block(
        styles,
        r"P@k \,=\, \frac{|L_{q}(k) \cap R_{q}|}{k}, \qquad "
        r"R@k \,=\, \frac{|L_{q}(k) \cap R_{q}|}{|R_{q}|}",
        label="(5.1)",
    ))
    flow.append(body_tight(styles, "and the average precision over a single query"))
    flow.append(equation_block(
        styles,
        r"\mathrm{AP}(q) \,=\, \frac{1}{|R_{q}|} \sum_{i=1}^{|L_{q}|} r_{i} \, P@i",
        label="(5.2)",
    ))
    flow.append(body(
        styles,
        "The mean average precision (MAP) is the arithmetic mean of "
        "AP over a query set. The mean reciprocal rank uses only the "
        "rank of the first relevant document:",
    ))
    flow.append(equation_block(
        styles,
        r"\mathrm{MRR} \,=\, \frac{1}{|Q|} \sum_{q \in Q} \frac{1}{\mathrm{rank}_{q}}",
        label="(5.3)",
    ))
    flow.append(body_tight(
        styles,
        "Finally, normalized discounted cumulative gain uses graded "
        "relevance scores <i>rel</i><sub>i</sub>:",
    ))
    flow.append(equation_block(
        styles,
        r"\mathrm{nDCG}@k \,=\, \frac{\sum_{i=1}^{k} (2^{rel_{i}} - 1) "
        r"/ \log_{2}(i + 1)}{\sum_{i=1}^{k} (2^{rel_{i}^{*}} - 1) "
        r"/ \log_{2}(i + 1)}",
        label="(5.4)",
    ))
    flow.append(body(
        styles,
        "where the denominator is the ideal DCG, computed by sorting "
        "the relevance grades in decreasing order before applying the "
        "logarithmic position discount.",
    ))

    # 6. Choosing a model
    flow.append(section(styles, "6", "Choosing a Model"))
    flow += bullet_list(styles, [
        "<b>TF&minus;IDF</b> &mdash; predictable, deterministic, and "
        "scores in [0,&nbsp;1]; preferred for small corpora and ensembles "
        "where a normalised signal is required.",
        "<b>Okapi BM25</b> &mdash; the general-purpose default. "
        "Outperforms TF&minus;IDF on virtually every benchmark and "
        "handles long documents gracefully through length normalization.",
    ])
    return flow
