import requests
import json
import re
import time
import warnings
from urllib3.exceptions import InsecureRequestWarning

warnings.filterwarnings('ignore')
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json',
}

# ─── BUILD ID CACHE (1h) ─────────────────────────────────────────────────────
_build_id_cache = {"id": None, "ts": 0}

def get_build_id():
    """Recupere le buildId Next.js depuis la page d'accueil (cache 1h)"""
    now = time.time()
    if _build_id_cache["id"] and (now - _build_id_cache["ts"]) < 3600:
        return _build_id_cache["id"]
    try:
        r = requests.get("https://www.casablanca-bourse.com/fr",
                         headers=HEADERS, verify=False, timeout=15)
        match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
                          r.text)
        if match:
            build_id = json.loads(match.group(1)).get("buildId")
            if build_id:
                _build_id_cache["id"] = build_id
                _build_id_cache["ts"] = now
                return build_id
    except Exception as e:
        print(f"Erreur buildId: {e}")
    return _build_id_cache.get("id")

# ─── MARCHE LIVE ─────────────────────────────────────────────────────────────
def get_market_live():
    """Toutes les actions en live (cours, variation, volume, capitalisation)"""
    try:
        r = requests.get(
            "https://www.casablanca-bourse.com/api/proxy/fr/api/bourse/dashboard/ticker",
            params={"marche": 59, "class[]": 50},
            headers=HEADERS, verify=False, timeout=15
        )
        if r.status_code == 200:
            stocks = r.json()["data"]["values"]
            result = []
            for s in stocks:
                result.append({
                    "ticker":         s.get("ticker", ""),
                    "name":           s.get("label", ""),
                    "sector":         s.get("sous_secteur", ""),
                    "last_price":     s.get("field_cours_courant"),
                    "ref_price":      s.get("field_static_reference_price"),
                    "open":           s.get("field_opening_price"),
                    "high":           s.get("field_high_price"),
                    "low":            s.get("field_low_price"),
                    "variation_pct":  s.get("field_var_veille"),
                    "volume":         s.get("field_cumul_volume_echange"),
                    "qty_traded":     s.get("field_cumul_titres_echanges"),
                    "nb_trades":      s.get("field_total_trades"),
                    "capitalisation": s.get("field_capitalisation"),
                    "status":         s.get("field_etat_cot_val"),
                    "bid_price":      s.get("field_best_bid_price"),
                    "ask_price":      s.get("field_best_ask_price"),
                })
            return result
    except Exception as e:
        print(f"Erreur market live: {e}")
    return []

def get_stock_by_ticker(ticker: str):
    """Donnees d'une action par son ticker (ex: IAM, ATW, COSUMAR)"""
    stocks = get_market_live()
    ticker_upper = ticker.upper()
    for s in stocks:
        if s["ticker"] == ticker_upper or s["name"].upper() == ticker_upper:
            return s
    return None

# ─── INDICES ─────────────────────────────────────────────────────────────────
def get_indices():
    """MASI, MASI20, MASI ESG, indices sectoriels"""
    try:
        r = requests.get(
            "https://www.casablanca-bourse.com/api/proxy/fr/api/bourse/dashboard/grouped_index_watch",
            headers=HEADERS, verify=False, timeout=15
        )
        if r.status_code == 200:
            raw = r.json().get("data", [])
            result = []
            for category in raw:
                cat_name = category.get("title", "")
                for item in category.get("items", []):
                    index_url = item.get("index_url", "")
                    code = index_url.split("/")[-1] if index_url else ""
                    result.append({
                        "category":      cat_name,
                        "name":          item.get("index", ""),
                        "code":          code,
                        "value":         item.get("field_index_value"),
                        "previous":      item.get("veille"),
                        "variation_pct": item.get("field_var_veille"),
                        "variation_ytd": item.get("field_var_year"),
                        "high":          item.get("field_index_high_value"),
                        "low":           item.get("field_index_low_value"),
                        "capitalisation":item.get("field_market_capitalisation"),
                    })
            return result
    except Exception as e:
        print(f"Erreur indices: {e}")
    return []

def get_index_by_code(code: str):
    """Donnees d'un indice par son code (ex: MASI, MSI20)"""
    indices = get_indices()
    code_upper = code.upper()
    for idx in indices:
        if idx["code"].upper() == code_upper:
            return idx
    return None

# ─── HISTORIQUE ──────────────────────────────────────────────────────────────
def get_symbol_id(ticker: str):
    """Trouve le drupal_internal__id d'un ticker"""
    build_id = get_build_id()
    if not build_id:
        return None
    try:
        url = f"https://www.casablanca-bourse.com/_next/data/{build_id}/fr/live-market/marche-actions-listing.json"
        r = requests.get(url, headers=HEADERS, verify=False, timeout=20)
        if r.status_code == 200:
            data = r.json()
            paragraphs = data["pageProps"]["node"]["field_vactory_paragraphs"]
            for block in paragraphs:
                widget_id = block.get("field_vactory_component", {}).get("widget_id", "")
                if widget_id == "bourse_data_listing:marches-actions":
                    raw = json.loads(block["field_vactory_component"]["widget_data"])
                    instruments = raw["extra_field"]["collection"]["data"]["data"]
                    for item in instruments:
                        url_inst = item["relationships"]["symbol"]["links"]["related"]["href"]
                        r2 = requests.get(url_inst, verify=False, timeout=10)
                        if r2.status_code == 200:
                            attrs = r2.json()["data"]["attributes"]
                            if attrs.get("symbol", "").upper() == ticker.upper():
                                return str(attrs.get("drupal_internal__id"))
    except Exception as e:
        print(f"Erreur symbol_id: {e}")
    return None

