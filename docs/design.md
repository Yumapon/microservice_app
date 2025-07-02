## サービス一覧と連携方式
| サービス名                   | 主な責務            | 主DB                                       | 外部連携方式              |
| ----------------------- | --------------- | ----------------------------------------- | ------------------- |
| `bff_service`           | api統合、認証・認可（Keycloak）    | Keycloak          | REST (各サービスと連携)、OpenID Connect     |
| `auth_service`          | 認証・認可（Keycloak） | Keycloak                                  | OpenID Connect      |
| `quotation_service`     | 保険見積もり作成・更新     | PostgreSQL（quotes 等）、MongoDB（scenarios 等） | REST + NATS（サブスク）   |
| `application_service`   | 申込処理管理          | PostgreSQL、MongoDB                        | REST + NATS（パブリッシュ） |
| `contract_service`      | 契約管理            | PostgreSQL、MongoDB                        | REST + NATS（パブリッシュ） |
| `rate_service`          | 利率データ取得         | MongoDB（interest\_rates）                  | REST                |
| `public_plan_service`  | 商品マスタ情報の取得      | MongoDB（insurance\_products）              | REST                |
| `event_log_service` | イベント監査ログ        | MongoDB or S3                             | バッチ         |

## 構成図

```mermaid
flowchart TD
  %% ===== クライアント層 =====
  UI[Web / Mobile] --> BFF[BFF Service]

  %% ===== BFF連携先 =====
  BFF --> QS[quotation_service]
  BFF --> AS[application_service]
  BFF --> CS[contract_service]
  BFF --> PPS[public_plan_service]

  %% ===== quotation_service内部構成 =====
  QS --> PSQL_Q[PostgreSQL: quotes, quote_details]
  QS --> MDB_QS[MongoDB: quote_scenarios, quote_status_history]
  QS --> RS[rate_service]
  QS --> PPS

  %% ===== application_service内部構成 =====
  AS --> PSQL_A[PostgreSQL: applications, application_snapshots]
  AS --> MDB_A[MongoDB: application_status_history]
  AS --> RS
  AS --> PPS

  %% ===== contract_service内部構成 =====
  CS --> PSQL_C[PostgreSQL: contracts, contract_snapshots]
  CS --> MDB_C[MongoDB: contract_status_history]

  %% ===== rate_service構成 =====
  RS --> MDB_R[MongoDB: interest_rates]

  %% ===== public_plan_service構成 =====
  PPS --> MDB_P[MongoDB: insurance_products]

  %% ===== NATS通信（非同期） =====
  AS -- ApplicationConfirmed --> QS
  CS -- ContractCreated --> AS
  CS -- ContractCreated --> QS
  AS -- ApplicationCancelled --> QS

  %% ===== スタイル定義 =====
  classDef svc fill:#e6e6fa,stroke:#444,stroke-width:1px,color:#000;
  classDef db_postgres fill:#ddeeff,stroke:#444,color:#000;
  classDef db_mongo fill:#ddefdd,stroke:#444,color:#000;
  classDef natslink stroke:#666,stroke-dasharray: 5 5;

  class QS,AS,CS,RS,PPS svc
  class PSQL_Q,PSQL_A,PSQL_C db_postgres
  class MDB_QS,MDB_A,MDB_C,MDB_R,MDB_P db_mongo
  linkStyle 14,15,16,17 stroke:#666,stroke-dasharray:5,5;
```