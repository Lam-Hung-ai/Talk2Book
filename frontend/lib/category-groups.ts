export const CATEGORY_GROUPS = [
  "Hãng hàng không",
  "Thành phố ⭐",
  "Loại tour",
  "Tiện nghi khách sạn",
  "Loại phòng",
  "Tầm nhìn phòng",
  "Gói dịch vụ phòng",
  "Tiện nghi phòng",
  "Loại vé máy bay",
  "Hạng ghế",
  "Tiện nghi chuyến bay",
] as const;

export type CategoryGroupName = (typeof CATEGORY_GROUPS)[number];
