import numpy as np
import pandas as pd

import geopandas as gpd

import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm

import geoplot as gplt
import geoplot.crs as gcrs

from tqdm.auto import tqdm

from rwrap import eurostat

sns.set_context('talk')

df_geo = eurostat.get_eurostat_geospatial(
    output_class='sf', resolution=60, nuts_level=2, year=2016
)
print(df_geo.head())