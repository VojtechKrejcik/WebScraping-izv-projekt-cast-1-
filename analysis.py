#!/usr/bin/env python3.8
# coding=utf-8

from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import os
# muzete pridat libovolnou zakladni knihovnu ci knihovnu predstavenou na prednaskach
# dalsi knihovny pak na dotaz

def trans(df, cols, ratio_req):
    """function to analazy how many times are columns memory cheaper as category"""
    prdellist=[]
    for col in cols:
        og = df[col].memory_usage(deep=True)
        category =df[col].astype('category').memory_usage(deep=True)
        ratio = og/category
        if(ratio > ratio_req):
                print(col, ratio)

#musim pridat nastaveni pro verbose
def get_dataframe(filename: str, verbose: bool = False) -> pd.DataFrame:
    df = pd.read_pickle(filename)
    og_size = df.memory_usage(deep=True).sum()/1048576 #PREVEST na MB
    
    df['date'] = pd.to_datetime(df['p2a'], format='%Y-%m-%d')
    for column in ['p36','p2a', 'weekday(p2a)','p6','j','k','p','q', 't', ]: #here add names of all columns to change to category
        df[column] = df[column].astype('category')
    if verbose:
        tr_size = df.memory_usage(deep=True).sum()/1048576
        print("Original memory usage:", format(og_size, '.1f'), "MB\nOptimized memory usage:",format(tr_size, '.1f'), "MB")    
    return df

# Ukol 2: následky nehod v jednotlivých regionech
def plot_conseq(df: pd.DataFrame, fig_location: str = None, show_figure: bool = False):
    mydf = df[['region','p13a','p13b','p13c']].groupby('region').agg('sum').reset_index()

    fig, axes = plt.subplots(4, 1, figsize=(21, 30))

    fig.suptitle('')

    mydf['sum'] = mydf['p13a'] + mydf['p13b'] + mydf['p13c']

    mydf = mydf.sort_values('sum', ascending=False)
    sns.barplot(ax=axes[0], data=mydf, x='region', y='p13a', color='#90AFC5')
    axes[0].set_ylabel('Umrti pri nehode')
    sns.barplot(ax=axes[1], data=mydf, x='region', y='p13b', color='#336B87')
    axes[1].set_ylabel('Tezce zraneni pri nehode')
    sns.barplot(ax=axes[2], data=mydf, x='region', y='p13c', color='#2A3132')
    axes[2].set_ylabel('lehce zraneni pri nehode')
    sns.barplot(ax=axes[3], data=mydf, x='region', y='sum', color='#763626')
    axes[3].set_ylabel('Celkem')
    plt.savefig(fig_location)

# Ukol3: příčina nehody a škoda
def plot_damage(df: pd.DataFrame, fig_location: str = None, show_figure: bool = False):
    """vypada to, ze ty data jsou obracena v grafu, nemuzu prijit na to proc(po kontrole s vysledkama kolegu)"""
    df['skoda'] = pd.cut(df['p53'].div(10), bins=[0,50, 200, 500, 1000,1000000], labels=['<50', '50-200', '200-500', '500-1000', '> 1000']) 
    df['typ'] = pd.cut(df['p12'], bins=[50,200,300,400,500,600,700], labels=['nezaviněná řidičem', 'nepřiměřená rychlost jízdy', 'nesprávné předjíždění', 'nedání přednosti v jízdě', 'nesprávný způsob jízdy', 'technická závada vozidla'])
    

    fig, axes = plt.subplots(2, 2, figsize=(21, 25))
    fig.suptitle('Nehody dle skody')
    mydf= df[df['region'] == 'JHC']
    sns.barplot(ax=axes[0,0],data=mydf, x='skoda', y='p53', hue='typ') 
    axes[0,0].set(yscale='log',title='JHC')

    mydf= df[df['region'] == 'STC']
    sns.barplot(ax=axes[1,0],data=mydf, x='skoda', y='p53', hue='typ') 
    axes[1,0].set(yscale='log',title='STC')

    mydf= df[df['region'] == 'PHA']
    sns.barplot(ax=axes[0,1],data=mydf, x='skoda', y='p53', hue='typ') 
    axes[0,1].set(yscale='log',title='PHA')

    mydf= df[df['region'] == 'KVK']
    sns.barplot(ax=axes[1,1],data=mydf, x='skoda', y='p53', hue='typ') 
    axes[1,1].set(yscale='log',title='KVK')
    plt.savefig(fig_location)

# Ukol 4: povrch vozovky
def plot_surface(df: pd.DataFrame, fig_location: str = None, show_figure: bool = False):
    #sns.catplot(data=df, x=)
    pass


if __name__ == "__main__":
    pass
    # zde je ukazka pouziti, tuto cast muzete modifikovat podle libosti
    # skript nebude pri testovani pousten primo, ale budou volany konkretni ¨
    # funkce.
    df = get_dataframe("accidents.pkl.gz", verbose=True)
    #pro zjisteni kde ziskam nejvetsi usporu
    # trans(df,['region', 'p1', 'p36', 'p37', 'p2a', 'weekday(p2a)', 'p2b', 'p6', 'p7', 'p8', 'p9', 'p10', 'p11', 'p12', 'p13a', 'p13b', 'p13c', 'p14', 'p15', 'p16', 'p17', 'p18', 'p19', 'p20', 'p21', 'p22', 'p23', 'p24', 'p27', 'p28', 'p34', 'p35', 'p39', 'p44', 'p45a', 'p47', 'p48a', 'p49', 'p50a', 'p50b', 'p51', 'p52', 'p53', 'p55a', 'p57', 'p58', 'a', 'b', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'n', 'o', 'p', 'q', 'r', 's', 't', 'p5a', 'p20', 'p30', 'p31', 'p32'], 2)
    
    plot_conseq(df, fig_location="01_nasledky.png", show_figure=True)
    plot_damage(df, "02_priciny.png", True)
    #plot_surface(df, "03_stav.png", True)
    
