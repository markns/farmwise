# FarmWise

### Empowering African Farmers with Smart Agriculture

FarmWise is your personal agronomic advisor and farm management system, accessible right from your phone via WhatsApp. 
Our mission is to increase agricultural productivity, sustainability, and profitability for farmers across Africa by making expert agronomic advice accessible to everyone.

## 🌾 Project Goals

FarmWise combines local agricultural knowledge with modern technology to provide personalized advice and support for farming operations. The platform aims to:

- **Make expert agricultural advice accessible** to all farmers through WhatsApp
- **Increase agricultural productivity** through personalized recommendations  
- **Improve farm sustainability** with climate-smart guidance
- **Enhance profitability** through market insights and optimized practices
- **Bridge the digital divide** by working on basic phones without app downloads

## ✨ Key Features

- **🌱 Crop Recommendations** - Personalized crop selection based on soil, climate, and market conditions
- **🌦️ Weather Forecasts** - Localized weather data for effective farm planning
- **🐛 Pest & Disease Management** - Expert identification and treatment advice with image diagnosis
- **📅 Planting Calendar** - Customized planting schedules for specific crops and regions
- **📊 Farm Analytics** - Performance tracking with detailed insights and reports
- **👥 Community Support** - Connection with other farmers and agricultural experts
- **📱 WhatsApp Integration** - Full platform access via WhatsApp messaging
- **💰 Market Prices** - Real-time commodity pricing and market trends

### Feature Example - Disease and Pest alerts
In this use case example, a farmer spots a crop pest, sends a photo to the FarmWise bot via WhatsApp, and instantly gets a diagnosis and solution. 
Workflows in the FarmWise backend alert neighboring farmers who may be affected by the same pest, helping the entire community protect their crops.

[![Disease and Pest Alerts](https://img.youtube.com/vi/bBo851l6BJw/hqdefault.jpg)](https://www.youtube.com/embed/bBo851l6BJw)

## 📱 Getting Started with WhatsApp

No app downloads or complicated interfaces required! Simply:

1. **Save our number:** +254 708 883040
2. **Send "Hello"** to start
3. **Follow the prompts** to set up your farm profile

[**Start Chatting Now**](https://wa.me/254708883040)

## Platform Architecture

![paas](/docs/FarmWise.png)

## 🏗️ Technical Architecture

### Applications

- **`apps/farmbase/`** - Core FastAPI backend with multi-tenant architecture
- **`apps/farmwise/`** - AI agent service with WhatsApp integration
- **`apps/farmbase-workflows/`** - Temporal workflow engine for background tasks
- **`frontend/`** - React web console for farm management

### Libraries

- **`libs/farmbase-client/`** - Auto-generated API client
- **`libs/isdasoil-api-client/`** - Africa soil data integration

### Data Sources

- **GAEZ** (Global Agro-ecological Zones) climate and suitability data
- **KALRO** (Kenya Agricultural Research Organization) crop varieties
- **KAMIS** (Kenya Agricultural Market Information System) prices
- **ISDA** Africa soil property maps
- **Weather data** integration via Temporal workflows

## 🚀 Quick Start for Developers

### Prerequisites

- Python ≤ 3.13
- Node.js (for frontend)
- PostgreSQL with PostGIS extension
- OpenAI API key

### Setup

1. **Clone and setup environment:**
```bash
git clone <repository-url>
cd farmwise
echo 'OPENAI_API_KEY=your_openai_api_key' >> .env
```

2. **Start database:**
```bash
docker-compose up db
```

3. **Install dependencies:**
```bash
uv sync
```

4. **Run database migrations:**
```bash
cd apps/farmbase
uv run alembic upgrade head
```

5. **Start services:**
```bash
# Backend API
cd apps/farmbase && uv run fastapi dev src/farmbase/main.py

# AI Agent Service  
cd apps/farmwise && uv run python src/farmwise/main.py

# Frontend (in separate terminal)
cd frontend && npm install && npm run dev
```

TODO: Describe WhatsApp business API configuration

## 🛠️ Development

### Code Quality

```bash
# Format code
uv run poe fmt

# Lint with auto-fix
uv run poe lint

# Type checking
uv run poe check

# Run tests
uv run poe test

# Run all checks
uv run poe all
```

### Database Management

```bash
# Create migration after model changes
cd apps/farmbase
uv run alembic revision --autogenerate -m "Description"

# Apply migrations
uv run alembic upgrade head
```

### API Client Generation

```bash
# Generate updated API client
uv run poe client-gen
```

## 🗄️ Database Design

- **PostgreSQL with PostGIS** for spatial data
- **Schema-based multi-tenancy** (`farmbase_organization_{slug}`)
- **Automatic organization routing** via middleware
- **Async SQLAlchemy** with SQLModel

## 📊 Tech Stack

- **Backend:** FastAPI, SQLAlchemy, PostgreSQL, Temporal
- **Frontend:** React, TypeScript, Vite
- **AI:** OpenAI APIs, custom agricultural agents
- **Geospatial:** PostGIS, GeoPandas, rioxarray
- **Communication:** WhatsApp Business API
- **Infrastructure:** Docker, uv for dependency management

## 🤝 Contributing

1. Follow the existing code conventions
2. Use the provided linting and formatting tools
3. Add tests for new functionality
4. Update documentation as needed

## 📄 License

Sustainable use license. Please contact marknuttallsmith@gmail.com for alternative licensing.

---

*© 2025 FarmWise. All rights reserved.*