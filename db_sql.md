Tuyệt—dưới đây là **script SQL PostgreSQL đầy đủ** để tạo CSDL (đúng với thiết kế & ERD chúng ta đã thống nhất). Bạn có thể chạy nguyên khối trong psql/pgAdmin.

```sql
-- =========================================================
-- Travel Super-App (PostgreSQL) – Full DDL
-- =========================================================
-- (Tùy chọn)
-- CREATE DATABASE travel_app TEMPLATE template1 ENCODING 'UTF8';
-- \c travel_app

-- Extensions
CREATE EXTENSION IF NOT EXISTS citext;
CREATE EXTENSION IF NOT EXISTS pgcrypto;  -- gen_random_uuid()

-- =========================================================
-- Utility: updated_at trigger
-- =========================================================
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =========================================================
-- 1) Geo
-- =========================================================
CREATE TABLE countries (
  country_code  CHAR(2) PRIMARY KEY,
  name          TEXT NOT NULL,
  currency_code CHAR(3) NOT NULL
);

CREATE TABLE cities (
  city_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  country_code CHAR(2) NOT NULL REFERENCES countries(country_code) ON DELETE RESTRICT,
  name         TEXT NOT NULL
);

CREATE TABLE airports (
  iata     CHAR(3) PRIMARY KEY,
  icao     CHAR(4),
  city_id  UUID NOT NULL REFERENCES cities(city_id) ON DELETE RESTRICT,
  name     TEXT NOT NULL,
  timezone TEXT NOT NULL
);

-- =========================================================
-- 2) Identity & Access
-- =========================================================
CREATE TABLE users (
  user_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email         CITEXT UNIQUE NOT NULL,
  phone         VARCHAR(32),
  password_hash TEXT NOT NULL,
  status        VARCHAR(20) NOT NULL DEFAULT 'active',
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE roles (
  role_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code    TEXT UNIQUE NOT NULL
);

CREATE TABLE user_roles (
  user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  role_id UUID NOT NULL REFERENCES roles(role_id) ON DELETE CASCADE,
  PRIMARY KEY (user_id, role_id)
);

-- =========================================================
-- 3) Providers & Contracts
-- =========================================================
CREATE TABLE providers (
  provider_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  type         VARCHAR(20) NOT NULL,  -- airline|hotel|operator|transport
  legal_name   TEXT NOT NULL,
  display_name TEXT NOT NULL,
  country_code CHAR(2) REFERENCES countries(country_code) ON DELETE RESTRICT,
  status       VARCHAR(20) NOT NULL DEFAULT 'active',
  CHECK (type IN ('airline','hotel','operator','transport'))
);

CREATE TABLE contracts (
  contract_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  provider_id    UUID NOT NULL REFERENCES providers(provider_id) ON DELETE CASCADE,
  effective_from DATE NOT NULL,
  effective_to   DATE,
  commission_pct NUMERIC(5,2),
  currency_code  CHAR(3) NOT NULL,
  CHECK (commission_pct IS NULL OR (commission_pct >= 0 AND commission_pct <= 100))
);

-- =========================================================
-- 4) Flights: Catalog & Inventory
-- =========================================================
CREATE TABLE routes (
  route_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  origin      CHAR(3) NOT NULL REFERENCES airports(iata) ON DELETE RESTRICT,
  destination CHAR(3) NOT NULL REFERENCES airports(iata) ON DELETE RESTRICT,
  distance_km INT
);

CREATE TABLE flight_schedules (
  schedule_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  provider_id   UUID NOT NULL REFERENCES providers(provider_id) ON DELETE RESTRICT, -- airline
  route_id      UUID NOT NULL REFERENCES routes(route_id) ON DELETE CASCADE,
  flight_number TEXT NOT NULL,
  dow           BIT(7) NOT NULL,
  dep_time      TIME NOT NULL,
  arr_time      TIME NOT NULL,
  arrival_day_offset SMALLINT NOT NULL DEFAULT 0, -- -1,0,+1
  aircraft_code TEXT
);

CREATE TABLE flight_instances (
  instance_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  schedule_id  UUID NOT NULL REFERENCES flight_schedules(schedule_id) ON DELETE CASCADE,
  flight_date  DATE NOT NULL,
  dep_datetime TIMESTAMPTZ NOT NULL,
  arr_datetime TIMESTAMPTZ NOT NULL,
  status       VARCHAR(20) NOT NULL DEFAULT 'scheduled', -- scheduled|canceled|delayed|departed|arrived
  UNIQUE (schedule_id, flight_date),
  CHECK (dep_datetime < arr_datetime)
);

CREATE TABLE seat_inventory (
  instance_id UUID NOT NULL REFERENCES flight_instances(instance_id) ON DELETE CASCADE,
  cabin       VARCHAR(10) NOT NULL,     -- econ|prem|biz
  fare_bucket CHAR(1) NOT NULL,         -- Y,B,M...
  total_seats INT NOT NULL,
  held_seats  INT NOT NULL DEFAULT 0,
  sold_seats  INT NOT NULL DEFAULT 0,
  PRIMARY KEY (instance_id, cabin, fare_bucket),
  CHECK (total_seats >= 0 AND held_seats >= 0 AND sold_seats >= 0),
  CHECK (held_seats + sold_seats <= total_seats)
);

-- =========================================================
-- 5) Stays (Hotels)
-- =========================================================
CREATE TABLE hotels (
  hotel_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  provider_id  UUID NOT NULL REFERENCES providers(provider_id) ON DELETE RESTRICT,
  city_id      UUID NOT NULL REFERENCES cities(city_id) ON DELETE RESTRICT,
  name         TEXT NOT NULL,
  star_rating  NUMERIC(2,1),
  address      TEXT,
  checkin_time TIME,
  checkout_time TIME,
  lat          NUMERIC(9,6),
  lng          NUMERIC(9,6)
);

CREATE TABLE hotel_rooms (
  room_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  hotel_id   UUID NOT NULL REFERENCES hotels(hotel_id) ON DELETE CASCADE,
  code       TEXT,
  capacity   INT NOT NULL,
  bed_config TEXT
);

CREATE TABLE room_rate_plans (
  rate_plan_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  hotel_id           UUID NOT NULL REFERENCES hotels(hotel_id) ON DELETE CASCADE,
  name               TEXT NOT NULL,
  meal_plan          VARCHAR(20),      -- RO|BB|HB...
  cancellation_policy JSONB,
  currency_code      CHAR(3) NOT NULL
);

CREATE TABLE room_inventory_daily (
  room_id       UUID NOT NULL REFERENCES hotel_rooms(room_id) ON DELETE CASCADE,
  rate_plan_id  UUID NOT NULL REFERENCES room_rate_plans(rate_plan_id) ON DELETE CASCADE,
  stay_date     DATE NOT NULL,
  allotment     INT  NOT NULL,
  sold          INT  NOT NULL DEFAULT 0,
  stop_sell     BOOLEAN NOT NULL DEFAULT FALSE,
  min_length_of_stay INT DEFAULT 1,
  max_length_of_stay INT,
  cutoff_hours  INT,
  base_price    NUMERIC(12,2) NOT NULL,
  tax_inclusive BOOLEAN NOT NULL DEFAULT TRUE,
  PRIMARY KEY (room_id, rate_plan_id, stay_date),
  CHECK (allotment >= 0 AND sold >= 0),
  CHECK (sold <= allotment)
);

-- =========================================================
-- 6) Activities / Transport
-- =========================================================
CREATE TABLE products (
  product_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  provider_id UUID NOT NULL REFERENCES providers(provider_id) ON DELETE RESTRICT,
  type        VARCHAR(20) NOT NULL,   -- activity|transport
  city_id     UUID REFERENCES cities(city_id) ON DELETE SET NULL,
  title       TEXT NOT NULL,
  CHECK (type IN ('activity','transport'))
);

CREATE TABLE time_slots (
  slot_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id     UUID NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
  start_datetime TIMESTAMPTZ NOT NULL,
  end_datetime   TIMESTAMPTZ NOT NULL,
  CHECK (start_datetime < end_datetime)
);

CREATE TABLE slot_inventory (
  slot_id       UUID PRIMARY KEY REFERENCES time_slots(slot_id) ON DELETE CASCADE,
  capacity      INT NOT NULL,
  sold          INT NOT NULL DEFAULT 0,
  price         NUMERIC(12,2) NOT NULL,
  currency_code CHAR(3) NOT NULL,
  CHECK (capacity >= 0 AND sold >= 0 AND sold <= capacity)
);

-- =========================================================
-- 7) Taxes, FX, Price Quotes
-- =========================================================
CREATE TABLE taxes (
  tax_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  scope         VARCHAR(20) NOT NULL,  -- flight|hotel|activity
  name          TEXT NOT NULL,
  rate          NUMERIC(6,3),
  amount        NUMERIC(12,2),
  currency_code CHAR(3),
  CHECK (scope IN ('flight','hotel','activity')),
  CHECK ( (rate IS NOT NULL AND amount IS NULL) OR (rate IS NULL AND amount IS NOT NULL) )
);

CREATE TABLE exchange_rates (
  rate_date DATE NOT NULL,
  base      CHAR(3) NOT NULL,
  quote     CHAR(3) NOT NULL,
  rate      NUMERIC(18,8) NOT NULL,
  PRIMARY KEY (rate_date, base, quote)
);

CREATE TABLE price_quotes (
  quote_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID REFERENCES users(user_id) ON DELETE SET NULL,
  vertical      VARCHAR(20) NOT NULL,  -- flight|hotel|activity
  payload       JSONB NOT NULL,        -- snapshot giá/thuế/fee
  currency_code CHAR(3) NOT NULL,
  total_amount  NUMERIC(12,2) NOT NULL,
  expires_at    TIMESTAMPTZ NOT NULL,
  CHECK (vertical IN ('flight','hotel','activity'))
);

-- =========================================================
-- 8) Promo & Bookings
-- =========================================================
CREATE TABLE coupons (
  coupon_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code            TEXT UNIQUE NOT NULL,
  discount_type   VARCHAR(10) NOT NULL,   -- percent|amount
  discount_value  NUMERIC(12,2) NOT NULL,
  currency_code   CHAR(3),
  starts_at       TIMESTAMPTZ,
  ends_at         TIMESTAMPTZ,
  max_redemptions INT,
  per_user_limit  INT,
  CHECK (discount_type IN ('percent','amount')),
  CHECK ( (discount_type <> 'percent') OR (discount_value > 0 AND discount_value <= 100) ),
  CHECK ( (discount_type <> 'amount')  OR (currency_code IS NOT NULL) )
);

CREATE TABLE bookings (
  booking_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID REFERENCES users(user_id) ON DELETE SET NULL,
  state         VARCHAR(20) NOT NULL,   -- created|holding|paid|ticketed|canceled|refunded|failed
  currency_code CHAR(3) NOT NULL,
  total_amount  NUMERIC(12,2) NOT NULL,
  quote_id      UUID REFERENCES price_quotes(quote_id) ON DELETE SET NULL,
  coupon_id     UUID REFERENCES coupons(coupon_id) ON DELETE SET NULL,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  CHECK (state IN ('created','holding','paid','ticketed','canceled','refunded','failed'))
);

CREATE TRIGGER trg_bookings_updated_at
BEFORE UPDATE ON bookings
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE coupon_redemptions (
  coupon_id   UUID NOT NULL REFERENCES coupons(coupon_id) ON DELETE CASCADE,
  user_id     UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  booking_id  UUID NOT NULL REFERENCES bookings(booking_id) ON DELETE CASCADE,
  redeemed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (coupon_id, user_id, booking_id)
);
-- mỗi booking chỉ dùng tối đa 1 coupon
CREATE UNIQUE INDEX ux_coupon_per_booking ON coupon_redemptions (booking_id);

-- =========================================================
-- 9) Booking Items, Passengers, Tickets, Audit
-- =========================================================
CREATE TABLE booking_items (
  item_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  booking_id     UUID NOT NULL REFERENCES bookings(booking_id) ON DELETE CASCADE,
  vertical       VARCHAR(20) NOT NULL,   -- flight|hotel|activity
  supplier_ref   TEXT,
  start_datetime TIMESTAMPTZ,
  end_datetime   TIMESTAMPTZ,
  details        JSONB NOT NULL,
  price_amount   NUMERIC(12,2) NOT NULL,
  CHECK (vertical IN ('flight','hotel','activity'))
);
CREATE INDEX idx_booking_items_booking ON booking_items (booking_id);

CREATE TABLE passengers (
  passenger_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  booking_id   UUID NOT NULL REFERENCES bookings(booking_id) ON DELETE CASCADE,
  first_name   TEXT NOT NULL,
  last_name    TEXT NOT NULL,
  dob          DATE,
  gender       CHAR(1),
  nationality  CHAR(2)
);

CREATE TABLE tickets (
  ticket_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  item_id   UUID NOT NULL REFERENCES booking_items(item_id) ON DELETE CASCADE,
  type      VARCHAR(20) NOT NULL,   -- eticket|voucher
  code      TEXT NOT NULL,
  issued_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CHECK (type IN ('eticket','voucher')),
  CONSTRAINT ux_ticket_per_item UNIQUE (item_id),
  CONSTRAINT ux_ticket_code UNIQUE (code)
);

CREATE TABLE booking_audit_logs (
  log_id     BIGSERIAL PRIMARY KEY,
  booking_id UUID NOT NULL REFERENCES bookings(booking_id) ON DELETE CASCADE,
  action     TEXT NOT NULL,      -- state_change|hold|release|issue|refund
  actor      TEXT NOT NULL,      -- system|user|provider
  data       JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =========================================================
-- 10) Payments & Refunds
-- =========================================================
CREATE TABLE payments (
  payment_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  booking_id      UUID NOT NULL REFERENCES bookings(booking_id) ON DELETE CASCADE,
  provider        TEXT NOT NULL,         -- stripe|paypal|momo|zalopay...
  amount          NUMERIC(12,2) NOT NULL,
  currency_code   CHAR(3) NOT NULL,
  status          VARCHAR(20) NOT NULL,  -- pending|authorized|captured|failed|refunded
  idempotency_key TEXT UNIQUE,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  CHECK (status IN ('pending','authorized','captured','failed','refunded'))
);
CREATE INDEX idx_payments_booking ON payments (booking_id);

CREATE TABLE payment_transactions (
  txn_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  payment_id   UUID NOT NULL REFERENCES payments(payment_id) ON DELETE CASCADE,
  type         VARCHAR(20) NOT NULL,      -- authorize|capture|refund|void
  gateway_ref  TEXT,
  amount       NUMERIC(12,2) NOT NULL,
  status       VARCHAR(20) NOT NULL,      -- pending|succeeded|failed
  processed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CHECK (type IN ('authorize','capture','refund','void')),
  CHECK (status IN ('pending','succeeded','failed'))
);

CREATE TABLE refunds (
  refund_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  booking_id UUID NOT NULL REFERENCES bookings(booking_id) ON DELETE CASCADE,
  amount     NUMERIC(12,2) NOT NULL,
  reason     TEXT,
  status     VARCHAR(20) NOT NULL,      -- pending|processed|failed
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CHECK (status IN ('pending','processed','failed'))
);

-- =========================================================
-- 11) Reviews & Support
-- =========================================================
CREATE TABLE reviews (
  review_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  target_type VARCHAR(20) NOT NULL,     -- hotel|activity|flight
  target_id   UUID NOT NULL,
  rating      INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
  title       TEXT,
  body        TEXT,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  CHECK (target_type IN ('hotel','activity','flight'))
);
CREATE UNIQUE INDEX ux_review_once ON reviews (user_id, target_type, target_id);

CREATE TABLE support_tickets (
  ticket_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id    UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  booking_id UUID REFERENCES bookings(booking_id) ON DELETE SET NULL,
  subject    TEXT NOT NULL,
  status     VARCHAR(20) NOT NULL,      -- open|pending|resolved|closed
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CHECK (status IN ('open','pending','resolved','closed'))
);

-- =========================================================
-- Helpful Indexes
-- =========================================================
CREATE INDEX idx_price_quotes_expiry ON price_quotes (expires_at);
CREATE INDEX idx_room_inv_date ON room_inventory_daily (stay_date);
CREATE INDEX idx_flight_instances_date ON flight_instances (flight_date);
CREATE INDEX idx_coupon_redemptions_coupon_user ON coupon_redemptions (coupon_id, user_id);

-- =========================================================
-- Done
-- =========================================================
```

Bạn cần mình kèm luôn **bộ dữ liệu seed mẫu** (quốc gia, thành phố, vài sân bay/khách sạn demo) hoặc **script drop-all** để reset môi trường không?
