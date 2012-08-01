
# To use:
# setwd("/Users/mongo/Documents/projects/cosm/data/timeseries-hetzner/2012-03-01")
# tsPlot("_test.txt", "_test.pdf")

library(ggplot2)
library(grid)

# load data
loadData <- function (filename) {
  d <- read.csv(filename, header=FALSE, sep="\t", blank.lines.skip=TRUE, quote="", 
    col.names=c("ENVID", "STREAMID", "TIME", "VALUE"),
    colClasses=c("character", "character", "character", "character"))
  d$ID <- paste(d$ENVID, ".", d$STREAMID, sep="")
  d$TIME <- as.POSIXct(d$TIME, format="%Y-%m-%dT%H:%M:%S.%OS")
  d$VALUE <- as.double(d$VALUE)
  d
}

replaceNaValues <- function(d, valueCol, repValueCol, aggregationFunc) {
  # For all NA values: replace with mean
  d[,repValueCol] <- d[,valueCol]
  # Get IDs with missing data
  naIndex <- is.na(d[,repValueCol])
  naId <- unique(d[naIndex,]$ID)
  # Compute the mean of all other data points for the same ID
  nnaData <- d[d$ID %in% naId & !is.na(d[,repValueCol]),]
  naValue <- tapply(nnaData[,repValueCol], factor(nnaData$ID), aggregationFunc)
  # For IDs which only have NAs: substitute "0" as default value
  naValue[naId] <- naValue[naId]
  naValue[is.na(naValue[naId])] <- 0

  # Apply
  d[naIndex,repValueCol] <- naValue[d[naIndex,]$ID]
  d
}

tsPlot <- function(dataFilename, pdfFilename) {
  d <- loadData(dataFilename)
  # set some NA values to test
  # d[1,]$VALUE <- NA
  d <- replaceNaValues(d, "VALUE", "FIXED_VALUE", mean)

  # plot with lots of decoration and spacing
  # p <- ggplot(data = d, aes(x = TIME, y = FIXED_VALUE, facets = ID, color=is.na(VALUE))) + 
  #   geom_point(aes(shape=is.na(VALUE))) + 
  #   theme_bw() + 
  #   scale_colour_manual(values=c("black", "red")) + 
  #   scale_shape_manual(values=c(16,4)) +
  #   facet_grid(ID ~ ., scales = "free") + 
  #   opts(axis.title.x = theme_blank(), axis.title.y = theme_blank(), 
  #   axis.text.x = theme_text(size = 5), axis.text.y = theme_text(size = 5),
  #   legend.position = "none")

  # plot a very plain style, no borders
  p <- ggplot(data = d, aes(x = TIME, y = FIXED_VALUE, facets = ID, color=is.na(VALUE))) + 
    geom_point(aes(shape=is.na(VALUE)), size=1) + 
    theme_bw() + 
    scale_colour_manual(values=c("black", "red")) + 
    scale_shape_manual(values=c(16,4)) +
    scale_y_continuous(breaks=NULL, expand=c(0.4, 0)) +
    facet_grid(ID ~ ., scales = "free") + 
    opts(
      axis.title.x = theme_blank(), axis.title.y = theme_blank(), 
      legend.position = "none", 
      axis.text.x=theme_text(size = 5), axis.text.y=theme_blank(),
      strip.text.y = theme_text(size = 5, angle = 270, face = 'bold'),
      strip.background = theme_blank(),
      panel.border = theme_blank(), panel.margin=unit(0 , "lines"),
      title="Sensor Data Feeds")
  
  ggsave(plot=p, filename=pdfFilename, width=15, height=length(unique(d$ID)), units="cm")
  
  # p
}

# scale_size_manual(values=c(1, 2, 3)) +
# axis.ticks = theme_blank(), 
# panel.grid.minor=theme_blank(), panel.grid.major=theme_blank()
# panel.border = theme_rect(colour="black",size=0.1))
