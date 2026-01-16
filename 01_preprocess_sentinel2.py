import rasterio
import numpy as np
from rasterio.warp import reproject
from rasterio.enums import Resampling
import os



#data paths
b8_pre_fire = r"Sentinel_data\T34TFK_20240716T091559_B08_10m.jp2"
b8_post_fire = r"Sentinel_data\T34TFK_20240815T091559_B08_10m.jp2"

b12_pre_fire = r"Sentinel_data\T34TFK_20240716T091559_B12_20m.jp2"
b12_post_fire =  r"Sentinel_data\T34TFK_20240815T091559_B12_20m.jp2"

b3_pre_fire = r"Sentinel_data\T34TFK_20240716T091559_B03_10m.jp2"
b3_post_fire = r"Sentinel_data\T34TFK_20240815T091559_B03_10m.jp2"

scl_pre_fire = r"Sentinel_data\T34TFK_20240716T091559_SCL_20m.jp2"
scl_post_fire = r"Sentinel_data\T34TFK_20240815T091559_SCL_20m.jp2"



out_dir = r"Outputs"
os.makedirs(out_dir, exist_ok=True)


reflectiv_bands = [
    b3_pre_fire,
    b3_post_fire,
    b8_pre_fire,
    b8_post_fire
]

inputs = [
    b12_pre_fire,
    b12_post_fire,
    scl_pre_fire,
    scl_post_fire
]

# -------------------------------------------------
# REFERENCE 10 m GRID (B08 pre-fire)
# -------------------------------------------------
with rasterio.open(b8_pre_fire) as ref:
    ref_profile = ref.profile
    ref_transform = ref.transform
    ref_crs = ref.crs
    ref_shape = ref.read(1).shape

# -------------------------------------------------
# LOOP
# -------------------------------------------------
for x in inputs:

    with rasterio.open(x) as src:
        data = src.read(1)
        src_transform = src.transform
        src_crs = src.crs

    # Allocate output array
    out = np.empty(ref_shape, dtype=np.float32)

    # -------------------------
    # SCL (categorical)
    # -------------------------
    if "SCL" in os.path.basename(x):
        reproject(
            source=data,
            destination=out,
            src_transform=src_transform,
            src_crs=src_crs,
            dst_transform=ref_transform,
            dst_crs=ref_crs,
            resampling=Resampling.nearest
        )
        out = out.astype(np.uint8)

    # -------------------------
    # REFLECTANCE BANDS (B12)
    # -------------------------
    else:
        data = data.astype("float32") / 10000.0

        reproject(
            source=data,
            destination=out,
            src_transform=src_transform,
            src_crs=src_crs,
            dst_transform=ref_transform,
            dst_crs=ref_crs,
            resampling=Resampling.bilinear
        )

    # -------------------------
    # OUTPUT NAME
    # -------------------------
    filename = os.path.basename(x)
    parts = filename.split("_")

    timestamp = parts[1]   # 20240716T091559
    band = parts[2]        # B12 or SCL

    out_path = rf"{out_dir}\{timestamp}_{band}_10m.tif"

    # -------------------------
    # SAVE (GeoTIFF)
    # -------------------------
    ref_profile.update(
        driver="GTiff",
        dtype=out.dtype,
        nodata=None
    )

    with rasterio.open(out_path, "w", **ref_profile) as dst:
        dst.write(out, 1)

    print(f"Saved: {out_path}")

for z in reflectiv_bands:
    with rasterio.open(z) as src:
        data = src.read(1).astype(np.float32)  # convert to float
        profile = src.profile

        # Convert to reflectance
        reflectance = data / 10000.0

        # Update profile for float32 GeoTIFF
        profile.update(
            driver="GTiff",
            dtype=rasterio.float32,
            nodata=None
        )

        # -------------------------
        # OUTPUT NAME
        # -------------------------
        filename = os.path.basename(z)
        parts = filename.split("_")

        timestamp = parts[1]   # 20240716T091559
        band = parts[2]        # B12 or SCL

        out_path = rf"{out_dir}\{timestamp}_{band}_reflect.tif"


    with rasterio.open(out_path, "w", **profile) as dst:
        dst.write(reflectance, 1)

    print(f"Saved at: {out_path}")
