import rasterio
import numpy as np

def compute_dnbr_rbr(
    nbr_pre_path,
    nbr_post_path,
    dnbr_out_path,
    rbr_out_path
):
    """
    Compute dNBR and RBR from pre- and post-fire NBR rasters.
    """

    # -------------------------
    # Read NBR rasters
    # -------------------------
    with rasterio.open(nbr_pre_path) as pre_src:
        nbr_pre = pre_src.read(1).astype(np.float32)
        profile = pre_src.profile.copy()
        nodata = pre_src.nodata

    with rasterio.open(nbr_post_path) as post_src:
        nbr_post = post_src.read(1).astype(np.float32)

    # -------------------------
    # Build valid mask
    # -------------------------
    mask = np.isnan(nbr_pre) | np.isnan(nbr_post)

    if nodata is not None:
        mask |= (nbr_pre == nodata) | (nbr_post == nodata) #to exclude no valid data from calculations

    # -------------------------
    # dNBR
    # -------------------------
    dnbr = np.full(nbr_pre.shape, np.nan, dtype=np.float32)
    dnbr[~mask] = nbr_pre[~mask] - nbr_post[~mask]

    # -------------------------
    # RBR (Parks et al. 2014)
    # -------------------------
    rbr = np.full(nbr_pre.shape, np.nan, dtype=np.float32)
    rbr[~mask] = dnbr[~mask] / (nbr_pre[~mask] + 1.001)

    # -------------------------
    # Save outputs
    # -------------------------
    profile.update(
        driver="GTiff",
        dtype=np.float32,
        count=1,
        nodata=np.nan
    )

    with rasterio.open(dnbr_out_path, "w", **profile) as dst:
        dst.write(dnbr, 1)

    with rasterio.open(rbr_out_path, "w", **profile) as dst:
        dst.write(rbr, 1)

    print("dNBR written at:", dnbr_out_path)
    print("RBR written at:", rbr_out_path)


compute_dnbr_rbr(
    nbr_pre_path = r"Outputs\NBR_pre_fire.tif",
    nbr_post_path = r"Outputs\NBR_post_fire.tif",
    dnbr_out_path = r"Outputs\dNBR.tif",
    rbr_out_path = r"Outputs\RBR.tif"
)
