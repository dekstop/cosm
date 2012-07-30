
# Example: 
# 
# setwd('~/Documents/projects/cosm/data')
# world <- readShapePoly('maps/TM_WORLD_BORDERS_SIMPL-0.3/TM_WORLD_BORDERS_SIMPL-0.3.shp')
## world <- readShapePoly('maps/TM_WORLD_BORDERS_SIMPL-0.3-generalised/TM_WORLD_BORDERS_SIMPL-0.3-generalised.shp', delete_null_obj=TRUE)
# p_geo <- basemap(world)
# 
# d <- read.csv("feed_index/feed_index.txt", header=TRUE, sep="\t", blank.lines.skip=TRUE, quote="")
# 
# savePdf(mapPlot(prepareCosmData(d, "radiation"), p_geo, "Radiation Sensors"), "feed_index/map_test.pdf", 15, 10)

library(maps)
library(maptools)
library(mapproj)
library(sp)
library(ggplot2)
library(gridExtra)

gpclibPermit()

stratify <- function(data, grid, offset=0) {
	transform(data, 
		Lon = (Lon - offset) - ((Lon - offset) %% grid) + offset, 
		Lat = (Lat - offset) - ((Lat - offset) %% grid) + offset)
}

stratified_hist <- function(data_stratified) {
	h = aggregate(
		data.frame(Lat=data_stratified$Lat, Lon=data_stratified$Lon), 
		list(SLat=data_stratified$Lat, SLon=data_stratified$Lon), 
		length)
	data.frame(Lat=h$SLat, Lon=h$SLon, Count=h$Lat)
}

basemap <- function(world) {
  ggplot(world, aes(long, lat, group=group)) + 
		geom_polygon(size=0.2, fill=I('#ffffff'), col=I('#bbbbbb')) +
  	coord_equal() + 
  	# opts(aspect.ratio = 1) + 
  	opts(panel.background = theme_blank(), 
      # legend.position = "none",
  		panel.grid.minor=theme_blank(), panel.grid.major=theme_blank(), 
  		axis.ticks = theme_blank(), axis.text.x = theme_blank(), axis.title.x=theme_blank(), axis.text.y = theme_blank(), axis.title.y=theme_blank())
}

prepareCosmData <- function(d, tagStr) {
  mapdata <- d[grep(tagStr, d$JOINED_TAGS, ignore.case=TRUE),]
  mapdata <- subset(mapdata, !is.na(LAT))
  mapdata$Lat <- mapdata$LAT
  mapdata$Lon <- mapdata$LON
  stratified_hist(stratify(mapdata, 0.02))
}

mapPlot <- function(mapdata, basemap, title) {
  mapdata <<- mapdata # making it global to address a variable scoping bug below
  
  basemap + 
    geom_point(data=mapdata, aes(group=1, x=mapdata$Lon, y=mapdata$Lat, cex=mapdata$Count), col='#ff0000', alpha=0.5, type='p', pch=19) +
		scale_size(range=c(0.3,4), name="Sensors") +
    coord_map(project="mercator", xlim=c(-170,170), ylim=c(-55,70)) +
		opts(title=title)
    # coord_cartesian(xlim=c(min(mapdata$Lon), max(mapdata$Lon)), ylim=c(min(mapdata$Lat), max(mapdata$Lat)))
}
  
savePdf <- function(p, pdfFilename, width, height) {
  ggsave(plot=p, filename=pdfFilename, width=width, height=height, units="cm")
}
