# Uganda Roads dataset — pre-transformation audit

**Dataset location:** `data/uganda_roads/`

**Original archive:** `data/uganda_roads.zip` (303,362 bytes; preserved unchanged)
**Review purpose:** inventory and validation only; no attributes were imputed or transformed.

## Contents

| File | Purpose | Check |
|---|---|---|
| `Uganda_Roads.shp` | Road line geometry | 87 PolyLine records; readable |
| `Uganda_Roads.shx` | Geometry index | 87 entries; offsets and lengths match `.shp` |
| `Uganda_Roads.dbf` | Road attributes | 87 rows; 18 fields; row count matches geometry |
| `Uganda_Roads.prj` | Coordinate reference system | WGS 84 geographic coordinates (decimal degrees) |
| `Uganda_Roads.sbn`, `.sbx` | Spatial index files | Present |
| `Uganda_Roads.shp.xml` | ArcGIS metadata | Present, but some counts/extents do not match the data |

The ZIP member CRC checks passed. There is no `.cpg` file, so the source does not explicitly declare DBF text encoding. The included text values loaded successfully during inspection.

## Attribute header

Types follow dBASE notation: `C` = character, `N` = numeric; width and decimal places are shown as stored.

| Field | Stored type | Field | Stored type |
|---|---:|---|---:|
| `LINKNO` | N(10,0) | `ROADNO` | C(10) |
| `START_KM` | N(10,0) | `END_KM` | N(10,0) |
| `LENGTH` | N(10,2) | `STARTDESC` | C(50) |
| `ENDDESC` | C(50) | `CLASS` | C(20) |
| `REGION` | C(30) | `WIDTH` | N(10,2) |
| `LANES` | N(5,0) | `SURFTYPE` | C(30) |
| `CONDITION` | C(30) | `AADT` | N(10,0) |
| `iso3` | C(50) | `AICD_REG` | N(4,0) |
| `TAH` | N(4,0) | `Class_1` | N(4,0) |

## Dataset profile

- **87** road segments and **27,477** vertices.
- Geometry coordinate bounds: longitude **29.71735–34.56693**, latitude **−1.42425–3.57535**.
- Regions: Central (24), Eastern (16), Western (16), Northern (15), Southern (8), Nile (7), Karamoyo (1).
- Surface: Paved (58), Unpaved (24), Unknown (5).
- Condition: Fair (32), Good (16), Poor (6), Bad (4), Unknown (29).
- Numeric ranges: `LENGTH` 1.90–92.48, `WIDTH` 4.80–14.00, `LANES` 2–4, `AADT` 13–12,025. The source does **not** state `LENGTH`/`WIDTH` units.
- Every `iso3` value is `UGA`. Every `START_KM` value is 0, and every `Class_1` value is 1. These fields are currently non-varying in this file.
- `ROADNO` is unique (87 distinct values); `LINKNO` has 79 distinct values, with eight identifiers appearing twice.

## Missingness and validation findings

### Actual blank values

- `ENDDESC` is blank in **6 of 87** records.
- No other DBF fields have blank values in the supplied records.

### Explicit unknown labels

“Unknown” is an existing category, not a blank: `CONDITION` has 29, `CLASS` has 5, and `SURFTYPE` has 5 such records. Do not silently convert these to null or infer replacements without a project rule.

### Documentation or consistency gaps

1. The metadata reports **281 features**, but the `.shp`, `.shx`, and `.dbf` contain **87**. Treat the count in the metadata as stale or mismatched until the publisher clarifies it.
2. The metadata extent (29.598534–34.931301 longitude, −1.424248–3.780505 latitude) is broader than the actual geometry extent.
3. One polyline's stored per-record bounding box slightly overstates its minimum latitude (about **0.00037°**). Its point coordinates and record structure are readable.
4. No `.cpg` encoding declaration is present.
5. `LENGTH` unit and semantics are not documented clearly enough to assume kilometers. `LENGTH` differs from `END_KM - START_KM` by more than 0.02 in 34 records; this is a review flag, not proof of an error, especially because units/definitions are unclear.
6. Metadata says the road data pertains to **2004**, compiled by Africon Limited for the World Bank/AICD study from Roads Agency Formation Unit data. It is a historical snapshot; no repeated dates or deterioration-over-time target are included.

## Recommendation before transformation

Keep the archive and extracted files as the immutable source. Decide how to handle the six blank `ENDDESC` values and the explicit `Unknown` labels; verify the feature count and length units if possible; and use an appropriate projected CRS before calculating distances. This dataset can support a historical condition baseline, but by itself it cannot establish how roads deteriorated over time.
