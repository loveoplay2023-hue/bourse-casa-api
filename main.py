from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import date
import scraper

app = FastAPI(
    title="Bourse de Casablanca API",
    description="API REST live et gratuite de la Bourse de Casablanca - 2026",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────────────────────
# ROOT
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/", tags=["Info"])
def root():
    return {
        "name": "Bourse de Casablanca API",
        "version": "2.0.0",
        "status": "online",
        "endpoints": [
            "/api/v1/market",
            "/api/v1/market/summary",
            "/api/v1/stocks/{ticker}",
            "/api/v1/indices",
            "/api/v1/indices/{code}",
            "/api/v1/top/gainers",
            "/api/v1/top/losers",
            "/api/v1/top/active",
            "/api/v1/historical/{ticker}",
            "/docs",
        ]
    }

# ─────────────────────────────────────────────────────────────────────────────
# MARCHE LIVE
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/api/v1/market", tags=["Marche Live"])
def get_all_stocks():
    """Toutes les actions cotees en temps reel"""
    data = scraper.get_market_live()
    if not data:
        raise HTTPException(status_code=503, detail="Donnees indisponibles")
    return {"count": len(data), "data": data}

@app.get("/api/v1/market/summary", tags=["Marche Live"])
def get_summary():
    """Resume global du marche (nombre hausse/baisse, volume total)"""
    data = scraper.get_market_summary()
    if not data:
        raise HTTPException(status_code=503, detail="Donnees indisponibles")
    return data

@app.get("/api/v1/stocks/{ticker}", tags=["Marche Live"])
def get_stock(ticker: str):
    """Donnees d'une action par son ticker (ex: IAM, ATW, COSUMAR, CIH)"""
    data = scraper.get_stock_by_ticker(ticker)
    if not data:
        raise HTTPException(status_code=404, detail=f"Ticker '{ticker}' non trouve")
    return data

# ─────────────────────────────────────────────────────────────────────────────
# INDICES
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/api/v1/indices", tags=["Indices"])
def get_all_indices():
    """Tous les indices (MASI, MSI20, MASI ESG, indices sectoriels)"""
    data = scraper.get_indices()
    if not data:
        raise HTTPException(status_code=503, detail="Donnees indisponibles")
    return {"count": len(data), "data": data}

@app.get("/api/v1/indices/{code}", tags=["Indices"])
def get_index(code: str):
    """Donnees d'un indice specifique (ex: MASI, MSI20, BANK, ASSUR)"""
    data = scraper.get_index_by_code(code)
    if not data:
        raise HTTPException(status_code=404, detail=f"Indice '{code}' non trouve")
    return data

# ─────────────────────────────────────────────────────────────────────────────
# TOP LISTES
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/api/v1/top/gainers", tags=["Top Listes"])
def top_gainers(limit: int = Query(default=10, ge=1, le=50)):
    """Les N actions avec la plus forte hausse"""
    data = scraper.get_top_gainers(limit)
    return {"count": len(data), "data": data}

@app.get("/api/v1/top/losers", tags=["Top Listes"])
def top_losers(limit: int = Query(default=10, ge=1, le=50)):
    """Les N actions avec la plus forte baisse"""
    data = scraper.get_top_losers(limit)
    return {"count": len(data), "data": data}

@app.get("/api/v1/top/active", tags=["Top Listes"])
def most_active(limit: int = Query(default=10, ge=1, le=50)):
    """Les N actions les plus actives (par volume)"""
    data = scraper.get_most_active(limit)
    return {"count": len(data), "data": data}

# ─────────────────────────────────────────────────────────────────────────────
# HISTORIQUE
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/api/v1/historical/{ticker}", tags=["Historique"])
def get_historical(
    ticker: str,
    from_date: str = Query(description="Date debut YYYY-MM-DD"),
    to_date: str = Query(description="Date fin YYYY-MM-DD"),
):
    """Historique OHLCV d'un titre sur une periode donnee"""
    data = scraper.get_historical(ticker, from_date, to_date)
    if data is None:
        raise HTTPException(status_code=404, detail=f"Historique introuvable pour '{ticker}'")
    return {"ticker": ticker.upper(), "count": len(data), "data": data}

# ─────────────────────────────────────────────────────────────────────────────
# HEALTH CHECK
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/health", tags=["Info"])
def health():
    return {"status": "ok"}
