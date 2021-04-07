#!/usr/bin/python3.8
# coding=utf-8
# autor: Vojtech Krejcik
# login: xkrejc68
# email: xkrejc68@vutbr.cz

import pandas as pd
import geopandas
import matplotlib.pyplot as plt
import contextily as ctx
import sklearn.cluster
import numpy as np
from collections import Counter
# muzeze pridat vlastni knihovny


def make_geo(df: pd.DataFrame) -> geopandas.GeoDataFrame:
    """ Konvertovani dataframe do geopandas.GeoDataFrame
    se spravnym kodovani"""
    df = df.dropna(subset=["d"])
    df = df.dropna(subset=["e"])
    return geopandas.GeoDataFrame(df, geometry=geopandas.points_from_xy(df["d"], df["e"]), crs="EPSG:5514")


def plot_geo(gdf: geopandas.GeoDataFrame, fig_location: str = None,
             show_figure: bool = False):
    """ Vykresleni grafu s dvemi podgrafy podle toho zda nehoda
     byla v obci, nebo mimo obec (v obou pripadech v jihomoravskem kraji). """

    _, axes = plt.subplots(1, 2, figsize=(20, 15))
    gdf[gdf["region"] == 'JHM'][gdf["p5a"] == 1].plot(ax=axes[0], markersize=0.1)
    ctx.add_basemap(axes[0], crs=gdf.crs.to_string(), source=ctx.providers.Stamen.TonerLite, zoom=10)
    axes[0].axis("off")
    axes[0].set_xlim([-670000, -520000])
    axes[0].set_ylim([-1220000, -1100000])
    axes[0].title.set_text("Nehody v obci v jihomoravskem kraji")

    gdf[gdf["region"] == 'JHM'][gdf["p5a"] == 2].plot(ax=axes[1], markersize=0.1)
    ctx.add_basemap(axes[1], crs=gdf.crs.to_string(), source=ctx.providers.Stamen.TonerLite, zoom=10)
    axes[1].axis("off")
    axes[1].set_xlim([-670000, -520000])
    axes[1].set_ylim([-1220000, -1100000])
    axes[1].title.set_text("Nehody mimo obec v jihomoravskem kraji")

# ukladani/zobrazeni grafu
    if fig_location is not None:
        plt.savefig(fig_location)

    if show_figure:
        plt.show()


def plot_cluster(gdf: geopandas.GeoDataFrame, fig_location: str = None,
                 show_figure: bool = False):
    """ Vykresleni grafu s lokalitou vsech nehod v jihomoravskem
    kraji shlukovanych do  9 clusteru """
    gdf = gdf[gdf["region"] == 'JHM']

    plt.figure(figsize=(20, 15))
    ax = plt.gca()
    gdf = gdf.set_geometry(gdf.centroid)
    gdf = gdf.to_crs("epsg:3857")
    # vyplotovani vsech nehod do grafu
    gdf.plot(ax=ax, color="grey", markersize=0.5)

    # ypocet kmeans algoritmu pro 9 clusteru s max 300 iteracemi
    coords = np.dstack([gdf.geometry.x, gdf.geometry.y]).reshape(-1, 2)
    kmeans = sklearn.cluster.KMeans(n_clusters=9).fit(coords)

    clusters = geopandas.GeoDataFrame(geometry=geopandas.points_from_xy(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1]))
    # pridani sloupce s clustery do dataframu
    gdf["cluster"] = kmeans.labels_
    gdf = gdf.dissolve(by="cluster", aggfunc={"p1": "count"})
    gdf = gdf.merge(clusters, left_on="cluster", right_index=True).set_geometry("geometry_y")

    # plotovani clusteru a omezeni os
    gdf.plot(ax=ax, markersize=gdf["p1"]*0.8, column="p1", legend=True, alpha=0.5)
    ax.set_title("Nehody v Jihomoravskem kraji")
    ax.axis("off")
    ax.set_ylim([6220000, 6380000])
    ax.set_xlim([1735000, 1970000])
    # mapovy podklad
    ctx.add_basemap(ax, crs="epsg:3857", source=ctx.providers.Stamen.TonerLite, zoom=10, alpha=0.9)

    # ukladani/zobrazeni grafu
    if fig_location is not None:
        plt.savefig(fig_location)

    if show_figure:
        plt.show()


if __name__ == "__main__":
    # zde muzete delat libovolne modifikace
    gdf = make_geo(pd.read_pickle("accidents.pkl.gz"))
    plot_geo(gdf, "geo1.png", True)
    plot_cluster(gdf, "geo2.png", True)
