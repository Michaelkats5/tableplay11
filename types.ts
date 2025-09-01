export type Restaurant = {
  id: number;
  key: string;
  name: string;
  cuisine: string;
  price: '$'|'$$'|'$$$';
  rating: number;
  distance_km: number;
  tags: string[];
  badges: string[];
  menu_highlights: string[];
};
