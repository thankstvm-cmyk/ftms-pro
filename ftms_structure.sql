DROP TABLE IF EXISTS vehicle_models;

CREATE TABLE vehicle_models (
id INTEGER PRIMARY KEY AUTOINCREMENT,
brand_id INTEGER NOT NULL,
model_name TEXT NOT NULL,
created_at TEXT DEFAULT CURRENT_TIMESTAMP,
UNIQUE (brand_id, model_name), FOREIGN KEY (brand_id) REFERENCES vehicle_brands(id)
);