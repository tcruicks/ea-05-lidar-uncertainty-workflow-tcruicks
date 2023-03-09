# ea-05-lidar-uncertainty-workflow-tcruicks
Functionalized code to download and analyze LIDAR CHM tree height estimates with insitu observations for two California [NEON](https://www.neonscience.org/) sites.

This code extracts CHM (canopy height model) tree height estimates from LIDAR for two California NEON sites: [SJER](https://www.neonscience.org/field-sites/soap) and [SOAP](https://www.neonscience.org/field-sites/sjer).  The tree height estimates are compared to insitu observations from each study area.  The code establishes a buffer around each insitu measurement plot and extracts the CHM max and mean tree height estimate for the pixels contained inside the buffer zone.  The code then produces a comparison plot and a linear regression model fit for the max and mean tree height stats for the NEON and SOAP study areas.

In it's current form, all functions are imported from external /.py files.  The user can specify via variable either 'soap' or 'sjer' sites and the buffer size in meter.

The data set used is downloaded from the [EarthPy](https://earthpy.readthedocs.io/en/latest/#) package.  The data set is called 'spatial-vector-lidar' and can be found under [EarthPy Data Subsets](https://earthpy.readthedocs.io/en/latest/earthpy-data-subsets.html#)

Author: Tyler Cruickshank
tcruicks@gmail.com
March 2023
