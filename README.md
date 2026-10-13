# Road deterioration datasets

Both source archives and their extracted contents are in `data/`:

- `uganda_roads.zip` and `uganda_roads/`: Uganda road-network shapefile (87 line features and 18 attributes).
- `road_surface_condition_coco.zip` and `road_surface_condition_coco/`: COCO segmentation image dataset (3,154 images and 6,304 annotations).

These are separate datasets: the first is geospatial road inventory; the second is road-surface defect imagery.

## Open the local viewer

From the project root, run:

```powershell
python viewer/server.py
```

Then open <http://127.0.0.1:8000> in your browser. The viewer uses Python's standard library only and currently displays the Uganda road-network shapefile. Use **Color by** to compare condition, road class, or region; search the attribute table or click a road to see all its fields.

Stop the server with Ctrl+C. No files are edited by the viewer.

## Dataset notes

- The supplied shapefile contains 87 PolyLine features and 18 DBF attribute fields.
- Its metadata describes 2004 road data and reports 281 features, which does not match the supplied shapefile/DBF count.
- `CONDITION` has 29 `Unknown` values, and six `ENDDESC` values are blank.
- The projection is WGS 84 geographic coordinates (degrees). The provided files do not state the units for `LENGTH`.
- The viewer is for exploration only; it does not clean, impute, or transform the data.

## COCO image dataset notes

- Extracted images and annotations are under `data/road_surface_condition_coco/`; the original ZIP is preserved as `data/road_surface_condition_coco.zip`.
- The COCO manifest is `data/road_surface_condition_coco/train/_annotations.coco.json`. It references 3,154 640×640 grayscale images and 6,304 segmentation annotations.
- Classes with annotations: `Cracks`, `Damaged_Asphalt`, `Open_Manhole`, `Potholes`, and `Water_Filled_Potholes`.
- The archive contains only a `train` split; no validation or test split was included.
- The included Roboflow note states the license is CC BY 4.0 and documents resizing/grayscale preprocessing and augmentations.
- Import validation passed: archive CRC is valid, all 3,154 manifest image references resolve, and all 6,304 annotations include polygon segmentation data.
