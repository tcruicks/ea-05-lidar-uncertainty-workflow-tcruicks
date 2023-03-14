import os
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterstats as rs
import xarray as xr
import rioxarray as rxr

class Processing:

    def __init__(self, study_site, lidar_pth, insitu_pth, plots_pth, buf_size):

        self.study_site = study_site
        self.lidar_pth = lidar_pth
        self.insitu_pth = insitu_pth
        self.plots_pth = plots_pth
        self.buf_size = buf_size

    def lidar_stats(self, plot_buffer_path):

        lidar_chm = rxr.open_rasterio(self.lidar_pth, masked=True).squeeze()
        # Clean up the lidar file.
        lidar_chm_clean = lidar_chm.where(lidar_chm > 0, np.nan)

        lidar_chm_stats = rs.zonal_stats(
            plot_buffer_path,
            lidar_chm_clean.values,
            stats=['mean', 'max'],
            affine=lidar_chm_clean.rio.transform(),
            geojson_out=True, nodata=0, copy_properties=True,
        )
        # Stick it in a dataframe.
        lidar_chm_stats_gdf = gpd.GeoDataFrame.from_features(lidar_chm_stats)

        # Rename df columns.
        lidar_chm_stats_gdf.rename(
            columns={'max': 'lidar_max',
                     'mean': 'lidar_mean', 'ID': 'Plot_ID'},
            inplace=True
        )

        return (lidar_chm_clean, lidar_chm_stats_gdf)

    def insitu_stats(self):

        insitu_gdf = gpd.read_file(self.insitu_pth)

        # Reduce the columns to only what we need.
        insitu_gdf = (insitu_gdf[
            ["siteid", "sitename", "plotid", "stemheight", "scientificname"]])

        # This solves an oddity.  The 'stemheight' column is not coming out as numeric.
        # We need to change the datatype to a float.  As a float .mean and .max will work.
        insitu_gdf["stemheight"] = pd.to_numeric(
            insitu_gdf["stemheight"], downcast="float")

        # Create a df to include max and mean height.
        insitu_stem_height_df = (insitu_gdf.groupby(
            'plotid')['stemheight'].agg(['max', 'mean']))

        # Rename column names to be more explanatory/
        insitu_stem_height_df.rename(
            columns={"mean": "insitu_mean", "max": "insitu_max"},
            inplace=True
        )

        # The index is plotid but we just want 0 ... 9 ...
        insitu_stem_height_df = insitu_stem_height_df.reset_index()
        insitu_stem_height_df.head()

        return (insitu_stem_height_df)

    def buffer(self):

        # Open sjer plot location file.
        plots_gdf = gpd.read_file(self.plots_pth)
        # reset the geometry to the buffer version.
        plots_gdf.geometry = plots_gdf.geometry.buffer(self.buf_size)
        plots_gdf.head()

        # Name and location of the buffered insitu measurement sites.

        # Create an output dir for created files.
        output_path = os.path.join(os.getcwd(), 'outputs')
        if not os.path.isdir(output_path):
            os.makedir(output_path)

        plot_buffer_path = os.path.join(output_path, "plot_buffer.shp")
        # Create the buffered file.
        plots_gdf.to_file(plot_buffer_path)

        return (plots_gdf, plot_buffer_path)

    def merge(self, lidar_stats_gdf, insitu_stats_df):

        # Merge insitu stats df with LIDAR stats df.

        # For SOAP data, the ID columns doesnt match.
        # The Lidar file column needs 'SOAP' appended.
        if (self.study_site == 'soap'):
            ss = self.study_site.upper()
            lidar_stats_gdf['Plot_ID'] = ss + lidar_stats_gdf['Plot_ID']

        # Merge the two stats gdfs to create a master gdf.
        # Will use this gdf to plot from.
        all_heights_gdf = lidar_stats_gdf.merge(
            insitu_stats_df,
            left_on='Plot_ID',
            right_on='plotid')

        return (all_heights_gdf)
