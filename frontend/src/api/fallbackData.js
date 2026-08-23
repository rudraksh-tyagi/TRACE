/**
 * TRACE Static Demonstration Fallback Data
 * Matches exact backend Pydantic models (MasterIncidentResponse, VesselSchema, AttributionSchema)
 */

export const FALLBACK_INCIDENT = {
  incident_id: "INC-2026-001",
  spill: {
    spill_id: "SP001",
    detected: true,
    confidence: 0.94,
    timestamp: "2025-05-22T08:15:00Z",
    centroid: {
      lat: 18.4200,
      lon: 72.8100
    },
    area_km2: 18.60,
    perimeter_km: 27.40,
    polygon_geojson: {
      type: "Feature",
      properties: {
        spill_id: "SP001",
        source: "Sentinel-1 SAR oil_mask.tif"
      },
      geometry: {
        type: "Polygon",
        coordinates: [
          [
            [72.785, 18.410],
            [72.805, 18.395],
            [72.835, 18.405],
            [72.845, 18.425],
            [72.830, 18.445],
            [72.800, 18.440],
            [72.780, 18.425],
            [72.785, 18.410]
          ]
        ]
      }
    },
    bounding_box: {
      min_lat: 18.395,
      min_lon: 72.780,
      max_lat: 18.445,
      max_lon: 72.845
    }
  },
  drift: {
    origin_coordinates: {
      lat: 18.3200,
      lon: 72.1800
    },
    source_time_window: {
      start_time: "2025-05-22T02:00:00Z",
      end_time: "2025-05-22T03:30:00Z"
    },
    uncertainty_radius_km: 25.60,
    backward_track: [
      { lat: 18.3200, lon: 72.1800, timestamp: "2025-05-22T02:30:00Z" },
      { lat: 18.3450, lon: 72.3200, timestamp: "2025-05-22T04:00:00Z" },
      { lat: 18.3700, lon: 72.4800, timestamp: "2025-05-22T05:30:00Z" },
      { lat: 18.3950, lon: 72.6400, timestamp: "2025-05-22T07:00:00Z" },
      { lat: 18.4200, lon: 72.8100, timestamp: "2025-05-22T08:15:00Z" }
    ],
    forecast_tracks: [
      {
        points: [
          { lat: 18.4200, lon: 72.8100, timestamp: "2025-05-22T08:15:00Z" },
          { lat: 18.4450, lon: 72.9500, timestamp: "2025-05-22T14:00:00Z" },
          { lat: 18.4700, lon: 73.1000, timestamp: "2025-05-22T20:00:00Z" }
        ]
      }
    ]
  },
  ranked_candidates: [
    {
      mmsi: "123456789",
      vessel_identity: "Vessel A (Ocean Meridian)",
      overall_score: 91.0,
      component_scores: {
        distance_score: 94.0,
        time_compatibility_score: 97.0,
        trajectory_consistency_score: 88.0,
        behavior_score: 72.0
      },
      explanations: [
        "Vessel was within the probable source region during the estimated time window.",
        "Vessel was present during the source time window.",
        "Historical trajectory is consistent with the backward drift vector.",
        "AIS behavior indicators show loitering near source region.",
        "AIS gap detected near source coordinates."
      ]
    },
    {
      mmsi: "987654321",
      vessel_identity: "Vessel B (Gulf Carrier)",
      overall_score: 74.0,
      component_scores: {
        distance_score: 78.0,
        time_compatibility_score: 82.0,
        trajectory_consistency_score: 70.0,
        behavior_score: 65.0
      },
      explanations: [
        "Vessel trajectory passed within 28.7 km of estimated source region.",
        "Timing correlates moderately with initial spill detection window.",
        "Steady course over ground with minor speed fluctuations."
      ]
    },
    {
      mmsi: "456789123",
      vessel_identity: "Vessel C (Blue Horizon)",
      overall_score: 43.0,
      component_scores: {
        distance_score: 45.0,
        time_compatibility_score: 50.0,
        trajectory_consistency_score: 40.0,
        behavior_score: 35.0
      },
      explanations: [
        "Vessel was 45.3 km from source area during origin window.",
        "Partial time overlap detected but distance reduces compatibility."
      ]
    },
    {
      mmsi: "321654987",
      vessel_identity: "Vessel D (Atlantic Trader)",
      overall_score: 22.0,
      component_scores: {
        distance_score: 20.0,
        time_compatibility_score: 25.0,
        trajectory_consistency_score: 22.0,
        behavior_score: 20.0
      },
      explanations: [
        "Vessel crossed maritime corridor 63.1 km distant from source area.",
        "Low spatial & temporal correlation."
      ]
    },
    {
      mmsi: "654987321",
      vessel_identity: "Vessel E (Pacific Navigator)",
      overall_score: 11.0,
      component_scores: {
        distance_score: 10.0,
        time_compatibility_score: 12.0,
        trajectory_consistency_score: 10.0,
        behavior_score: 10.0
      },
      explanations: [
        "Vessel transit 78.9 km away from spill centroid.",
        "No spatial or temporal overlap with source region."
      ]
    }
  ],
  metadata: {
    generation_timestamp: "2025-05-22T10:45:00Z",
    system_version: "TRACE-0.1.0"
  }
};

