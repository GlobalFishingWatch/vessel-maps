def makeMap(grid,fig_title,fig_min_value,
            fig_max_value, outfile = None, outfolder = '',
            cmap= plt.get_cmap('Reds'), 
            num_levels = 5, 
            firstlat = max_lat,
            lastlat =  min_lat,
            firstlon = min_lon,
            lastlon = max_lon):

    plt.rcParams["figure.figsize"] = [9,7.5]

    firstlat = max_lat
    lastlat =  min_lat
    firstlon = min_lon
    lastlon = max_lon

    numlats = int((firstlat-lastlat)/cellsize+.5)
    numlons = int((lastlon-firstlon)/cellsize+.5)

    lat_boxes = np.linspace(lastlat,firstlat,num=numlats,endpoint=False)
    lon_boxes = np.linspace(firstlon,lastlon,num=numlons,endpoint=False)

    fig = plt.figure()
    extra = 0
    m = Basemap(llcrnrlat=lastlat-extra, urcrnrlat=firstlat+extra,
              llcrnrlon=firstlon-extra, urcrnrlon=lastlon+extra, lat_ts=0, projection='mill',resolution="h")

    m.drawmapboundary()#fill_color='#111111')
    m.fillcontinents('#cccccc',lake_color='#cccccc')#, lake_color, ax, zorder, alpha)

    x = np.linspace(firstlon, lastlon, -(firstlon-lastlon)*one_over_cellsize+1)
    y = np.linspace(lastlat, firstlat, (firstlat-lastlat)*one_over_cellsize+1)
    x, y = np.meshgrid(x, y)
    converted_x, converted_y = m(x, y)
    maximum = fig_max_value # grid.max()
    minimum = fig_min_value #1
    norm = colors.LogNorm(vmin=fig_min_value, vmax=fig_max_value)
#     norm = colors.Normalize

    m.pcolormesh(converted_x, converted_y, grid, norm=norm, vmin=fig_min_value, vmax=fig_max_value, cmap =cmap)# plt.get_cmap('Reds'))

    t = fig_title
    plt.title(t, color = "#000000", fontsize=18)
    ax = fig.add_axes([0.2, 0.1, 0.65, 0.02]) #x coordinate , 
    norm = colors.LogNorm(vmin=minimum, vmax=maximum)
    lvls = np.logspace(np.log10(minimum),np.log10(maximum),num=num_levels)
    cb = colorbar.ColorbarBase(ax,norm = norm, orientation='horizontal', ticks=lvls, cmap = cmap)# plt.get_cmap('Reds'))
    cb.ax.set_xticklabels([int(i) for i in lvls], fontsize=10, color = "#000000")
    cb.set_label('Number of Encounters',labelpad=-40, y=0.45, color = "#000000")
    if outfile:
        plt.savefig(out_folder +outfile+".png",bbox_inches='tight',dpi=300,transparent=True,pad_inches=.1)
    plt.show()