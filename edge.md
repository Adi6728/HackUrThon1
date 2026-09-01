# Edge Cases — Multi-Agent Financial Intelligence System

> Every case below has a **Detection** method, a **Handling** strategy, and a **User-Facing Behaviour** so nothing silently fails.

---

## 1. Market Data Layer (`services/market_data/`)

### 1.1 yfinance / Feed Failures

| # | Edge Case | Detection | Handling | User-Facing |
|---|-----------|-----------|----------|-------------|
| 1.1.1 | Ticker symbol does not exist (e.g. typo `RELIANCEE`) | `yf.Ticker().info` returns empty dict or raises | Return `DataUnavailableError`; reject request early | "Ticker not found. Please verify the symbol." |
| 1.1.2 | Market is closed / weekend / public holiday | OHLCV rows are empty for the requested date | Serve last known close; flag `market_open: false` in response | Signal card shows "Market Closed — last data from {date}" |
| 1.1.3 | Yahoo Finance returns HTTP 429 (rate-limit) | HTTP status code check in `fetcher.py` | Switch to CSV mock in `data/mock/`; log degraded state | `DegradedDataBanner` shown on dashboard |
| 1.1.4 | Partial data — some fields null (e.g. no volume) | Schema validation via Pydantic `.model_validate()` | Fill nulls with `None`; skip indicators that require the missing field | Indicator card shows "Insufficient data" for affected indicator |
| 1.1.5 | Yahoo Finance changes internal HTML structure (scraper break) | `fetcher.py` raises `KeyError` or `AttributeError` | Fall through to CSV mock; alert in log | Same as 1.1.3 |
| 1.1.6 | Stale cache served after TTL but feed still down | TTL expiry triggers re-fetch; re-fetch fails | Serve stale data with age timestamp; flag `stale: true` | Banner: "Data may be up to {age}s old" |
| 1.1.7 | Negative or zero price in feed (data corruption) | `price <= 0` guard in `models.py` | Discard record; use previous valid snapshot | Agent outputs note "price data anomaly detected" |

### 1.2 Technical Indicator Computation (`indicators.py`)

| # | Edge Case | Detection | Handling | User-Facing |
|---|-----------|-----------|----------|-------------|
| 1.2.1 | Fewer candles than indicator window (e.g. 5 rows for RSI-14) | `len(df) < period` check | Return `confidence: 0.0`; omit that indicator | Signal card shows "Insufficient history for RSI" |
| 1.2.2 | All prices identical (zero variance) — division-by-zero in Bollinger | `std == 0` guard | Set band width to 0; mark signal as "Neutral / No Volatility" | Neutral signal badge |
| 1.2.3 | NaN propagation through pandas rolling window | `df.isnull().any()` check after computation | Forward-fill then drop leading NaNs | Silently handled; no NaN reaches agent |
| 1.2.4 | Single-day IPO — no historical data at all | Empty DataFrame | Skip all indicator-based signals; rely only on fundamental + sentiment agents | "New listing — technical signals unavailable" |

---

## 2. Document Ingestion & RAG (`services/document_ingestion/`, `services/rag/`)

| # | Edge Case | Detection | Handling | User-Facing |
|---|-----------|-----------|----------|-------------|
| 2.1 | Uploaded PDF is password-protected | PyMuPDF raises `fitz.FileDataError` | Return `DocumentParseError`; skip file | "Could not read document — it may be password protected." |
| 2.2 | PDF is a scanned image (no text layer) | `page.get_text()` returns empty string for all pages | Fall back to OCR (pytesseract) or skip with warning | "Document has no text layer — skipped." |
| 2.3 | Duplicate document uploaded | Hash (SHA-256) of file bytes compared against ChromaDB metadata | Skip re-ingestion; return "already indexed" | "Document already in knowledge base." |
| 2.4 | Document is extremely large (>50 MB / >500 pages) | File size + page count check before processing | Cap at first 200 pages; warn user | "Large document — indexed first 200 pages only." |
| 2.5 | Vector store collection empty at query time | `collection.count() == 0` before retrieval | Return empty `retrieved_chunks: []`; agent uses LLM knowledge only; marks citation as "No filing available" | Citation shows "No documents indexed" |
| 2.6 | RAG returns chunks from wrong company | Metadata filter `{"ticker": ticker}` not applied | Always pass ticker metadata filter in `retriever.py` | Prevents cross-company hallucination |
| 2.7 | Embedding model unavailable (HuggingFace download fails offline) | `OSError` on `SentenceTransformer` load | Check `~/.cache` first; if missing, raise startup error with clear message | App startup fails with actionable message: "Run with internet to download embedding model first." |
| 2.8 | Query returns zero similarity matches (score below threshold) | Cosine similarity < 0.3 for all chunks | Return empty results; agent notes "no relevant filings found" | Attribution section shows "No relevant documents found" |
| 2.9 | ChromaDB collection corrupted on disk | Exception on `collection.query()` | Delete and reinitialise collection; re-run ingest script | Log error + admin alert; user sees "Knowledge base rebuilding…" |

