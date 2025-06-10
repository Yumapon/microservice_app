# DB設計

整備中

## 利用するDBMS

- PostgreSQL：構造化されたデータ（ユーザー・見積・申込など）
- MongoDB　：柔軟な構造を持つデータ（保険商品詳細、見積もり履歴など）

##  PostgreSQL：DDL（テーブル定義）

### users テーブル

```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  name VARCHAR(100) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### plans テーブル

```sql
CREATE TABLE plans (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  monthly_premium INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### quotes テーブル

```sql
CREATE TABLE quotes (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  plan_id INTEGER REFERENCES plans(id),
  age INTEGER NOT NULL,
  coverage INTEGER NOT NULL,
  estimated_premium INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### applications テーブル

```sql
CREATE TABLE applications (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  quote_id INTEGER REFERENCES quotes(id),
  agreement BOOLEAN NOT NULL,
  status VARCHAR(50) DEFAULT 'pending',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## MongoDB：ドキュメントスキーマと初期データ例

### スキーマ定義

```js
{
  product_id: Number,              // RDB上の保険商品IDに対応
  faq: [
    {
      question: String,
      answer: String
    }
  ],
  coverage_items: [
    {
      label: String,               // 補償名（例：死亡保険金）
      amount: String               // 金額など（例：1000万円）
    }
  ]
}
```

### user_activity_logs スキーマ定義（ユーザー操作ログ）

```js
{
  user_id: Number,
  action: String,                  // 操作内容（例："viewed_product"）
  product_id: Number,              // 対象保険商品ID（該当すれば）
  timestamp: ISODate               // 操作日時（UTC推奨）
}
```

### system_messages スキーマ定義（アプリメッセージ）

```js
{
  key: String,                     // メッセージ識別子（例："quote_success"）
  message: String                  // 表示内容
}
```

### plan_details コレクション（保険商品の詳細）

```json
{
  "plan_id": 1,
  "coverage_items": [
    { "type": "death", "amount": 1000000, "description": "死亡保険金" },
    { "type": "hospital", "amount": 5000, "description": "入院日額" }
  ],
  "conditions": {
    "age_limit": 60,
    "exclusions": ["持病", "海外渡航中"]
  }
}
```

### quote_logs コレクション（見積もり履歴）

```json
{
  "quote_id": 123,
  "input": {
    "age": 30,
    "coverage": 1000000
  },
  "calculation_steps": [
    "base: 5000",
    "age_factor: +300",
    "coverage_factor: +700"
  ],
  "result": 6000,
  "timestamp": "2025-05-26T10:30:00Z"
}
```

## mongodb初期データ

### product_details（保険商品に紐づく柔軟な詳細情報）

```json
[
  {
    "product_id": 1,
    "faq": [
      { "question": "いつから補償されますか？", "answer": "契約翌日からです。" },
      { "question": "途中解約できますか？", "answer": "はい、できますが返金条件があります。" }
    ],
    "coverage_items": [
      { "label": "死亡保険金", "amount": "1000万円" },
      { "label": "入院保険金", "amount": "日額5,000円" }
    ]
  },
  {
    "product_id": 2,
    "faq": [],
    "coverage_items": []
  }
]
```

### user_activity_logs（ユーザーの行動履歴ログ）

```json
[
  {
    "user_id": 101,
    "action": "viewed_product",
    "product_id": 1,
    "timestamp": "2025-05-26T10:05:00Z"
  },
  {
    "user_id": 101,
    "action": "started_application",
    "product_id": 1,
    "timestamp": "2025-05-26T10:06:00Z"
  }
]
```

### system_messages（ユーザーに表示されるアプリメッセージ）

```json
[
  {
    "key": "quote_success",
    "message": "見積もりが正常に作成されました。"
  },
  {
    "key": "application_submitted",
    "message": "申込が完了しました。審査結果をお待ちください。"
  }
]
```

## mongoimport 用テンプレートコマンド(MongoDBサーバへJSONファイルをインポートする際に使うコマンド)

```bash
mongoimport --db insurance_app --collection product_details --file ./product_details.json --jsonArray
```

```bash
mongoimport --db insurance_app --collection user_activity_logs --file ./user_activity_logs.json --jsonArray
```

```bash
mongoimport --db insurance_app --collection system_messages --file ./system_messages.json --jsonArray
```