-- =============================================================================
-- Talk2Book — PostgreSQL Complete Database Setup (Single File)
-- =============================================================================
-- Đây là file duy nhất để khởi tạo toàn bộ cơ sở dữ liệu từ đầu.
-- Không cần chạy migration riêng. Tất cả thay đổi đã được tích hợp vào đây.
--
-- HƯỚNG DẪN CHẠY TRÊN MÁY MỚI:
--   Bước 1 — Tạo database (chỉ chạy 1 lần, dùng account superuser):
--             createdb -U postgres talk2book
--        hoặc: psql -U postgres -c "CREATE DATABASE talk2book;"
--
--   Bước 2 — Chạy script này vào database vừa tạo:
--             psql -U postgres -d talk2book -f create_database.sql
--
--   Hoặc gộp 2 bước:
--             psql -U postgres -c "CREATE DATABASE talk2book;" && \
--             psql -U postgres -d talk2book -f create_database.sql
-- =============================================================================

-- ================
-- 0. Extensions
-- ================
CREATE EXTENSION IF NOT EXISTS citext;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ================
-- 0b. Utility Functions
-- ================
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ================
-- 0c. ENUM Types
-- ================
DO $$ BEGIN
  CREATE TYPE user_status        AS ENUM ('active','suspended','deleted');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE provider_type      AS ENUM ('airline','hotel','tour');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE booking_state      AS ENUM ('draft','pending_payment','confirmed','cancelled','refunded');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE payment_status     AS ENUM ('pending','authorized','captured','failed','refunded');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE discount_type      AS ENUM ('percent','amount');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE cabin_type         AS ENUM ('economy','premium','business','first');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE review_target_type AS ENUM ('hotel','product','flight','airport');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE gender_type AS ENUM ('M','F','O');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE product_type AS ENUM ('tour','activity','transport');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE ticket_type AS ENUM ('flight','hotel','tour');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- =========================================================