---

## 3. Multi-Agent Orchestration (`agents/`, `orchestrator/`)

### 3.1 Individual Agent Failures

| # | Edge Case | Detection | Handling | User-Facing |
|---|-----------|-----------|----------|-------------|
| 3.1.1 | Agent returns malformed JSON (LLM hallucination) | Pydantic `ValidationError` on parse | Retry once with stricter prompt; if still fails, mark that agent's output as `null` | "Technical analysis unavailable for this run." |
| 3.1.2 | Agent times out (Groq slow / network lag) | `asyncio.wait_for` with per-agent timeout (default 20 s) | Return partial result with `timed_out: true`; synthesis agent notes missing input | Warning badge on the affected agent card |
| 3.1.3 | Groq returns HTTP 429 (rate limit) | `groq.RateLimitError` | Exponential backoff: 2 s → 4 s → 8 s (max 3 retries) before marking as failed | Brief spinner; user unaware unless all retries fail |
| 3.1.4 | Groq returns HTTP 503 / 500 (server error) | `groq.APIStatusError` with 5xx | Retry once after 5 s; if fails, mark agent failed | Same as 3.1.2 |
| 3.1.5 | Agent returns confidence = 0 for all signals | Post-parse validation: `all(s.confidence == 0)` | Do not surface signal as actionable; flag in synthesis | "Confidence too low — no actionable signal." |
| 3.1.6 | LLM returns a refusal (e.g. "I cannot provide financial advice") | Response contains refusal keywords | Detect refusal pattern in `contracts.py` validator; retry with rephrased prompt | Agent silently retried; user never sees refusal text |

### 3.2 Conflict & Synthesis

| # | Edge Case | Detection | Handling | User-Facing |
|---|-----------|-----------|----------|-------------|
| 3.2.1 | All three agents contradict each other (bull/bear/neutral) | `conflict_resolver.py` checks signal direction spread | Weighted majority vote; lower overall confidence; add explicit caveat in synthesis | Recommendation shown as "Mixed Signals — proceed cautiously" |
| 3.2.2 | Only one of three agents succeeds | Count of non-null agent results < 2 | Synthesis proceeds with available agents; explicitly notes missing inputs | "Analysis based on {n}/3 agents — results may be incomplete." |
| 3.2.3 | Zero agents succeed | All results are `null` | Abort synthesis; return `pipeline_failed: true` | "Analysis could not be completed. Please try again." |
| 3.2.4 | Synthesis agent itself times out | Outer pipeline timeout (60 s total) | Return last cached result for this ticker if available | "Showing previous analysis from {timestamp}." |
| 3.2.5 | Agents agree but contradict user's existing position | Portfolio holdings vs signal direction check in synthesis | Add explicit risk note: "This signal conflicts with your current position in {ticker}." | Conflict note shown in `RecommendationBanner` |

---

## 4. User Profiling & Personalization (`services/user_profile/`)

| # | Edge Case | Detection | Handling | User-Facing |
|---|-----------|-----------|----------|-------------|
| 4.1 | New user with no profile | `profile_id` not found in DB | Serve a default conservative profile; prompt to complete profile | Onboarding nudge: "Set your risk profile for personalised insights." |
| 4.2 | User portfolio has a stock that is delisted | Ticker no longer found in yfinance | Mark holding as `status: delisted`; exclude from live signals | Portfolio row shows "Delisted" badge; excluded from risk score |
| 4.3 | Portfolio concentration reaches 100% in one stock | HHI score = 10,000 | Flag `extreme_concentration: true` in risk scorer | Warning banner: "High concentration risk detected." |
| 4.4 | Risk tolerance set to maximum but portfolio is all fixed income | Mismatch between `risk_tolerance` and portfolio composition | Note discrepancy in synthesis agent prompt context | "Your portfolio composition does not match your stated risk profile." |
| 4.5 | User submits negative quantity or negative cost basis | Pydantic `Field(gt=0)` constraint on `Portfolio` schema | Reject with 422 validation error | Form shows field-level validation error |
| 4.6 | Behaviour tracker grows unbounded | Row count > 10,000 per user | Trim oldest 20% of records on insert | Silent maintenance; no user impact |
| 4.7 | Concurrent profile updates from two browser tabs | SQLite row-level write conflict | Use `aiosqlite` with serialised writes; last-write-wins with timestamp | Second tab receives 409 Conflict response; prompts refresh |

