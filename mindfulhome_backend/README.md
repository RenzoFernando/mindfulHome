# MindfulHome (backend)

FastAPI backend que responde una única pregunta: **¿Puedo comprar esta propiedad sin poner en riesgo mi estabilidad financiera?**

## Stack

| Capa | Tecnología |
|---|---|
| API | FastAPI 0.111 |
| Base de datos | PostgreSQL 16 + SQLAlchemy 2 |
| Migraciones | Alembic |
| Auth | JWT (python-jose + bcrypt) |
| LLM | Groq |
| Contenedores | Docker + docker-compose |
| Tests | pytest + pytest-cov |

---

## Inicio rápido

```bash
# 1. Clonar y entrar al proyecto
cp .env.example .env

# 2. Levantar servicios
docker-compose up --build

# La API queda disponible en http://localhost:8000
```

---

## Estructura del proyecto

```
app/
├── api/
│   ├── endpoints/
│   │   ├── auth.py        # POST /auth/register, POST /auth/login
│   │   ├── users.py       # GET/PATCH /users/me
│   │   └── analyses.py    # CRUD /analyses
│   ├── deps.py
│   └── router.py
├── core/
│   ├── config.py          # Settings via pydantic-settings
│   └── security.py        # Hash y JWT
├── db/base.py             # Engine, SessionLocal y get_db
├── models/
│   ├── user.py            # SQLAlchemy User model
│   └── analysis.py        # SQLAlchemy PropertyAnalysis model
├── schemas/
│   ├── user.py            # Pydantic schemas de usuario
│   └── analysis.py        # Pydantic schemas de análisis
├── services/
│   ├── mortgage.py        # Motor de cálculo hipotecario
│   ├── cashflow.py        # Flujo post-compra
│   ├── ratios.py          # Indicadores clave
│   ├── llm.py             # Integración LLM
│   └── analysis.py        # Orquestador del pipeline
└── main.py
alembic/                   # Migraciones de base de datos
tests/
├── unit/                  # Pruebas del motor matemático y seguridad
└── integration/           # Pruebas de endpoints HTTP
```

---

## Endpoints

### Auth
| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/auth/register` | Registro de usuario |
| POST | `/api/auth/login` | Login → JWT |

### Usuarios
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/users/me` | Perfil del usuario actual |
| PATCH | `/api/users/me` | Actualizar perfil (financiero, laboral, deudas, vivienda, hogar) |

### Análisis
| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/analyses` | Ejecutar análisis completo de una propiedad |
| GET | `/api/analyses` | Listar todos los análisis del usuario |
| GET | `/api/analyses/{id}` | Ver análisis por ID |
| DELETE | `/api/analyses/{id}` | Eliminar análisis |

---

## Pipeline de análisis

```
PropertyInput
     │
     ▼
[1] mortgage.py   →  loan_amount, monthly_payment, total_paid, total_interest
     │
     ▼
[2] cashflow.py   →  liquidity, status (SAFE / MODERATE / RISKY / CRITICAL)
     │
     ▼
[3] ratios.py     →  mortgage_ratio, housing_ratio, emergency_months, FCF ratio…
     │
     ▼
[4] llm.py        →  Análisis en lenguaje natural estructurado (JSON)
     │
     ▼
PropertyAnalysis  →  Guardado en PostgreSQL
```