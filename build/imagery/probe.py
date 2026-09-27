import os,rasterio,time
os.environ['CURL_CA_BUNDLE']='/root/.ccr/ca-bundle.crt'
os.environ['GDAL_DISABLE_READDIR_ON_OPEN']='EMPTY_DIR'
t=time.time()
u='/vsicurl/https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/33/U/XP/2023/7/S2A_33UXP_20230706_0_L2A/TCI.tif'
with rasterio.open(u) as r:print(r.crs,r.bounds,r.overviews(1),r.shape)
u='/vsicurl/https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_N48E015_Map.tif'
with rasterio.open(u) as r:print(r.crs,r.bounds,r.overviews(1),r.shape)
print(time.time()-t)
