"""
Tests unitaires pour l'API Bourse de Casablanca
Utilise TestClient de FastAPI (httpx en backend)
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Import de l'application
from main import app

client = TestClient(app)


# ─────────────────────────────────────────────────────────────────────────────
# Tests de base (sans scraping réel)
# ─────────────────────────────────────────────────────────────────────────────

def test_root():
    """Test de l'endpoint racine"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert data["status"] == "online"
    assert "endpoints" in data


def test_health():
    """Test du health check"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_docs_available():
    """Test que la documentation Swagger est accessible"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_redoc_available():
    """Test que la documentation ReDoc est accessible"""
    response = client.get("/redoc")
    assert response.status_code == 200


# ─────────────────────────────────────────────────────────────────────────────
# Tests avec mock du scraper
# ─────────────────────────────────────────────────────────────────────────────

MOCK_STOCKS = [
    {
        "ticker": "ATW",
        "name": "Attijariwafa Bank",
        "sector": "Banques",
        "last_price": 485.0,
        "ref_price": 482.5,
        "open": 482.0,
        "high": 487.0,
        "low": 481.0,
        "variation_pct": "0.52",
        "volume": "125430.0",
        "qty_traded": "258",
        "nb_trades": "45",
        "capitalisation": "86700000000.0",
        "status": "1",
        "bid_price": 484.0,
        "ask_price": 486.0,
    },
    {
        "ticker": "IAM",
        "name": "Maroc Telecom",
        "sector": "Telecoms",
        "last_price": 112.5,
        "ref_price": 113.0,
        "open": 113.0,
        "high": 113.5,
        "low": 112.0,
        "variation_pct": "-0.44",
        "volume": "85000.0",
        "qty_traded": "756",
        "nb_trades": "32",
        "capitalisation": "98400000000.0",
        "status": "1",
        "bid_price": 112.0,
        "ask_price": 113.0,
    },
]

MOCK_INDICES = [
    {
        "category": "Indices généraux",
        "name": "MASI",
        "code": "MASI",
        "value": 13245.67,
        "previous": 13198.45,
        "variation_pct": "0.36",
        "variation_ytd": "2.14",
        "high": 13267.0,
        "low": 13190.0,
        "capitalisation": "700000000000.0",
    }
]


@patch("scraper.get_market_live", return_value=MOCK_STOCKS)
def test_market_endpoint(mock_scraper):
    """Test de l'endpoint /api/v1/market"""
    response = client.get("/api/v1/market")
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert "data" in data
    assert data["count"] == 2
    assert data["data"][0]["ticker"] == "ATW"


@patch("scraper.get_market_live", return_value=[])
def test_market_empty(mock_scraper):
    """Test quand le marché ne retourne rien (503)"""
    response = client.get("/api/v1/market")
    assert response.status_code == 503


@patch("scraper.get_market_live", return_value=MOCK_STOCKS)
def test_stock_by_ticker_found(mock_scraper):
    """Test de la recherche d'une action par ticker"""
    response = client.get("/api/v1/stocks/ATW")
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "ATW"
    assert data["name"] == "Attijariwafa Bank"


@patch("scraper.get_market_live", return_value=MOCK_STOCKS)
def test_stock_by_ticker_not_found(mock_scraper):
    """Test quand le ticker n'existe pas (404)"""
    response = client.get("/api/v1/stocks/UNKNOWN")
    assert response.status_code == 404


@patch("scraper.get_indices", return_value=MOCK_INDICES)
def test_indices_endpoint(mock_scraper):
    """Test de l'endpoint /api/v1/indices"""
    response = client.get("/api/v1/indices")
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert data["count"] == 1
    assert data["data"][0]["name"] == "MASI"


@patch("scraper.get_market_live", return_value=MOCK_STOCKS)
def test_top_gainers(mock_scraper):
    """Test des top gainers"""
    response = client.get("/api/v1/top/gainers")
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert "data" in data
    # ATW a variation positive, donc doit être dans gainers
    tickers = [s["ticker"] for s in data["data"]]
    assert "ATW" in tickers


@patch("scraper.get_market_live", return_value=MOCK_STOCKS)
def test_top_losers(mock_scraper):
    """Test des top losers"""
    response = client.get("/api/v1/top/losers")
    assert response.status_code == 200
    data = response.json()
    # IAM a variation négative
    tickers = [s["ticker"] for s in data["data"]]
    assert "IAM" in tickers


@patch("scraper.get_market_live", return_value=MOCK_STOCKS)
def test_top_active(mock_scraper):
    """Test des actions les plus actives"""
    response = client.get("/api/v1/top/active")
    assert response.status_code == 200
    data = response.json()
    assert "count" in data


@patch("scraper.get_market_live", return_value=MOCK_STOCKS)
def test_market_summary(mock_scraper):
    """Test du résumé du marché"""
    response = client.get("/api/v1/market/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_instruments" in data
    assert "gainers" in data
    assert "losers" in data
    assert data["total_instruments"] == 2
    assert data["gainers"] == 1
    assert data["losers"] == 1


def test_historical_missing_params():
    """Test historique sans paramètres obligatoires (422)"""
    response = client.get("/api/v1/historical/ATW")
    assert response.status_code == 422
