// mongo-init/init-mongo.js
// MongoDB 初期化スクリプト（初回起動時にのみ実行）
// コレクションのスキーマバリデーション定義

const dbName = process.env.MONGO_INITDB_DATABASE || 'notification_service';

db = db.getSiblingDB(dbName);

// user_notifications コレクション作成（バリデーション付き）
db.createCollection("user_notifications", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["user_id", "message_id", "type", "title", "message", "date"],
      properties: {
        user_id: {
          bsonType: "string",
          description: "必須。ユーザーID（文字列）"
        },
        message_id: {
          bsonType: "string",
          description: "必須。メッセージID（UUID文字列）"
        },
        type: {
          bsonType: "string",
          enum: ["info", "warning", "error", "promotion", "alert", "progress"],
          description: "通知タイプ。指定されたenumのいずれか"
        },
        title: {
          bsonType: "string",
          description: "通知タイトル"
        },
        message: {
          bsonType: "string",
          description: "通知本文"
        },
        date: {
          bsonType: "date",
          description: "通知発行日"
        }
      }
    }
  }
});

// index作成（高速検索用）
db.user_notifications.createIndex({ user_id: 1, date: -1 });