-- 1) Geography & Currency
-- =========================================================
CREATE TABLE IF NOT EXISTS currency (
  code CHAR(3) PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS country (
  code          CHAR(2) PRIMARY KEY,
  name          TEXT NOT NULL,
  currency_code CHAR(3) NOT NULL REFERENCES currency(code) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS city (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  country_code CHAR(2) NOT NULL REFERENCES country(code) ON DELETE RESTRICT,
  name         TEXT NOT NULL,
  CONSTRAINT uq_city_country_name UNIQUE (country_code, name)
);

CREATE TABLE IF NOT EXISTS airport (
  iata     CHAR(3) PRIMARY KEY,
  icao     CHAR(4) UNIQUE,
  city_id  UUID NOT NULL REFERENCES city(id) ON DELETE RESTRICT,
  name     TEXT NOT NULL,
  timezone TEXT NOT NULL,
  CONSTRAINT uq_airport_city_name UNIQUE (city_id, name)
);

-- =========================================================
-- 1b) Category (lookup / taxonomy)
-- =========================================================
CREATE TABLE IF NOT EXISTS category (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  group_name   TEXT NOT NULL,
  value        TEXT NOT NULL,
  description  TEXT,
  sort_order   INT NOT NULL DEFAULT 0,
  is_active    BOOLEAN NOT NULL DEFAULT TRUE,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_category_group_value UNIQUE (group_name, value)
);
CREATE INDEX IF NOT EXISTS idx_category_group_name ON category (group_name);
DROP TRIGGER IF EXISTS trg_category_updated_at ON category;
CREATE TRIGGER trg_category_updated_at
BEFORE UPDATE ON category
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- =========================================================
-- 2) User, Profile & Role  (Better Auth schema)
-- =========================================================
-- "user" is a reserved keyword in Postgres, so we must quote it.
-- id is TEXT (string) as required by Better Auth.
CREATE TABLE IF NOT EXISTS "user" (
  id             TEXT PRIMARY KEY,
  name           TEXT NOT NULL,
  email          CITEXT UNIQUE NOT NULL,
  email_verified BOOLEAN NOT NULL DEFAULT FALSE,
  image          TEXT,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Better Auth: session tokens
CREATE TABLE IF NOT EXISTS session (
  id         TEXT PRIMARY KEY,
  expires_at TIMESTAMPTZ NOT NULL,
  token      TEXT NOT NULL UNIQUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  ip_address TEXT,
  user_agent TEXT,
  user_id    TEXT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS session_userId_idx ON session (user_id);

-- Better Auth: linked OAuth / credential accounts
CREATE TABLE IF NOT EXISTS account (
  id                        TEXT PRIMARY KEY,
  account_id                TEXT NOT NULL,
  provider_id               TEXT NOT NULL,
  user_id                   TEXT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
  access_token              TEXT,
  refresh_token             TEXT,
  id_token                  TEXT,
  access_token_expires_at   TIMESTAMPTZ,
  refresh_token_expires_at  TIMESTAMPTZ,
  scope                     TEXT,
  password                  TEXT,
  created_at                TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at                TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS account_userId_idx ON account (user_id);

-- Better Auth: email / phone verification tokens
CREATE TABLE IF NOT EXISTS verification (
  id         TEXT PRIMARY KEY,
  identifier TEXT NOT NULL,
  value      TEXT NOT NULL,
  expires_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS verification_identifier_idx ON verification (identifier);

-- Domain profile (separate from auth identity)
-- NOTE: SQLModel auto-names this table 'userprofile' (no __tablename__ defined in model)
CREATE TABLE IF NOT EXISTS userprofile (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     TEXT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
  gender      gender_type,
  birthday    DATE,
  nationality CHAR(2) REFERENCES country(code) ON DELETE RESTRICT,
  address     TEXT,
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
DROP TRIGGER IF EXISTS trg_user_profile_updated_at ON userprofile;
CREATE TRIGGER trg_user_profile_updated_at
BEFORE UPDATE ON userprofile
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- "role" is also a reserved keyword
CREATE TABLE IF NOT EXISTS "role" (
  id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code TEXT UNIQUE NOT NULL
);

-- user_id is TEXT to match "user".id
CREATE TABLE IF NOT EXISTS user_role (
  user_id TEXT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
  role_id UUID NOT NULL REFERENCES "role"(id) ON DELETE CASCADE,
  PRIMARY KEY (user_id, role_id)
);

-- =========================================================
-- 3) Provider
-- =========================================================
CREATE TABLE IF NOT EXISTS provider (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  type         provider_type NOT NULL,
  legal_name   TEXT NOT NULL,
  display_name TEXT NOT NULL,
  country_code CHAR(2) REFERENCES country(code) ON DELETE RESTRICT,
  status       user_status NOT NULL DEFAULT 'active',
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
DROP TRIGGER IF EXISTS trg_provider_updated_at ON provider;
CREATE TRIGGER trg_provider_updated_at
BEFORE UPDATE ON provider
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- =========================================================
-- 4) Flight Inventory
-- =========================================================
CREATE TABLE IF NOT EXISTS route (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  origin      CHAR(3) NOT NULL REFERENCES airport(iata) ON DELETE RESTRICT,
  destination CHAR(3) NOT NULL REFERENCES airport(iata) ON DELETE RESTRICT,
  distance_km INT,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT chk_route_origin_dest CHECK (origin != destination),
  CONSTRAINT chk_route_distance CHECK (distance_km IS NULL OR distance_km > 0),
  CONSTRAINT uq_route_od UNIQUE (origin, destination)
);
DROP TRIGGER IF EXISTS trg_route_updated_at ON route;
CREATE TRIGGER trg_route_updated_at
BEFORE UPDATE ON route
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE IF NOT EXISTS flight_schedule (
  id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  provider_id        UUID NOT NULL REFERENCES provider(id) ON DELETE RESTRICT,
  route_id           UUID NOT NULL REFERENCES route(id) ON DELETE CASCADE,
  flight_number      TEXT NOT NULL,
  dow                VARCHAR(7) NOT NULL,   -- bitstring 7 ký tự, e.g. '1000000'
  dep_time           TIME NOT NULL,
  arr_time           TIME NOT NULL,
  arrival_day_offset SMALLINT NOT NULL DEFAULT 0,
  amenities          JSONB,
  created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT chk_fs_dow_bits CHECK (
    char_length(dow) = 7 AND dow ~ '^[01]+$' AND dow <> '0000000'
  ),
  CONSTRAINT uq_fs_provider_route_flt_dow_time UNIQUE (provider_id, route_id, flight_number, dow, dep_time)
);
DROP TRIGGER IF EXISTS trg_flight_schedule_updated_at ON flight_schedule;
CREATE TRIGGER trg_flight_schedule_updated_at
BEFORE UPDATE ON flight_schedule
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE IF NOT EXISTS flight_instance (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  schedule_id     UUID NOT NULL REFERENCES flight_schedule(id) ON DELETE CASCADE,
  flight_date     DATE NOT NULL,
  dep_datetime    TIMESTAMPTZ NOT NULL,
  arr_datetime    TIMESTAMPTZ NOT NULL,
  aircraft_code   TEXT,
  status          VARCHAR(20) NOT NULL DEFAULT 'scheduled',
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_fi_schedule_date UNIQUE (schedule_id, flight_date),
  CONSTRAINT chk_fi_time CHECK (dep_datetime < arr_datetime)
);
CREATE INDEX IF NOT EXISTS idx_flight_instance_date ON flight_instance (flight_date);
DROP TRIGGER IF EXISTS trg_flight_instance_updated_at ON flight_instance;
CREATE TRIGGER trg_flight_instance_updated_at
BEFORE UPDATE ON flight_instance
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE IF NOT EXISTS seat_inventory (
  instance_id   UUID          NOT NULL REFERENCES flight_instance(id) ON DELETE CASCADE,
  cabin         cabin_type    NOT NULL,
  total_seats   INT           NOT NULL,
  held_seats    INT           NOT NULL DEFAULT 0,
  sold_seats    INT           NOT NULL DEFAULT 0,
  price         NUMERIC(12,2) NOT NULL DEFAULT 0,
  currency_code CHAR(3)       NOT NULL DEFAULT 'VND' REFERENCES currency(code) ON DELETE RESTRICT,
  amenities     JSONB         NOT NULL DEFAULT '{}'::jsonb,
  CONSTRAINT chk_si_seats CHECK (held_seats + sold_seats <= total_seats),
  CONSTRAINT chk_si_price CHECK (price >= 0),
  PRIMARY KEY (instance_id, cabin)
);
CREATE INDEX IF NOT EXISTS idx_si_instance ON seat_inventory(instance_id, cabin);

-- =========================================================
-- 5) Hotel Inventory
-- =========================================================
CREATE TABLE IF NOT EXISTS hotel (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  provider_id   UUID NOT NULL REFERENCES provider(id) ON DELETE RESTRICT,
  city_id       UUID NOT NULL REFERENCES city(id) ON DELETE RESTRICT,
  name          TEXT NOT NULL,
  star_rating   NUMERIC(2,1),
  address       TEXT,
  lat           NUMERIC(9,6),
  lng           NUMERIC(9,6),
  description   TEXT,
  images        JSONB,
  amenities     JSONB,
  usp           TEXT,
  room_count    INT,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_hotel_city_star ON hotel(city_id, star_rating);
DROP TRIGGER IF EXISTS trg_hotel_updated_at ON hotel;
CREATE TRIGGER trg_hotel_updated_at
BEFORE UPDATE ON hotel
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE IF NOT EXISTS hotel_room (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  hotel_id              UUID NOT NULL REFERENCES hotel(id) ON DELETE CASCADE,
  code                  TEXT,
  capacity              INT NOT NULL,
  bed_config            TEXT,
  room_type             TEXT,
  area_sqm              DOUBLE PRECISION,
  view_type             TEXT,
  amenities             JSONB,
  service_package       TEXT,
  cancellation_policy   TEXT,
  description           TEXT,
  images                JSONB,
  CONSTRAINT uq_room_hotel_code UNIQUE (hotel_id, code),
  CONSTRAINT chk_room_capacity CHECK (capacity > 0)
);
CREATE INDEX IF NOT EXISTS idx_hotel_room_hotel ON hotel_room(hotel_id);

CREATE TABLE IF NOT EXISTS room_rate_plan (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  hotel_id            UUID NOT NULL REFERENCES hotel(id) ON DELETE CASCADE,
  name                TEXT NOT NULL,
  meal_plan           VARCHAR(20),
  cancellation_policy JSONB,
  currency_code       CHAR(3) NOT NULL REFERENCES currency(code) ON DELETE RESTRICT,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_rrp_hotel_name UNIQUE (hotel_id, name)
);
DROP TRIGGER IF EXISTS trg_room_rate_plan_updated_at ON room_rate_plan;
CREATE TRIGGER trg_room_rate_plan_updated_at
BEFORE UPDATE ON room_rate_plan
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- Composite PK: (room_id, rate_plan_id, stay_date) — bảng không có surrogate key
CREATE TABLE IF NOT EXISTS room_inventory_daily (
  room_id      UUID NOT NULL REFERENCES hotel_room(id) ON DELETE CASCADE,
  rate_plan_id UUID NOT NULL REFERENCES room_rate_plan(id) ON DELETE CASCADE,
  stay_date    DATE NOT NULL,
  allotment    INT  NOT NULL,
  sold         INT  NOT NULL DEFAULT 0,
  stop_sell    BOOLEAN NOT NULL DEFAULT FALSE,
  base_price   NUMERIC(12,2) NOT NULL,
  CONSTRAINT uq_room_rate_date UNIQUE (room_id, rate_plan_id, stay_date),
  CONSTRAINT chk_rid_sold_allotment CHECK (sold <= allotment),
  CONSTRAINT chk_rid_allotment_positive CHECK (allotment > 0),
  CONSTRAINT chk_rid_price_positive CHECK (base_price >= 0),
  PRIMARY KEY (room_id, rate_plan_id, stay_date)
);
CREATE INDEX IF NOT EXISTS idx_room_inv_date ON room_inventory_daily (stay_date);
CREATE INDEX IF NOT EXISTS idx_room_inv_room_date ON room_inventory_daily (room_id, stay_date);

-- =========================================================
-- 6) Tour / Activity / Transport (time-slotted inventory)
-- =========================================================
CREATE TABLE IF NOT EXISTS product (
  id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  provider_id        UUID NOT NULL REFERENCES provider(id) ON DELETE RESTRICT,
  type               product_type NOT NULL,
  title              TEXT NOT NULL,
  description        TEXT,
  itinerary          JSONB,
  images             JSONB,
  duration_days      INT,
  created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_product_provider_type ON product(provider_id, type);
DROP TRIGGER IF EXISTS trg_product_updated_at ON product;
CREATE TRIGGER trg_product_updated_at
BEFORE UPDATE ON product
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE IF NOT EXISTS time_slot (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id     UUID NOT NULL REFERENCES product(id) ON DELETE CASCADE,
  start_datetime TIMESTAMPTZ NOT NULL,
  end_datetime   TIMESTAMPTZ NOT NULL,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT chk_slot_dates CHECK (start_datetime < end_datetime),
  CONSTRAINT uq_slot_unique UNIQUE (product_id, start_datetime, end_datetime)
);
CREATE INDEX IF NOT EXISTS idx_slot_product_start ON time_slot(product_id, start_datetime);
DROP TRIGGER IF EXISTS trg_time_slot_updated_at ON time_slot;
CREATE TRIGGER trg_time_slot_updated_at
BEFORE UPDATE ON time_slot
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- slot_id là PK (1 suất = 1 dòng tồn kho)
CREATE TABLE IF NOT EXISTS slot_inventory (
  slot_id       UUID PRIMARY KEY REFERENCES time_slot(id) ON DELETE CASCADE,
  capacity      INT NOT NULL,
  sold          INT NOT NULL DEFAULT 0,
  price         NUMERIC(12,2) NOT NULL DEFAULT 0,
  currency_code CHAR(3) NOT NULL REFERENCES currency(code) ON DELETE RESTRICT,
  CONSTRAINT chk_inventory_sold_capacity CHECK (sold <= capacity),
  CONSTRAINT chk_inventory_capacity_positive CHECK (capacity > 0),
  CONSTRAINT chk_inventory_price_positive CHECK (price >= 0)
);

-- =========================================================
-- 7) Price Quote
-- =========================================================
-- user_id là TEXT để khớp "user".id (Better Auth)
CREATE TABLE IF NOT EXISTS price_quote (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       TEXT REFERENCES "user"(id) ON DELETE SET NULL,
  vertical      VARCHAR(20) NOT NULL,
  payload       JSONB NOT NULL,
  currency_code CHAR(3) NOT NULL REFERENCES currency(code) ON DELETE RESTRICT,
  total_amount  NUMERIC(12,2) NOT NULL,
  expires_at    TIMESTAMPTZ NOT NULL,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT check_price_quotes_amount_positive CHECK (total_amount >= 0),
  CONSTRAINT check_price_quotes_expiry CHECK (expires_at > (now() - interval '1 minute'))
);
CREATE INDEX IF NOT EXISTS idx_price_quotes_expiry ON price_quote (expires_at);

-- =========================================================
-- 8) Promotion & Coupon
-- =========================================================
CREATE TABLE IF NOT EXISTS coupon (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code                TEXT UNIQUE NOT NULL,

  discount_type       discount_type NOT NULL,
  discount_value      NUMERIC(12,2) NOT NULL,
  currency_code       CHAR(3) REFERENCES currency(code) ON DELETE RESTRICT,

  min_order_amount    NUMERIC(12,2),
  max_discount_amount NUMERIC(12,2),

  max_uses_total      INT,
  max_uses_per_user   INT,
  current_uses        INT NOT NULL DEFAULT 0,

  starts_at           TIMESTAMPTZ,
  ends_at             TIMESTAMPTZ,
  is_active           BOOLEAN NOT NULL DEFAULT TRUE,

  created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),

  CONSTRAINT chk_coupon_window CHECK (starts_at IS NULL OR ends_at IS NULL OR starts_at < ends_at),
  CONSTRAINT chk_coupon_usage_limit CHECK (current_uses >= 0 AND (max_uses_total IS NULL OR current_uses <= max_uses_total)),
  CONSTRAINT chk_coupon_logic CHECK (
    (discount_type = 'percent' AND discount_value >= 0 AND discount_value <= 100)
    OR
    (discount_type = 'amount'  AND discount_value >= 0 AND currency_code IS NOT NULL)
  )
);
DROP TRIGGER IF EXISTS trg_coupon_updated_at ON coupon;
CREATE TRIGGER trg_coupon_updated_at
BEFORE UPDATE ON coupon
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- =========================================================
-- 9) Booking & Transaction
-- =========================================================
-- user_id là TEXT để khớp "user".id (Better Auth)
CREATE TABLE IF NOT EXISTS booking (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       TEXT REFERENCES "user"(id) ON DELETE SET NULL,
  state         booking_state NOT NULL,
  currency_code CHAR(3) NOT NULL REFERENCES currency(code) ON DELETE RESTRICT,
  total_amount  NUMERIC(12,2) NOT NULL,
  quote_id      UUID REFERENCES price_quote(id) ON DELETE SET NULL,
  coupon_id     UUID REFERENCES coupon(id) ON DELETE SET NULL,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT chk_booking_total_amount CHECK (total_amount >= 0)
);
DROP TRIGGER IF EXISTS trg_booking_updated_at ON booking;
CREATE TRIGGER trg_booking_updated_at
BEFORE UPDATE ON booking
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- actor_id là TEXT để khớp "user".id (Better Auth)
CREATE TABLE IF NOT EXISTS booking_audit_log (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  booking_id  UUID NOT NULL REFERENCES booking(id) ON DELETE CASCADE,
  actor_type  TEXT,
  actor_id    TEXT REFERENCES "user"(id) ON DELETE SET NULL,
  action      TEXT NOT NULL,
  from_state  TEXT,
  to_state    TEXT,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  meta        JSONB
);
CREATE INDEX IF NOT EXISTS idx_booking_audit_log_booking ON booking_audit_log (booking_id);
CREATE INDEX IF NOT EXISTS idx_booking_audit_log_actor ON booking_audit_log (actor_id);

