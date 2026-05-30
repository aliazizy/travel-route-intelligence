export type TravelRequest = {
  request_text: string;
  default_country?: string | null;
  language?: string;
  client_context?: Record<string, unknown>;
};

export type ParsedPlaceRef = {
  name: string;
  place_type: string;
  city_hint?: string | null;
  country_hint?: string | null;
  role?: string | null;
  day?: number | null;
  nights?: number | null;
  confidence: number;
  inferred: boolean;
};

export type ItineraryStep = {
  sequence_index: number;
  day?: number | null;
  step_type: string;
  name: string;
  latitude?: number | null;
  longitude?: number | null;
  role?: string | null;
  confidence: number;
  locked: boolean;
  editable: boolean;
  warnings: string[];
};

export type ResolvedPlace = {
  raw_text: string;
  canonical_name: string;
  place_type: string;
  latitude: number;
  longitude: number;
  provider: string;
  confidence: number;
  alternatives: Record<string, unknown>[];
};

export type RouteSegment = {
  from_sequence_index: number;
  to_sequence_index: number;
  distance_meters?: number | null;
  duration_seconds?: number | null;
  geometry_geojson?: GeoJSON.LineString | null;
  provider?: string | null;
};

export type FullProcessResponse = {
  request_id: string;
  parsed_itinerary: {
    arrival?: ParsedPlaceRef | null;
    departure?: ParsedPlaceRef | null;
    cities: ParsedPlaceRef[];
    hotels: ParsedPlaceRef[];
    activities: ParsedPlaceRef[];
    restaurants: ParsedPlaceRef[];
    transport: Record<string, unknown>;
    constraints: string[];
  };
  entities: Array<Record<string, unknown>>;
  resolved_places: ResolvedPlace[];
  unresolved_places: Array<Record<string, unknown>>;
  sequence: ItineraryStep[];
  route_segments: RouteSegment[];
  geojson: GeoJSON.FeatureCollection;
  warnings: string[];
  confidence_summary: {
    overall: number;
    parsing: number;
    geocoding: number;
    sequencing: number;
  };
};
