# bourse-casa-api

> **API REST live et gratuite de la Bourse de Casablanca**
> Cours en temps réel, indices, actions, historique OHLCV — FastAPI + Python 2026

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green?logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-ready-blue?logo=docker)
![License](https://img.shields.io/badge/License-MIT-yellow)
![CI/CD](https://github.com/loveoplay2023-hue/bourse-casa-api/actions/workflows/deploy.yml/badge.svg)

---

## Table des matières

- [Description](#description)
- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Installation](#installation)
- [Démarrage rapide](#démarrage-rapide)
- [Endpoints API](#endpoints-api)
- [Docker](#docker)
- [Configuration](#configuration)
- [Contribution](#contribution)
- [Licence](#licence)

---

## Description

`bourse-casa-api` est une API REST complète qui scrape en temps réel les données de la **Bourse de Casablanca (BVC)** via les APIs internes de [casablanca-bourse.com](https://www.casablanca-bourse.com).

Contrairement aux API payantes, cette solution est entièrement **gratuite, illimitée et auto-hébergée**.

### Stack technique

| Composant | Technologie |
|-----------|-------------|
| Framework API | FastAPI 0.109 |
| Serveur ASGI | Uvicorn |
| HTTP Client | requests 2.31 + urllib3 |
| Conteneurisation | Docker + Docker Compose |
| CI/CD | GitHub Actions |
| Python | 3.11 |

---

## Fonctionnalités

- **Marché live** : Prix, variation, volume, capitalisation de toutes les actions cotées
- **Résumé du marché** : Nombre de hausses / baisses / stables, volume total
- **Indices boursiers** : MASI, MSI20, MASI ESG et sous-indices sectoriels
- **Top Gainers / Losers** : Les N actions les plus performantes ou les plus en baisse
- **Top Actifs** : Les N actions les plus actives par volume
- **Historique OHLCV** : Open/High/Low/Close/Volume sur une période donnée
- **Health check** : Endpoint de monitoring
- **Documentation interactive** : Swagger UI intégrée (`/docs`)

---

## Architecture

```
bourse-casa-api/
├── main.py                    # Application FastAPI + routes
├── scraper.py                 # Moteur de scraping (APIs BVC)
├── requirements.txt           # Dépendances Python
├── Dockerfile                 # Image Docker Python 3.11 slim
├── docker-compose.yml         # Stack complète (API + Redis + Nginx)
├── tests/
│   └── test_main.py           # Tests unitaires FastAPI
└── .github/
    └── workflows/
        └── deploy.yml         # CI/CD : Tests + Build + Sécurité
```

---

## Installation

### Prérequis

- Python 3.11+
- pip
- Docker & Docker Compose (optionnel)

### Installation locale

```bash
# 1. Cloner le dépôt
git clone https://github.com/loveoplay2023-hue/bourse-casa-api.git
cd bourse-casa-api

# 2. Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate      # Windows

# 3. Installer les dépendances
pip install -r requirements.txt
```

---

## Démarrage rapide

### Mode développement

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Mode production

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

L'API sera disponible sur : **http://localhost:8000**
Documentation Swagger : **http://localhost:8000/docs**
Documentation ReDoc : **http://localhost:8000/redoc**

---

## Endpoints API

### Info & Résumé

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/` | Info générale + liste des endpoints |
| GET | `/health` | Health check |
| GET | `/docs` | Swagger UI |
| GET | `/redoc` | Documentation ReDoc |

### Marché Live

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/v1/market` | Toutes les actions cotées en temps réel |
| GET | `/api/v1/market/summary` | Résumé du marché (hausse/baisse/volume total) |
| GET | `/api/v1/stocks/{ticker}` | Données d'une action par ticker (ex: `IAM`, `ATW`) |

### Indices

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/v1/indices` | Tous les indices (MASI, MSI20, MASI ESG, sectoriels) |
| GET | `/api/v1/indices/{code}` | Valeur d'un indice spécifique (ex: `MASI`, `MSI20`) |

### Top Listes

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/v1/top/gainers?limit=10` | Top N actions en hausse |
| GET | `/api/v1/top/losers?limit=10` | Top N actions en baisse |
| GET | `/api/v1/top/active?limit=10` | Top N actions les plus actives par volume |

### Historique

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/v1/historical/{ticker}?from_date=YYYY-MM-DD&to_date=YYYY-MM-DD` | Historique OHLCV |

### Exemple de réponse — action

```json
{
  "ticker": "ATW",
  "name": "Attijariwafa Bank",
  "sector": "Banques",
  "last_price": 485.00,
  "variation_pct": 0.52,
  "volume": 125430.00,
  "open": 482.00,
  "high": 487.00,
  "low": 481.00,
  "capitalisation": 86700000000.0
}
```

---

## Docker

### Démarrage avec Docker Compose

```bash
# Démarrer tous les services (API + Redis)
docker-compose up -d

# Démarrer avec Nginx (mode production)
docker-compose --profile production up -d

# Voir les logs
docker-compose logs -f api

# Arrêter les services
docker-compose down
```

### Build manuel

```bash
docker build -t bourse-casa-api:latest .
docker run -d -p 8000:8000 bourse-casa-api:latest
```

---

## Configuration

Variables d'environnement disponibles :

| Variable | Défaut | Description |
|----------|--------|-------------|
| `PORT` | `8000` | Port d'écoute |
| `REDIS_URL` | `redis://localhost:6379/0` | URL Redis pour le cache |
| `CACHE_TTL` | `300` | Durée du cache en secondes |
| `LOG_LEVEL` | `info` | Niveau de log |

---

## Contribution

Les contributions sont les bienvenues !

1. Forkez le projet
2. Créez votre branche (`git checkout -b feature/ma-fonctionnalite`)
3. Commitez vos changements (`git commit -m 'feat: ma fonctionnalité'`)
4. Pushez vers la branche (`git push origin feature/ma-fonctionnalite`)
5. Ouvrez une Pull Request

---

## Licence

MIT License — libre d'utilisation pour usage personnel et éducatif.

---

> **Note** : Ce projet utilise les APIs publiques du site de la Bourse de Casablanca. Respectez les conditions d'utilisation du site.