-- user_id là TEXT để khớp "user".id (Better Auth)
CREATE TABLE IF NOT EXISTS coupon_redemption (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  coupon_id       UUID NOT NULL REFERENCES coupon(id) ON DELETE RESTRICT,
  user_id         TEXT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
  booking_id      UUID NOT NULL REFERENCES booking(id) ON DELETE CASCADE,

  discount_amount NUMERIC(12,2) NOT NULL,
  currency_code   CHAR(3) NOT NULL REFERENCES currency(code) ON DELETE RESTRICT,

  redeemed_at     TIMESTAMPTZ NOT NULL DEFAULT now(),

  CONSTRAINT uq_redemption_booking UNIQUE (booking_id, coupon_id),
  CONSTRAINT chk_redemption_amount CHECK (discount_amount > 0)
);
CREATE INDEX IF NOT EXISTS idx_redemption_user_coupon ON coupon_redemption(user_id, coupon_id);
CREATE INDEX IF NOT EXISTS idx_redemption_coupon ON coupon_redemption(coupon_id);

-- Trigger tự động cập nhật current_uses trên coupon
CREATE OR REPLACE FUNCTION update_coupon_usage_count()
RETURNS TRIGGER AS $$
BEGIN
  IF (TG_OP = 'INSERT') THEN
    UPDATE coupon
    SET current_uses = current_uses + 1
    WHERE id = NEW.coupon_id;
  ELSIF (TG_OP = 'DELETE') THEN
    UPDATE coupon
    SET current_uses = current_uses - 1
    WHERE id = OLD.coupon_id;
  END IF;
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_auto_update_coupon_uses ON coupon_redemption;
CREATE TRIGGER trg_auto_update_coupon_uses
AFTER INSERT OR DELETE ON coupon_redemption
FOR EACH ROW EXECUTE FUNCTION update_coupon_usage_count();