export const FALLBACK_VESSELS = [
  {
    spill_id: "SP001",
    mmsi: "123456789",
    vessel_name: "Vessel A",
    vessel_type: "Tanker",
    minimum_distance_km: 12.4,
    source_window_presence: true,
    time_spent_near_source_min: 75,
    average_speed: 10.3,
    course: 63.0,
    ais_gap_detected: true,
    trajectory: [
      { timestamp: "2025-05-22T01:30:00Z", lat: 18.2500, lon: 72.0500 },
      { timestamp: "2025-05-22T02:15:00Z", lat: 18.3100, lon: 72.1600 },
      { timestamp: "2025-05-22T03:00:00Z", lat: 18.3300, lon: 72.2200 },
      { timestamp: "2025-05-22T04:30:00Z", lat: 18.4100, lon: 72.4200 },
      { timestamp: "2025-05-22T06:00:00Z", lat: 18.5200, lon: 72.6500 }
    ]
  },
  {
    spill_id: "SP001",
    mmsi: "987654321",
    vessel_name: "Vessel B",
    vessel_type: "Cargo",
    minimum_distance_km: 28.7,
    source_window_presence: true,
    time_spent_near_source_min: 40,
    average_speed: 12.7,
    course: 51.0,
    ais_gap_detected: false,
    trajectory: [
      { timestamp: "2025-05-22T01:00:00Z", lat: 18.1500, lon: 72.0000 },
      { timestamp: "2025-05-22T02:45:00Z", lat: 18.2800, lon: 72.2800 },
      { timestamp: "2025-05-22T04:30:00Z", lat: 18.3900, lon: 72.5500 }
    ]
  },
  {
    spill_id: "SP001",
    mmsi: "456789123",
    vessel_name: "Vessel C",
    vessel_type: "Tanker",
    minimum_distance_km: 45.3,
    source_window_presence: false, // Partial presence
    time_spent_near_source_min: 15,
    average_speed: 11.2,
    course: 93.0,
    ais_gap_detected: false,
    trajectory: [
      { timestamp: "2025-05-22T02:00:00Z", lat: 18.5000, lon: 72.1000 },
      { timestamp: "2025-05-22T04:00:00Z", lat: 18.4800, lon: 72.3500 },
      { timestamp: "2025-05-22T06:00:00Z", lat: 18.4500, lon: 72.6000 }
    ]
  },
  {
    spill_id: "SP001",
    mmsi: "321654987",
    vessel_name: "Vessel D",
    vessel_type: "Supply",
    minimum_distance_km: 63.1,
    source_window_presence: false,
    time_spent_near_source_min: 0,
    average_speed: 14.5,
    course: 120.0,
    ais_gap_detected: false,
    trajectory: [
      { timestamp: "2025-05-22T01:00:00Z", lat: 18.0000, lon: 72.5000 },
      { timestamp: "2025-05-22T03:00:00Z", lat: 18.1000, lon: 72.7000 }
    ]
  },
  {
    spill_id: "SP001",
    mmsi: "654987321",
    vessel_name: "Vessel E",
    vessel_type: "Cargo",
    minimum_distance_km: 78.9,
    source_window_presence: false,
    time_spent_near_source_min: 0,
    average_speed: 15.0,
    course: 140.0,
    ais_gap_detected: false,
    trajectory: [
      { timestamp: "2025-05-22T01:00:00Z", lat: 17.9000, lon: 72.8000 },
      { timestamp: "2025-05-22T03:00:00Z", lat: 17.9500, lon: 72.9500 }
    ]
  }
];
