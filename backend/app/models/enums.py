from enum import StrEnum


class UserStatus(StrEnum):
    active = "active"
    suspended = "suspended"
    deleted = "deleted"


class ProviderType(StrEnum):
    airline = "airline"
    hotel = "hotel"
    tour = "tour"


class BookingState(StrEnum):
    draft = "draft"
    pending_payment = "pending_payment"
    confirmed = "confirmed"
    cancelled = "cancelled"
    refunded = "refunded"


class PaymentStatus(StrEnum):
    pending = "pending"
    authorized = "authorized"
    captured = "captured"
    failed = "failed"
    refunded = "refunded"


class DiscountType(StrEnum):
    percent = "percent"
    amount = "amount"


class CabinType(StrEnum):
    economy = "Phổ thông"
    premium = "Phổ thông đặc biệt"
    business = "Thương gia"
    first = "Hạng nhất"


class ReviewTargetType(StrEnum):
    hotel = "hotel"
    product = "product"
    flight = "flight"
    airport = "airport"


class GenderType(StrEnum):
    M = "M"
    F = "F"
    other = "O"


class ProductType(StrEnum):
    tour = "tour"
    activity = "activity"
    transport = "transport"


class TicketType(StrEnum):
    flight = "flight"
    hotel = "hotel"
    tour = "tour"