CREATE TABLE IF NOT EXISTS booking_item (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  booking_id   UUID NOT NULL REFERENCES booking(id) ON DELETE CASCADE,
  vertical     VARCHAR(20) NOT NULL,
  supplier_ref TEXT,
  details      JSONB NOT NULL,
  price_amount NUMERIC(12,2) NOT NULL,
  CONSTRAINT chk_item_price_amount CHECK (price_amount >= 0)
);
CREATE INDEX IF NOT EXISTS idx_booking_item_booking ON booking_item(booking_id);

CREATE TABLE IF NOT EXISTS passenger (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  booking_id  UUID NOT NULL REFERENCES booking(id) ON DELETE CASCADE,
  full_name   TEXT NOT NULL,
  nationality CHAR(2) REFERENCES country(code) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS ticket (
  id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  item_id   UUID NOT NULL REFERENCES booking_item(id) ON DELETE CASCADE,
  type      ticket_type NOT NULL,
  code      TEXT NOT NULL UNIQUE,
  issued_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =========================================================
-- 10) Payment
-- =========================================================
CREATE TABLE IF NOT EXISTS payment (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  booking_id      UUID NOT NULL REFERENCES booking(id) ON DELETE CASCADE,
  provider        TEXT NOT NULL,
  amount          NUMERIC(12,2) NOT NULL,
  currency_code   CHAR(3) NOT NULL REFERENCES currency(code) ON DELETE RESTRICT,
  status          payment_status NOT NULL,
  idempotency_key TEXT UNIQUE,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT chk_payment_amount CHECK (amount > 0)
);
CREATE INDEX IF NOT EXISTS idx_payment_booking_created ON payment(booking_id, created_at);

-- =========================================================
-- 11) Review
-- =========================================================
-- user_id là TEXT để khớp "user".id (Better Auth)
CREATE TABLE IF NOT EXISTS review (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     TEXT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
  target_type review_target_type NOT NULL,
  target_key  TEXT NOT NULL,
  rating      INT NOT NULL,
  comment     TEXT,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT chk_review_rating CHECK (rating >= 1 AND rating <= 5),
  CONSTRAINT uq_review_once UNIQUE (user_id, target_type, target_key)
);
CREATE INDEX IF NOT EXISTS idx_review_target ON review (target_type, target_key);

-- =========================================================
-- 12) Additional Performance Indexes
-- =========================================================
CREATE INDEX IF NOT EXISTS idx_city_country ON city(country_code);
CREATE INDEX IF NOT EXISTS idx_airport_city ON airport(city_id);
CREATE INDEX IF NOT EXISTS idx_route_updated ON route(updated_at);
CREATE INDEX IF NOT EXISTS idx_fs_route_dow ON flight_schedule(route_id, dow, dep_time);
CREATE INDEX IF NOT EXISTS idx_fi_sched_status ON flight_instance(schedule_id, flight_date, status);
CREATE INDEX IF NOT EXISTS idx_hotel_updated ON hotel(updated_at);
CREATE INDEX IF NOT EXISTS idx_product_updated ON product(updated_at);
CREATE INDEX IF NOT EXISTS idx_booking_user_created ON booking(user_id, created_at);

-- =========================================================
-- 13) Seed Minimal Data
-- =========================================================
INSERT INTO currency(code, name) VALUES
  ('USD','US Dollar'),
  ('EUR','Euro'),
  ('VND','Vietnamese Dong')
ON CONFLICT (code) DO NOTHING;