def get_historical(ticker: str, from_date: str, to_date: str):
    """Historique OHLCV d'un titre. from_date/to_date : YYYY-MM-DD"""
    symbol_id = get_symbol_id(ticker)
    if not symbol_id:
        return None
    h = {**HEADERS, "Accept": "application/vnd.api+json", "Content-Type": "application/vnd.api+json"}
    all_data = []
    offset = 0
    while True:
        params = [
            ("fields[instrument_history]", "symbol,created,openingPrice,coursCourant,highPrice,lowPrice,cumulTitresEchanges,cumulVolumeEchange,totalTrades,capitalisation,closingPrice"),
            ("sort[date-seance][path]", "created"),
            ("sort[date-seance][direction]", "DESC"),
            ("filter[published]", "1"),
            ("page[offset]", str(offset)),
            ("page[limit]", "250"),
            ("filter[filter-date-start-vh][condition][path]", "field_seance_date"),
            ("filter[filter-date-start-vh][condition][operator]", ">="),
            ("filter[filter-date-start-vh][condition][value]", from_date),
            ("filter[filter-date-end-vh][condition][path]", "field_seance_date"),
            ("filter[filter-date-end-vh][condition][operator]", "<="),
            ("filter[filter-date-end-vh][condition][value]", to_date),
            ("filter[filter-historique-instrument-emetteur][condition][path]", "symbol.meta.drupal_internal__target_id"),
            ("filter[filter-historique-instrument-emetteur][condition][operator]", "="),
            ("filter[filter-historique-instrument-emetteur][condition][value]", symbol_id),
        ]
        try:
            r = requests.get(
                "https://www.casablanca-bourse.com/api/proxy/fr/api/bourse_data/instrument_history",
                params=params, headers=h, verify=False, timeout=20
            )
            if r.status_code == 200:
                data = r.json()
                if "data" in data and data["data"]:
                    for item in data["data"]:
                        a = item["attributes"]
                        all_data.append({
                            "date":       a.get("created"),
                            "open":       a.get("openingPrice"),
                            "close":      a.get("closingPrice"),
                            "last":       a.get("coursCourant"),
                            "high":       a.get("highPrice"),
                            "low":        a.get("lowPrice"),
                            "volume":     a.get("cumulVolumeEchange"),
                            "qty":        a.get("cumulTitresEchanges"),
                            "trades":     a.get("totalTrades"),
                            "market_cap": a.get("capitalisation"),
                        })
                    if len(data["data"]) < 250:
                        break
                    offset += 250
                    time.sleep(0.3)
                else:
                    break
            else:
                break
        except Exception:
            break
    return all_data if all_data else None

# ─── TOP GAINERS / LOSERS / ACTIFS ───────────────────────────────────────────
def get_top_gainers(limit: int = 10):
    stocks = [s for s in get_market_live() if s["variation_pct"] is not None and float(s["variation_pct"]) > 0]
    stocks.sort(key=lambda x: float(x["variation_pct"]), reverse=True)
    return stocks[:limit]

def get_top_losers(limit: int = 10):
    stocks = [s for s in get_market_live() if s["variation_pct"] is not None and float(s["variation_pct"]) < 0]
    stocks.sort(key=lambda x: float(x["variation_pct"]))
    return stocks[:limit]

def get_most_active(limit: int = 10):
    stocks = [s for s in get_market_live() if s["volume"] is not None]
    stocks.sort(key=lambda x: float(x["volume"] or 0), reverse=True)
    return stocks[:limit]

# ─── RESUME MARCHE ────────────────────────────────────────────────────────────
def get_market_summary():
    stocks = get_market_live()
    gainers = [s for s in stocks if s["variation_pct"] and float(s["variation_pct"]) > 0]
    losers  = [s for s in stocks if s["variation_pct"] and float(s["variation_pct"]) < 0]
    stable  = [s for s in stocks if s["variation_pct"] and float(s["variation_pct"]) == 0]
    total_vol = sum(float(s["volume"] or 0) for s in stocks)
    total_cap = sum(float(s["capitalisation"] or 0) for s in stocks)
    return {
        "total_instruments": len(stocks),
        "gainers": len(gainers),
        "losers":  len(losers),
        "stable":  len(stable),
        "total_volume_mad": round(total_vol, 2),
        "total_capitalisation_mad": round(total_cap, 2),
    }
