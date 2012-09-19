
# Example: 
# 
# setwd('~/Documents/projects/cosm')
# world <- readShapePoly('data/maps/TM_WORLD_BORDERS_SIMPL-0.3/TM_WORLD_BORDERS_SIMPL-0.3.shp')
## world <- readShapePoly('data/maps/TM_WORLD_BORDERS_SIMPL-0.3-generalised/TM_WORLD_BORDERS_SIMPL-0.3-generalised.shp', delete_null_obj=TRUE)
# p_geo <- basemap(world)
# 
# d <- read.csv("data/feed_index/feed_index.txt", header=TRUE, sep="\t", blank.lines.skip=TRUE, quote="")
# 
# points <- stratifyLatLon(selectRecordsForTag("radiation", d))
# savePdf(mapPlot(points, p_geo, "Radiation Sensors"), "graphics/maps/map_test.pdf", 15, 10)

library(maps)
library(maptools)
library(mapproj)
library(sp)
library(ggplot2)
library(gridExtra)

gpclibPermit()

stratify <- function(data, latGridSize, lonGridSize=latGridSize, latOffset=0, lonOffset=0) {
  transform(data, 
    Lon = (Lon - lonOffset) - ((Lon - lonOffset) %% lonGridSize) + lonOffset + lonGridSize/2, 
    Lat = (Lat - latOffset) - ((Lat - latOffset) %% latGridSize) + latOffset + latGridSize/2)
}

aggregateByLatLon <- function(data_stratified, FUN=length) {
  aggregate(
      x=data.frame(Count=data_stratified$Count), 
      by=list(Lat=data_stratified$Lat, Lon=data_stratified$Lon), 
      FUN=FUN)
}

basemap <- function(world, size=0.2, fill=I('#ffffff'), col=I('#cccccc')) {
  ggplot(world, aes(long, lat, group=group)) + 
    geom_polygon(size=size, fill=fill, col=col) +
    coord_equal() + 
    # opts(aspect.ratio = 1) + 
    opts(panel.background = theme_blank(), 
      # legend.position = "none",
      panel.grid.minor=theme_blank(), panel.grid.major=theme_blank(), 
      axis.ticks = theme_blank(), axis.text.x = theme_blank(), axis.title.x=theme_blank(), axis.text.y = theme_blank(), axis.title.y=theme_blank())
}

selectRecordsForTag <- function(tagStr, d, tagCol="ALL_TAGS") {
  d[grep(tagStr, d[,tagCol], ignore.case=TRUE),]
}

stratifyLatLon <- function(d, latGridSize=0.02, lonGridSize=latGridSize, latOffset=0, lonOffset=0,FUN=length) {
  mapdata <- subset(d, !is.na(Lat))
  aggregateByLatLon(stratify(mapdata, latGridSize, lonGridSize, latOffset, lonOffset), FUN=FUN)
}

mapPlot <- function(mapPlotData, basemap, xlim=c(-170,170), ylim=c(-56,75), title=NA, units="Datastreams", col='#ff0000', alpha=0.5, scale_range=c(0.3,4), projection="mercator", legend.position="none") {
  mapPlotData <<- mapPlotData # making it global to address a variable scoping bug below

  m <- basemap + 
    geom_point(data=mapPlotData, aes(group=1, x=mapPlotData$Lon, y=mapPlotData$Lat, cex=mapPlotData$Count), col=col, alpha=alpha, type='p', pch=19) +
    scale_area(range=scale_range, name=units) + 
    opts(legend.position=legend.position, panel.margin=unit(0 , "cm"), plot.margin=unit(c(0,0,-1,-1), "lines")) +
    coord_map(project=projection, xlim=xlim, ylim=ylim)
    if (!is.na(title)) {
      m <- m + opts(title=title)
    }
    m
}
  
savePdf <- function(p, pdfFilename, width, height) {
  ggsave(plot=p, filename=pdfFilename, width=width, height=height, units="cm")
}
