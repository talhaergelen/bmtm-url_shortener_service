# URL Shortener Service — Mimari Diyagramı

Aşağıdaki Mermaid diyagramını kopyalayarak [Mermaid Live Editor](https://mermaid.live/) üzerinden PNG formatında indirebilir ve `architecture.png` olarak `docs/` klasörüne ekleyebilirsiniz.

```mermaid
flowchart TB
    %% Kullanıcılar
    Client[Kullanıcı / Tarayıcı]
    Admin[Admin / QA]

    %% K8s Cluster Sınırı
    subgraph K8s [Kubernetes Cluster / Minikube]
        direction TB
        
        %% Service
        Service[URL Shortener Service\nNodePort: 30080]
        
        %% Uygulama Podları
        subgraph AppPods [Uygulama Pod'ları (Replica: 2)]
            App1[FastAPI App 1]
            App2[FastAPI App 2]
        end
        
        %% Veritabanı
        DB[(SQLite / PostgreSQL\nurlshortener.db)]
        
        %% Monitoring
        subgraph Monitoring [Gözlemlenebilirlik (Observability)]
            Prometheus[Prometheus\nMetrics Scraper]
            Grafana[Grafana\nDashboard]
        end
        
        %% LocalStack
        LocalStack[LocalStack S3\nSahte AWS]
    end
    
    %% GitHub Actions CI/CD
    subgraph Pipeline [GitHub Actions CI/CD]
        direction LR
        Lint[Lint] --> Test[Pytest]
        Test --> Postman[Newman]
        Postman --> Docker[Docker Build]
        Docker --> Deploy[K8s Deploy]
    end

    %% Bağlantılar
    Client -- "HTTP GET / POST" --> Service
    Service --> App1 & App2
    
    App1 & App2 -- "CRUD İşlemleri" --> DB
    App1 & App2 -- "İstatistik JSON Yükleme" --> LocalStack
    
    Prometheus -- "/metrics endpoint'ini çeker" --> App1 & App2
    Grafana -- "PromQL Sorguları" --> Prometheus
    
    Admin -- "Dashboard Görüntüleme" --> Grafana
    Admin -- "Kodu İter" --> Pipeline
    Pipeline -. "İmajı Günceller" .-> AppPods

    %% Stil
    classDef default fill:#f9f9f9,stroke:#333,stroke-width:2px;
    classDef k8s fill:#e3f2fd,stroke:#2196f3,stroke-width:2px,stroke-dasharray: 5 5;
    classDef pods fill:#e8f5e9,stroke:#4caf50,stroke-width:2px;
    classDef db fill:#ffecb3,stroke:#ffc107,stroke-width:2px;
    classDef ext fill:#f3e5f5,stroke:#9c27b0,stroke-width:2px;
    
    class K8s k8s;
    class App1,App2 pods;
    class DB db;
    class Prometheus,Grafana,LocalStack,Pipeline ext;
```
