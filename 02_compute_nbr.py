import rasterio as rio
import numpy as np

def compute_nbr_with_mask(
    b8_path,
    b12_path,
    b3_path,
    scl_path,
    output_path,
    ndwi_thresh=0.0
):
    """
    Compute NBR with SCL + NDWI masking.
    All bands must be reflectance and 10 m.
    """

    with rio.open(b8_path) as b8_src, \
         rio.open(b12_path) as b12_src, \
         rio.open(b3_path) as b3_src, \
         rio.open(scl_path) as scl_src:

        b8 = b8_src.read(1).astype(np.float32)
        b12 = b12_src.read(1).astype(np.float32)
        b3 = b3_src.read(1).astype(np.float32)
        scl = scl_src.read(1)

        profile = b8_src.profile.copy()

    # -------------------------------------------------
    # SCL mask (True = mask out)
    # -------------------------------------------------
    scl_mask = np.isin(
        scl,
        [3, 6, 8, 9, 10, 11]  # cloud, shadow, water, snow
    )

    # -------------------------------------------------
    # NDWI mask (water)
    # -------------------------------------------------
    ndwi = np.full(b8.shape, np.nan, dtype=np.float32)
    valid_ndwi = (b3 + b8) != 0
    ndwi[valid_ndwi] = (b3[valid_ndwi] - b8[valid_ndwi]) / (b3[valid_ndwi] + b8[valid_ndwi])

    ndwi_mask = ndwi > ndwi_thresh

    # -------------------------------------------------
    # Combined mask (water & clouds)
    # -------------------------------------------------
    mask = (
        scl_mask |
        ndwi_mask |
        ((b8 + b12) == 0)
    )

    # -------------------------------------------------
    # Compute NBR
    # -------------------------------------------------
    nbr = np.full(b8.shape, np.nan, dtype=np.float32)
    valid = ~mask
    nbr[valid] = (b8[valid] - b12[valid]) / (b8[valid] + b12[valid])

    # -------------------------------------------------
    # Save output
    # -------------------------------------------------
    profile.update(
        driver="GTiff",
        dtype=np.float32,
        count=1,
        nodata=np.nan
    )

    with rio.open(output_path, "w", **profile) as dst:
        dst.write(nbr, 1)

    print(f"NBR written at: {output_path}")

compute_nbr_with_mask(
    b8_path=r"Outputs\20240716T091559_B08_reflect.tif",
    b12_path=r"Outputs\20240716T091559_B12_10m.tif",
    b3_path=r"Outputs\20240716T091559_B03_reflect.tif",
    scl_path=r"Outputs\20240716T091559_SCL_10m.tif",
    output_path=r"Outputs\NBR_pre_fire.tif"
)

compute_nbr_with_mask(
    b8_path=r"Outputs\20240815T091559_B08_reflect.tif",
    b12_path=r"Outputs\20240815T091559_B12_10m.tif",
    b3_path=r"Outputs\20240815T091559_B03_reflect.tif",
    scl_path=r"Outputs\20240815T091559_SCL_10m.tif",
    output_path=r"Outputs\NBR_post_fire.tif"
)

