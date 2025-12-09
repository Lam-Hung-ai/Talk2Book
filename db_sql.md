```sql
-- =========================================================
-- Travel Super-App (PostgreSQL) – Full DDL
-- Safe to run on a fresh DB. Requires: PG >= 13
-- =========================================================
-- CREATE DATABASE travel_app;
-- \c travel_app

-- ================
-- Extensions
-- ================
CREATE EXTENSION IF NOT EXISTS citext;
CREATE EXTENSION IF NOT EXISTS pgcrypto;     -- gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS btree_gist;   -- exclusion constraints

-- ================
-- Utility functions
-- ================
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ================
-- ENUM Types
-- ================
DO $$ BEGIN
  CREATE TYPE user_status        AS ENUM ('active','suspended','deleted');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE provider_type      AS ENUM ('airline','hotel','operator','transport');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE booking_state      AS ENUM ('draft','pending_payment','confirmed','cancelled','refunded');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE payment_status     AS ENUM ('pending','authorized','captured','failed','refunded');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE refund_status      AS ENUM ('pending','approved','processed','failed');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE discount_type      AS ENUM ('percent','amount');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE cabin_type         AS ENUM ('economy','premium','business','first');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE fare_bucket_type   AS ENUM ('Y','B','M','H','Q','K','L','T','N','S','V','R','D','C','J','F','P','Z','U','E');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE support_status     AS ENUM ('open','pending','resolved','closed');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE review_target_type AS ENUM ('hotel','product','flight','airport');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE gender_type AS ENUM ('M','F','O');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE product_type AS ENUM ('activity','transport');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE ticket_type AS ENUM ('flight','hotel','activity','transport');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- =========================================================
-- 1) Geo / Currency
-- =========================================================
CREATE TABLE IF NOT EXISTS currencies (
  code CHAR(3) PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS countries (
  code  CHAR(2) PRIMARY KEY,
  name          TEXT NOT NULL,
  currency_code CHAR(3) NOT NULL REFERENCES currencies(code) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS cities (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  country_code CHAR(2) NOT NULL REFERENCES countries(country_code) ON DELETE RESTRICT,
  name         TEXT NOT NULL,
  CONSTRAINT uq_cities_country_name UNIQUE (country_code, name)
);

CREATE TABLE IF NOT EXISTS airports (
  iata     CHAR(3) PRIMARY KEY,
  icao     CHAR(4),
  city_id  UUID NOT NULL REFERENCES cities(id) ON DELETE RESTRICT,
  name     TEXT NOT NULL,
  timezone TEXT NOT NULL,
  CONSTRAINT uq_airports_icao UNIQUE (icao),
  CONSTRAINT uq_airports_city_name UNIQUE (city_id, name)
);

-- =========================================================
-- 2) Users & Profiles & Roles
-- =========================================================
CREATE TABLE IF NOT EXISTS users (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email         CITEXT UNIQUE NOT NULL,
  phone         VARCHAR(32) UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  status        user_status NOT NULL DEFAULT 'active',
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS user_profiles (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id      UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
  full_name    TEXT NOT NULL,
  gender       gender_type,
  bithday          DATE,
  nationality  CHAR(2) REFERENCES countries(country_code) ON DELETE RESTRICT,
  avatar_url   TEXT,
  address      TEXT,
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE OR REPLACE FUNCTION set_user_profile_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_user_profiles_updated_at ON user_profiles;
CREATE TRIGGER trg_user_profiles_updated_at
BEFORE UPDATE ON user_profiles
FOR EACH ROW EXECUTE FUNCTION set_user_profile_updated_at();

CREATE TABLE IF NOT EXISTS roles (
  id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS user_roles (
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
  PRIMARY KEY (user_id, role_id)
);

-- =========================================================
-- 3) Providers & Contracts
-- =========================================================
CREATE TABLE IF NOT EXISTS providers (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  type         provider_type NOT NULL,
  legal_name   TEXT NOT NULL,
  display_name TEXT NOT NULL,
  country_code CHAR(2) REFERENCES countries(country_code) ON DELETE RESTRICT,
  status       user_status NOT NULL DEFAULT 'active',
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
DROP TRIGGER IF EXISTS trg_providers_updated_at ON providers;
CREATE TRIGGER trg_providers_updated_at
BEFORE UPDATE ON providers
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE IF NOT EXISTS contracts (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  provider_id    UUID NOT NULL REFERENCES providers(id) ON DELETE CASCADE,
  effective_from DATE NOT NULL,
  effective_to   DATE,
  commission_pct NUMERIC(5,2),
  currency_code  CHAR(3) NOT NULL REFERENCES currencies(code) ON DELETE RESTRICT,
  CHECK (commission_pct IS NULL OR (commission_pct >= 0 AND commission_pct <= 100))
);

-- =========================================================
-- 4) Flights
-- =========================================================
CREATE TABLE IF NOT EXISTS routes (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  origin      CHAR(3) NOT NULL REFERENCES airports(iata) ON DELETE RESTRICT,
  destination CHAR(3) NOT NULL REFERENCES airports(iata) ON DELETE RESTRICT,
  distance_km INT,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT chk_routes_origin_dest CHECK (origin <> destination),
  CONSTRAINT chk_routes_distance CHECK (distance_km IS NULL OR distance_km > 0)
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_routes_od ON routes(origin, destination);
DROP TRIGGER IF EXISTS trg_routes_updated_at ON routes;
CREATE TRIGGER trg_routes_updated_at
BEFORE UPDATE ON routes
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE IF NOT EXISTS flight_schedules (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  provider_id       UUID NOT NULL REFERENCES providers(id) ON DELETE RESTRICT,
  route_id          UUID NOT NULL REFERENCES routes(id) ON DELETE CASCADE,
  flight_number     TEXT NOT NULL,
  dow               BIT(7) NOT NULL,      -- 0=Sun .. 6=Sat
  dep_time          TIME NOT NULL,
  arr_time          TIME NOT NULL,
  arrival_day_offset SMALLINT NOT NULL DEFAULT 0,
  aircraft_code     TEXT,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT chk_fs_dow_nonzero CHECK (dow <> B'0000000')
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_fs_provider_route_flt_dow_time
  ON flight_schedules(provider_id, route_id, flight_number, dow, dep_time);
DROP TRIGGER IF EXISTS trg_flight_schedules_updated_at ON flight_schedules;
CREATE TRIGGER trg_flight_schedules_updated_at
BEFORE UPDATE ON flight_schedules
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE IF NOT EXISTS flight_instances (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  schedule_id  UUID NOT NULL REFERENCES flight_schedules(id) ON DELETE CASCADE,
  flight_date  DATE NOT NULL,
  dep_datetime TIMESTAMPTZ NOT NULL,
  arr_datetime TIMESTAMPTZ NOT NULL,
  status       VARCHAR(20) NOT NULL DEFAULT 'scheduled',
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (schedule_id, flight_date),
  CHECK (dep_datetime < arr_datetime)
);
CREATE INDEX IF NOT EXISTS idx_flight_instances_date ON flight_instances (flight_date);
DROP TRIGGER IF EXISTS trg_flight_instances_updated_at ON flight_instances;
CREATE TRIGGER trg_flight_instances_updated_at
BEFORE UPDATE ON flight_instances
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE IF NOT EXISTS seat_inventory (
  instance_id UUID NOT NULL REFERENCES flight_instances(id) ON DELETE CASCADE,
  cabin       cabin_type NOT NULL,
  fare_bucket fare_bucket_type NOT NULL,
  total_seats INT NOT NULL,
  held_seats  INT NOT NULL DEFAULT 0,
  sold_seats  INT NOT NULL DEFAULT 0,
  PRIMARY KEY (instance_id, cabin, fare_bucket),
  CHECK (held_seats + sold_seats <= total_seats)
);
CREATE INDEX IF NOT EXISTS idx_si_instance ON seat_inventory(instance_id, cabin, fare_bucket);

-- =========================================================
-- 5) Hotels
-- =========================================================
CREATE TABLE IF NOT EXISTS hotels (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  provider_id   UUID NOT NULL REFERENCES providers(id) ON DELETE RESTRICT,
  city_id       UUID NOT NULL REFERENCES cities(id) ON DELETE RESTRICT,
  name          TEXT NOT NULL,
  star_rating   NUMERIC(2,1),
  address       TEXT,
  checkin_time  TIME,
  checkout_time TIME,
  lat           NUMERIC(9,6),
  lng           NUMERIC(9,6),
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT chk_hotels_lat CHECK (lat IS NULL OR (lat >= -90 AND lat <= 90)),
  CONSTRAINT chk_hotels_lng CHECK (lng IS NULL OR (lng >= -180 AND lng <= 180))
);
CREATE INDEX IF NOT EXISTS idx_hotels_city_star ON hotels(city_id, star_rating);
DROP TRIGGER IF EXISTS trg_hotels_updated_at ON hotels;
CREATE TRIGGER trg_hotels_updated_at
BEFORE UPDATE ON hotels
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE IF NOT EXISTS hotel_rooms (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  hotel_id   UUID NOT NULL REFERENCES hotels(id) ON DELETE CASCADE,
  code       TEXT,
  capacity   INT NOT NULL,
  bed_config TEXT,
  CONSTRAINT uq_room_hotel_code UNIQUE (hotel_id, code),
  CONSTRAINT chk_room_capacity CHECK (capacity > 0)
);
CREATE INDEX IF NOT EXISTS idx_hotel_rooms_hotel ON hotel_rooms(hotel_id);

CREATE TABLE IF NOT EXISTS room_rate_plans (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  hotel_id      UUID NOT NULL REFERENCES hotels(id) ON DELETE CASCADE,
  name          TEXT NOT NULL,
  meal_plan     VARCHAR(20),
  cancellation_policy JSONB,
  currency_code CHAR(3) NOT NULL REFERENCES currencies(code) ON DELETE RESTRICT,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_rrp_hotel_name UNIQUE (hotel_id, name)
);
DROP TRIGGER IF EXISTS trg_rrp_updated_at ON room_rate_plans;
CREATE TRIGGER trg_rrp_updated_at
BEFORE UPDATE ON room_rate_plans
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE IF NOT EXISTS room_inventory_daily (
  room_id      UUID NOT NULL REFERENCES hotel_rooms(id) ON DELETE CASCADE,
  rate_plan_id UUID NOT NULL REFERENCES room_rate_plans(id) ON DELETE CASCADE,
  stay_date    DATE NOT NULL,
  allotment    INT  NOT NULL,
  sold         INT  NOT NULL DEFAULT 0,
  stop_sell    BOOLEAN NOT NULL DEFAULT FALSE,
  base_price   NUMERIC(12,2) NOT NULL,
  PRIMARY KEY (room_id, rate_plan_id, stay_date),
  CHECK (sold <= allotment),
  CHECK (allotment > 0),
  CHECK (base_price >= 0)
);
CREATE INDEX IF NOT EXISTS idx_room_inv_date ON room_inventory_daily (stay_date);
CREATE INDEX IF NOT EXISTS idx_room_inv_room_date ON room_inventory_daily (room_id, stay_date);

-- =========================================================
-- 6) Activities / Transport
-- =========================================================
CREATE TABLE IF NOT EXISTS products (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  provider_id UUID NOT NULL REFERENCES providers(id) ON DELETE RESTRICT,
  type        product_type NOT NULL,
  city_id     UUID REFERENCES cities(id) ON DELETE SET NULL,
  title       TEXT NOT NULL,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_products_city_type ON products(city_id, type);
DROP TRIGGER IF EXISTS trg_products_updated_at ON products;
CREATE TRIGGER trg_products_updated_at
BEFORE UPDATE ON products
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE IF NOT EXISTS time_slots (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id     UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  start_datetime TIMESTAMPTZ NOT NULL,
  end_datetime   TIMESTAMPTZ NOT NULL,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  CHECK (start_datetime < end_datetime),
  CONSTRAINT uq_slot_unique UNIQUE (product_id, start_datetime, end_datetime)
);
CREATE INDEX IF NOT EXISTS idx_slots_product_start ON time_slots(product_id, start_datetime);
DROP TRIGGER IF EXISTS trg_time_slots_updated_at ON time_slots;
CREATE TRIGGER trg_time_slots_updated_at
BEFORE UPDATE ON time_slots
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE IF NOT EXISTS slot_inventory (
  slot_id      UUID PRIMARY KEY REFERENCES time_slots(id) ON DELETE CASCADE,
  capacity     INT NOT NULL,
  sold         INT NOT NULL DEFAULT 0,
  price        NUMERIC(12,2) NOT NULL,
  currency_code CHAR(3) NOT NULL REFERENCES currencies(code) ON DELETE RESTRICT,
  CHECK (sold <= capacity),
  CHECK (capacity > 0),
  CHECK (price >= 0)
);

-- =========================================================
-- 7) Taxes, FX, Price Quotes
-- =========================================================
CREATE TABLE IF NOT EXISTS taxes (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  scope         VARCHAR(20) NOT NULL,
  name          TEXT NOT NULL,
  rate          NUMERIC(6,3),
  amount        NUMERIC(12,2),
  currency_code CHAR(3),
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  CHECK ((rate IS NOT NULL AND amount IS NULL) OR (rate IS NULL AND amount IS NOT NULL)),
  CHECK (rate IS NULL OR (rate >= 0 AND rate <= 1)),
  CHECK (amount IS NULL OR amount >= 0)
);

CREATE TABLE IF NOT EXISTS exchange_rates (
  rate_date DATE NOT NULL,
  base      CHAR(3) NOT NULL,
  quote     CHAR(3) NOT NULL,
  rate      NUMERIC(18,8) NOT NULL,
  PRIMARY KEY (rate_date, base, quote),
  CHECK (base <> quote),
  CHECK (rate > 0)
);

CREATE TABLE IF NOT EXISTS price_quotes (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID REFERENCES users(id) ON DELETE SET NULL,
  vertical      VARCHAR(20) NOT NULL,
  payload       JSONB NOT NULL,
  currency_code CHAR(3) NOT NULL REFERENCES currencies(code) ON DELETE RESTRICT,
  total_amount  NUMERIC(12,2) NOT NULL,
  expires_at    TIMESTAMPTZ NOT NULL,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  CHECK (total_amount >= 0),
  CHECK (expires_at > (now() - interval '1 minute'))
);
CREATE INDEX IF NOT EXISTS idx_price_quotes_expiry ON price_quotes (expires_at);

-- =========================================================
-- 8) Promo & Bookings
-- =========================================================
CREATE TABLE IF NOT EXISTS coupons (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code           TEXT UNIQUE NOT NULL,
  discount_type  discount_type NOT NULL,
  discount_value NUMERIC(12,2) NOT NULL,
  currency_code  CHAR(3),
  starts_at      TIMESTAMPTZ,
  ends_at        TIMESTAMPTZ,
  CONSTRAINT chk_coupon_window CHECK (starts_at IS NULL OR ends_at IS NULL OR starts_at < ends_at),
  CONSTRAINT chk_coupon_value CHECK (
    (discount_type = 'percent' AND discount_value >= 0 AND discount_value <= 100 AND currency_code IS NULL)
    OR
    (discount_type = 'amount'  AND discount_value >= 0 AND currency_code IS NOT NULL)
  )
);

CREATE TABLE IF NOT EXISTS bookings (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID REFERENCES users(id) ON DELETE SET NULL,
  state         booking_state NOT NULL,
  currency_code CHAR(3) NOT NULL REFERENCES currencies(code) ON DELETE RESTRICT,
  total_amount  NUMERIC(12,2) NOT NULL,
  quote_id      UUID REFERENCES price_quotes(id) ON DELETE SET NULL,
  coupon_id     UUID REFERENCES coupons(id) ON DELETE SET NULL,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  CHECK (total_amount >= 0)
);
DROP TRIGGER IF EXISTS trg_bookings_updated_at ON bookings;
CREATE TRIGGER trg_bookings_updated_at
BEFORE UPDATE ON bookings
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE IF NOT EXISTS booking_items (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  booking_id   UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
  vertical     VARCHAR(20) NOT NULL,
  supplier_ref TEXT,
  details      JSONB NOT NULL,
  price_amount NUMERIC(12,2) NOT NULL,
  CHECK (price_amount >= 0)
);
CREATE INDEX IF NOT EXISTS idx_booking_items_booking ON booking_items(booking_id);

CREATE TABLE IF NOT EXISTS passengers (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  booking_id  UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
  full_name   TEXT NOT NULL,
  nationality CHAR(2) REFERENCES countries(country_code) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS tickets (
  id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  item_id   UUID NOT NULL REFERENCES booking_items(id) ON DELETE CASCADE,
  type      ticket_type NOT NULL,
  code      TEXT NOT NULL UNIQUE,
  issued_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =========================================================
-- 9) Payments & Refunds
-- =========================================================
CREATE TABLE IF NOT EXISTS payments (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  booking_id      UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
  provider        TEXT NOT NULL,
  amount          NUMERIC(12,2) NOT NULL,
  currency_code   CHAR(3) NOT NULL REFERENCES currencies(code) ON DELETE RESTRICT,
  status          payment_status NOT NULL,
  idempotency_key TEXT UNIQUE,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  CHECK (amount > 0)
);
CREATE INDEX IF NOT EXISTS idx_payments_booking_created ON payments(booking_id, created_at);

CREATE TABLE IF NOT EXISTS refunds (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  booking_id UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
  amount     NUMERIC(12,2) NOT NULL,
  reason     TEXT,
  status     refund_status NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CHECK (amount > 0)
);
CREATE INDEX IF NOT EXISTS idx_refunds_booking_created ON refunds(booking_id, created_at);

-- =========================================================
-- 10) Reviews & Support
-- =========================================================
CREATE TABLE IF NOT EXISTS reviews (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  target_type review_target_type NOT NULL,
  target_key  TEXT NOT NULL,   -- polymorphic key (e.g., airport IATA 'HAN', hotel UUID text, etc.)
  rating      INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
  comment     TEXT,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_review_once UNIQUE (user_id, target_type, target_key)
);
CREATE INDEX IF NOT EXISTS idx_reviews_target ON reviews (target_type, target_key);

CREATE TABLE IF NOT EXISTS support_tickets (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  booking_id UUID REFERENCES bookings(id) ON DELETE SET NULL,
  subject    TEXT NOT NULL,
  status     support_status NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
DROP TRIGGER IF EXISTS trg_support_tickets_updated_at ON support_tickets;
CREATE TRIGGER trg_support_tickets_updated_at
BEFORE UPDATE ON support_tickets
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- =========================================================
-- Helpful Indexes (additional)
-- =========================================================
CREATE INDEX IF NOT EXISTS idx_cities_country ON cities(country_code);
CREATE INDEX IF NOT EXISTS idx_airports_city ON airports(city_id);
CREATE INDEX IF NOT EXISTS idx_routes_updated ON routes(updated_at);
CREATE INDEX IF NOT EXISTS idx_fs_route_dow ON flight_schedules(route_id, dow, dep_time);
CREATE INDEX IF NOT EXISTS idx_fi_sched_status ON flight_instances(schedule_id, flight_date, status);
CREATE INDEX IF NOT EXISTS idx_hotels_updated ON hotels(updated_at);
CREATE INDEX IF NOT EXISTS idx_products_updated ON products(updated_at);
CREATE INDEX IF NOT EXISTS idx_bookings_user_created ON bookings(user_id, created_at);

-- =========================================================
-- Seed minimal currencies (tuỳ chọn)
-- =========================================================
INSERT INTO currencies(code, name) VALUES
  ('USD','US Dollar'),
  ('EUR','Euro'),
  ('VND','Vietnamese Dong')
ON CONFLICT (code) DO NOTHING;

-- Done ✅

```