
# Takes a nested list of arrays.
# Returns a flattened list.
flatten <- function(nestedArray) {
  do.call("c", nestedArray)
}

# Takes an array.
# Returns an unsorted histogram of array values.
# (This also works with string arrays.)
histogram <- function(values) {  
  tapply(values, values, length)
}

# Takes a list of strings.
# Returns a ranked histogram of array values (after converting to lowercase.)
rankTags <- function(values) {  
  sort(histogram(tolower(values)), decreasing=TRUE)
}

# Takes a nested list of arrays.
# Returns a ranked histogram of array values (after converting to lowercase.)
rankTagArrays <- function(nestedArray) {  
  sort(histogram(tolower(flatten(nestedArray))), decreasing=TRUE)
}

# takes a string and a ranked list of values, returns matching value names
grepRankedValues <- function(str, rankedString) {
  unique(names(rankedString[grep(str, names(rankedString), ignore.case=TRUE)]))
}

# takes a list of strings and a ranked list of values, returns matching value names
grepMultipleRankedValues <- function(strings, rankedStrings) {
  t <- c()
  for (str in strings) {
    t <- c(t, grepRankedValues(str, rankedStrings))
  }
  t
}

# Takes a list of values and a data frame of Cosm feed data. Only returns rows where the cell value matches perfecly.
subsetMultiple <- function(df, valCol, values, ignore.case=FALSE) {
  t <- c()
  for (val in values) {
    if (ignore.case==TRUE) {
      t <- unique(c(t, which(tolower(df[,valCol])==tolower(val))))
    } else {
      t <- unique(c(t, which(df[,valCol]==val)))
    }
  }
  df[t,]
}

# Takes a list of strings and a data frame of Cosm feed data.
# Does perfect string matching on a tag column (an array of strings.)
# Also works if cell values are nested arrays.
subsetCosmTags <- function(df, valCol, values) {
  t <- rep(FALSE, nrow(df))
  for (val in values) {
    t = t | unlist(lapply(df[,valCol], function(x){val %in% x}))
  }
  df[t,]
}

# Takes a list of strings and a data frame of Cosm feed data.
# Does partial and case insensitive matching on cell values.
# Also works if cell values are nested arrays.
grepCosmTags <- function(tags, df, tagCol="ALL_TAGS") {
  # t <- df[0:0,]
  t <- c()
  for (tag in tags) {
   # t <- merge(t, df[grep(tag, df[,tagCol], ignore.case=TRUE), ], all=TRUE)
    # t <- rbind(t, df[grep(tag, df[,tagCol], ignore.case=TRUE), ])
    # don't include rows that we already picked
    t <- unique(c(t, grep(tag, df[,tagCol], ignore.case=TRUE)))
  }
  df[t,]
}