---

## 5. API Gateway (`api/`)

| # | Edge Case | Detection | Handling | User-Facing |
|---|-----------|-----------|----------|-------------|
| 5.1 | `POST /api/analyze` called with empty ticker string | Pydantic `min_length=1` validator | 422 Unprocessable Entity | Form-level error |
| 5.2 | Same ticker analyzed concurrently by same user (double-click) | In-flight request cache keyed by `(user_id, ticker)` | Return 202 with `analysis_in_progress: true`; client polls | Button disabled while analysis runs |
| 5.3 | Request body exceeds size limit (giant document upload) | FastAPI `max_upload_size` middleware (set to 20 MB) | 413 Request Entity Too Large | "File too large. Maximum 20 MB." |
| 5.4 | `GET /api/market/{ticker}` for an unknown ticker | yfinance returns empty | 404 with `{"error": "ticker_not_found"}` | Error toast on dashboard |
| 5.5 | Malformed JSON body | FastAPI request parsing | 400 Bad Request | Generic error toast |
| 5.6 | API server restarts mid-analysis | Client WebSocket disconnects; reconnect triggers | Client auto-reconnects; re-polls `/api/history` for last result | Toast: "Reconnected. Loading last result…" |
| 5.7 | CORS blocked (frontend on different port during dev) | Browser console CORS error | `allow_origins=["http://localhost:5173"]` set in `main.py` | N/A — development config |

---

## 6. WebSocket Layer (`api/ws/`)

| # | Edge Case | Detection | Handling | User-Facing |
|---|-----------|-----------|----------|-------------|
| 6.1 | Client disconnects mid-stream | `WebSocketDisconnect` exception in `signal_stream.py` | Remove from active connection set; stop sending | Silent — client simply stops receiving |
| 6.2 | Client reconnects before previous stream finishes | New WS connection for same `user_id` | Cancel old stream task; start fresh | Seamless from user perspective |
| 6.3 | No subscribers for a ticker stream | Active connection set is empty | Pause data fetching for that ticker; resume on next subscriber | Saves fetch quota |
| 6.4 | Server pushes faster than client can consume | Client-side queue grows | Implement back-pressure: server checks ACK before next push | Prevents browser freeze |
| 6.5 | WebSocket message serialisation fails (non-JSON-serialisable field) | `json.dumps()` raises `TypeError` | Catch, log, and skip the offending message | Silent skip; no crash |

---

## 7. Frontend Dashboard (`frontend/src/`)

| # | Edge Case | Detection | Handling | User-Facing |
|---|-----------|-----------|----------|-------------|
| 7.1 | API is unreachable (backend not running) | `fetch` throws `NetworkError` in `useMarketData.js` | Show full-page "Backend unavailable" state; retry every 10 s | Offline banner with countdown |
| 7.2 | Chart receives empty data array | `data.length === 0` guard in `LiveChart.jsx` | Render empty-state placeholder instead of crashing | "No chart data available yet." |
| 7.3 | Agent trace panel receives `null` reasoning steps | `steps == null` guard in `AgentTracePanel.jsx` | Show "Reasoning not available" placeholder | Graceful empty state |
| 7.4 | Recommendation text is extremely long (LLM verbose output) | CSS `max-height` + `overflow-y: auto` on `RecommendationBanner` | Scrollable container; no layout break | Text remains readable |
| 7.5 | Citation popover has no source text | `citation.text == null` check in `CitationPopover.jsx` | Render "Source document not available" | Tooltip still appears, no crash |
| 7.6 | Portfolio table has zero holdings | `holdings.length === 0` | Render empty-state with "Add your first holding" CTA | Friendly empty state |
| 7.7 | `DegradedDataBanner` shown while data is actually fine | `degraded` flag clears within 30 s when feed recovers | Auto-dismiss banner when `health_checker` reports clean | Banner fades out automatically |
| 7.8 | Browser tab goes to background (Page Visibility API) | `document.visibilityState === "hidden"` | Pause WebSocket ticks; resume on tab focus | Prevents unnecessary traffic |
| 7.9 | Number formatting for very large values (e.g. market cap ₹2,40,00,000) | Intl formatter not covering Indian number system | Use `Intl.NumberFormat("en-IN")` everywhere | Correct lakh/crore formatting |
| 7.10 | User navigates away mid-analysis | React Router route change detected | Cancel in-flight fetch via `AbortController`; clean up WS subscription | No stale state on return |

---

## 8. Logging & Metrics (`services/logging/`)

