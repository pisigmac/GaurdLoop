# Architecture

## System Design

```mermaid
graph TB
    subgraph "Client"
        FE[Next.js 14 Dashboard]
    end

    subgraph "API Layer"
        API[FastAPI /async]
        AUTH[Clerk JWT]
    end

    subgraph "Core Services"
        TG[TaskGraph Engine]
        SE[ScoreEngine]
        CS[ContextScrub]
        BV[BrowserVerify]
        LM[LoopMonitor]
    end

    subgraph "Data Layer"
        PG[(Postgres 15)]
        RD[(Redis)]
    end

    subgraph "Agents"
        CUR[Cursor]
        CLA[Claude Code]
        COP[GitHub Copilot]
        CUS[Custom]
    end

    FE -->|REST + SSE| API
    API --> AUTH
    API --> TG
    API --> SE
    API --> CS
    API --> BV
    API --> LM
    TG --> PG
    SE --> PG
    CS --> PG
    BV --> PG
    LM --> RD
    API --> RD
    CUR -->|Webhook| API
    CLA -->|Webhook| API
    COP -->|Webhook| API
    CUS -->|Webhook| API
```

## Data Flow

1. **Webhook arrives** from Cursor/GitHub/Slack
2. **GuardLoop creates a Task** with dependencies
3. **TaskGraph Engine** checks if dependencies are met
4. **Agent adapter** dispatches to the actual agent
5. **LoopMonitor** tracks iterations in real-time
6. **ContextScrub** scans every LLM call for PII
7. **ScoreEngine** calculates confidence when task completes
8. **BrowserVerify** runs if UI was touched
9. **Decision gate** auto-approves, reviews, or blocks
10. **SSE stream** pushes updates to the dashboard

## Scalability

- Backend: Horizontal Pod Autoscaler (3-20 replicas)
- Postgres: Read replicas for score queries
- Redis: Cluster mode for pub/sub at scale
- BrowserVerify: Dedicated node pool with GPU for visual regression
