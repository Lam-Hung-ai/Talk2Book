from enum import Enum


class UserStatus(str, Enum):
    active = "active"
    suspended = "suspended"
    deleted = "deleted"


class ProviderType(str, Enum):
    airline = "airline"
    hotel = "hotel"
    operator = "operator"
    transport = "transport"


class BookingState(str, Enum):
    draft = "draft"
    pending_payment = "pending_payment"
    confirmed = "confirmed"
    cancelled = "cancelled"
    refunded = "refunded"


class PaymentStatus(str, Enum):
    pending = "pending"
    authorized = "authorized"
    captured = "captured"
    failed = "failed"
    refunded = "refunded"


class RefundStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    processed = "processed"
    failed = "failed"


class DiscountType(str, Enum):
    percent = "percent"
    amount = "amount"


class CabinType(str, Enum):
    economy = "economy"
    premium = "premium"
    business = "business"
    first = "first"


class FareBucketType(str, Enum):
    Y = "Y"
    B = "B"
    M = "M"
    H = "H"
    Q = "Q"
    K = "K"
    L = "L"
    T = "T"
    N = "N"
    S = "S"
    V = "V"
    R = "R"
    D = "D"
    C = "C"
    J = "J"
    F = "F"
    P = "P"
    Z = "Z"
    U = "U"
    E = "E"


class SupportStatus(str, Enum):
    open = "open"
    pending = "pending"
    resolved = "resolved"
    closed = "closed"


class ReviewTargetType(str, Enum):
    hotel = "hotel"
    product = "product"
    flight = "flight"
    airport = "airport"


class GenderType(str, Enum):
    M = "M"
    F = "F"
    O = "O"


class ProductType(str, Enum):
    tour = "tour"
    activity = "activity"
    transport = "transport"


class TicketType(str, Enum):
    flight = "flight"
    hotel = "hotel"
    tour = "tour"
