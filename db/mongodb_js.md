```javascript
use notification_service;

db.createCollection("global_notifications", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["message_id", "type", "title", "message_summary", "message_detail", "announcement_date"],
      properties: {
        message_id: { bsonType: "string" },
        type: { enum: ["info", "warning", "error", "promotion"] },
        title: { bsonType: "object" },
        message_summary: { bsonType: "object" },
        message_detail: { bsonType: "object" },
        announcement_date: { bsonType: "date" },
        target: { enum: ["all"] },
        created_at: { bsonType: "date" },
        updated_at: { bsonType: "date" }
      }
    }
  }
});

db.createCollection("user_notifications", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["message_id", "user_id", "type", "title", "message_summary", "message_detail"],
      properties: {
        message_id: { bsonType: "string" },
        user_id: { bsonType: "string" },
        type: { enum: ["info", "alert", "progress", "error"] },
        title: { bsonType: "object" },
        message_summary: { bsonType: "object" },
        message_detail: { bsonType: "object" },
        is_important: { bsonType: "bool" },
        delivery_status: { enum: ["delivered", "failed", "pending"] },
        delivered_at: { bsonType: "date" },
        created_at: { bsonType: "date" },
        updated_at: { bsonType: "date" }
      }
    }
  }
});

db.createCollection("user_read_status", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["user_id", "read_message_ids"],
      properties: {
        user_id: { bsonType: "string" },
        read_message_ids: {
          bsonType: "array",
          items: { bsonType: "string" }
        },
        updated_at: { bsonType: "date" }
      }
    }
  }
});
```