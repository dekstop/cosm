
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

# Takes a list of strings and a data frame of Cosm feed data
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