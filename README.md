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

`bourse-casa-api` est une API REST complète qui scrape en temps réel les données de la **Bourse de Casablanca (BVC)** à partir du site officiel [casablanca-bourse.com](https://www.casablanca-bourse.com).

Contrairement aux API payantes, cette solution est entièrement **gratuite, illimitée et auto-hébergée**.

### Stack technique

| Composant | Technologie |
|-----------|-------------|
| Framework API | FastAPI 0.109 |
| Serveur ASGI | Uvicorn |
| Scraping | BeautifulSoup4 + lxml |
| Cache | Redis 7 |
| Conteneurisation | Docker + Docker Compose |
| CI/CD | GitHub Actions |
| Python | 3.11 |

---

## Fonctionnalités

- **Cours en temps réel** : Prix, variation, volume de toutes les actions cotées
- **Indices boursiers** : MASI, MADEX et sous-indices sectoriels
- **Informations sociétés** : Secteur, capital, ISIN, dividendes
- **Top actives** : Les N actions les plus actives par volume
- **Historique OHLCV** : Open/High/Low/Close/Volume sur une période donnée
- **Health check** : Endpoint de monitoring
- **Documentation interactive** : Swagger UI intégrée (`/docs`)

---

## Architecture

```
bourse-casa-api/
├── main.py              # Application FastAPI + routes
├── scraper.py           # Moteur de scraping BeautifulSoup4
├── requirements.txt     # Dépendances Python
├── Dockerfile           # Image Docker Python 3.11 slim
├── docker-compose.yml   # Stack complète (API + Redis + Nginx)
└── .github/
    └── workflows/
        └── deploy.yml   # CI/CD : Tests + Build + Sécurité
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

### Marché général

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/v1/market` | Vue d'ensemble du marché |
| GET | `/api/v1/quotes` | Tous les cours en temps réel |
| GET | `/api/v1/quotes/{ticker}` | Cours d'une action spécifique |

### Indices

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/v1/indices` | Tous les indices (MASI, MADEX...) |
| GET | `/api/v1/indices/{index_name}` | Valeur d'un indice spécifique |

### Sociétés

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/v1/companies` | Liste de toutes les sociétés |
| GET | `/api/v1/companies/{ticker}` | Détails d'une société |

### Statistiques

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/v1/most-active` | Top actions par volume |
| GET | `/api/v1/historical/{ticker}` | Historique OHLCV |

### Système

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/docs` | Swagger UI |

### Exemple de réponse

```json
{
  "ticker": "ATW",
  "name": "Attijariwafa Bank",
  "price": 485.00,
  "change": 2.50,
  "change_pct": 0.52,
  "volume": 125430,
  "open": 482.00,
  "high": 487.00,
  "low": 481.00,
  "timestamp": "2026-02-18T22:00:00"
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
3. Commitez vos changements (`git commit -m 'Add: ma fonctionnalité'`)
4. Pushez vers la branche (`git push origin feature/ma-fonctionnalite`)
5. Ouvrez une Pull Request

---

## Licence

MIT License — Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

> **Note** : Ce projet est destiné à un usage personnel et éducatif. Respectez les conditions d'utilisation du site de la Bourse de Casablanca.