| # | Edge Case | Detection | Handling | User-Facing |
|---|-----------|-----------|----------|-------------|
| 8.1 | Metrics store write fails (disk full / permission) | `sqlite3.OperationalError` on insert | Log to stderr only; do not crash pipeline | No user impact; metrics gap in DB |
| 8.2 | Session recorder captures PII in agent output | Regex scan for Aadhaar / PAN patterns before persistence | Redact matched patterns before writing | Transparent to user |
| 8.3 | Latency tracker overflows (session runs > 24 h) | `time.monotonic()` delta > threshold | Cap latency recording at 24 h; log warning | No crash |
| 8.4 | Signal accuracy computed on a delisted stock | Ticker removed from yfinance | Mark accuracy entry as `unverifiable`; exclude from averages | Metrics panel shows N/A for that entry |
| 8.5 | Concurrent sessions write to same SQLite file | `aiosqlite` connection pool | Use WAL mode (`PRAGMA journal_mode=WAL`) for concurrent reads | No data corruption |

---

## 9. Data Integrity & Cross-Cutting Concerns

| # | Edge Case | Detection | Handling | User-Facing |
|---|-----------|-----------|----------|-------------|
| 9.1 | Groq returns inconsistent confidence values (> 1.0 or < 0.0) | Pydantic `Field(ge=0.0, le=1.0)` | Clamp to `[0.0, 1.0]` before downstream use | Confidence bar always renders correctly |
| 9.2 | Two agents cite the same source with conflicting extractions | `citation_tracker.py` deduplication + conflict flag | Mark conflicting citations; synthesis agent explicitly notes the discrepancy | "Sources conflict on this point — see citations." |
| 9.3 | Unicode / Devanagari characters in ticker or company name | Pydantic string validators; `str.encode("utf-8")` test | Ensure all DB columns and API responses use UTF-8 encoding | No garbled text anywhere |
| 9.4 | Clock skew between server and client (timestamp mismatch) | All timestamps stored as UTC ISO-8601 | Convert to user local time only in the UI layer via `Intl.DateTimeFormat` | Consistent timestamps |
| 9.5 | Entire pipeline produces recommendation but Groq context window exceeded mid-run | `groq.BadRequestError` with token count info | Truncate least-relevant RAG chunks first; retry with smaller context | Transparent retry; slightly fewer citations |
| 9.6 | System run under Python < 3.10 (missing `match`/`asyncio.TaskGroup`) | Version check at startup in `main.py` | `sys.version_info < (3, 10)` → raise `RuntimeError` with clear message | Startup fails immediately with version instruction |
| 9.7 | Environment variables / API keys missing at startup | `os.environ` check for `GROQ_API_KEY`, `GNEWS_API_KEY` in `main.py` lifespan | Raise `EnvironmentError` with a list of missing variables | "Missing environment variables: GROQ_API_KEY. Add to .env file." |
| 9.8 | Demo run with no internet (offline judging environment) | All external requests fail | Detect offline at startup: ping `8.8.8.8`; if offline, force full mock mode | Toast: "Running in offline demo mode — using mock data." |

---

## 10. Degraded-Mode Decision Tree

```
External Request (market data / news / LLM)
            │
    ┌───────▼────────┐
    │  Request OK?   │
    └───────┬────────┘
        NO  │  YES
            │   └──→ Normal path ✅
    ┌───────▼──────────────────┐
    │  Is cached result fresh? │  (age < TTL)
    └───────┬──────────────────┘
        NO  │  YES
            │   └──→ Serve cache + "may be stale" flag ⚠️
    ┌───────▼──────────────────────┐
    │  Is CSV / mock fixture avail?│
    └───────┬──────────────────────┘
        NO  │  YES
            │   └──→ Serve mock + DegradedDataBanner 🟡
    ┌───────▼────────────────────────────┐
    │  Can partial result be synthesised?│  (≥1 agent succeeded)
    └───────┬────────────────────────────┘
        NO  │  YES
            │   └──→ Partial result + missing-agent warning 🟡
    ┌───────▼───────────────┐
    │  Full pipeline failure │  → Return error + clear message ❌
    └───────────────────────┘
```

---

## 11. Quick Reference — Error Code Catalogue

| HTTP Code | When Used | Example Scenario |
|-----------|-----------|-----------------|
| `400` | Malformed request body | Invalid JSON sent to `/api/analyze` |
| `404` | Resource not found | Unknown ticker in `/api/market/{ticker}` |
| `409` | Concurrent write conflict | Two tabs updating profile simultaneously |
| `413` | Payload too large | Document upload > 20 MB |
| `422` | Validation failure | Empty ticker string, negative quantity |
| `429` | Rate limit (internal guard) | Client polling faster than 1 req/s |
| `500` | Unhandled exception | Unexpected LLM response format |
| `503` | Dependency unavailable | Groq API down and all retries exhausted |
