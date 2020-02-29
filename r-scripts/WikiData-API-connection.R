library(data.table); library(httr); library(jsonlite); library(tidyverse)
df <- fread("data/muratova_res6.csv", encoding = "UTF-8")
# creating target from surname + initials
df$target <- paste(df$адресатИП, df$адресат_ио, sep = " ")
# creating a year
df$year <- paste0(str_extract_all(df$даты, "1\\d+")[[1]], collapse = ";")
# take significant variables
df <- select(df, -"адресат", -"даты", -names(df)[13:19])
names(df) <- c("source", "affiliation", "publish", "year_of_publish", "form_of_publish", "one-two-sided", "personas", "comments", "e-source", "n-letters", "target", "year")
# creating a columns for WikiData IDs
df$source_wkid = NA
df$target_wkid = NA
# cleaning data from multiple authors
tmp <- df[grepl(";", df$source),]
fwrite(tmp, file = "data/multiple_authors.csv"); rm(tmp)
df <- df[!grepl(";", df$source),]
# getting search results from WikiData
## https://www.mediawiki.org/wiki/API:Search

# for sources
for (i in 1:nrow(df)) {
  print(i)
  tmp <- GET("https://www.wikidata.org/w/api.php", 
             query = list(action = "query",
                          list = "search",
                          srsearch = df$source[i],
                          format = "json"))
  tmp <- content(tmp)$query$search
  if (is_empty(tmp)) next
  # collect instances IDs
  tmp_titles = character(); for (j in 1:length(tmp)) {tmp_titles[j] = tmp[[j]]$title}
  titles_parse <- paste(tmp_titles, collapse = "|")
  # get instances info
  ## https://www.wikidata.org/w/api.php?action=help&modules=wbgetentities
  tmp2 <- GET("https://www.wikidata.org/w/api.php", 
              query = list(action = "wbgetentities",
                           ids = titles_parse,
                           languages = "ru",
                           format = "json"))
  tmp2 <- content(tmp2)$entities
  # instance of: human - filter by it
  ids = character(length = length(tmp_titles))
  for (k in 1:length(tmp_titles)) {
    try(if(
      eval(parse(text = str_c("tmp2$", tmp_titles[k], "$claims$P31[[1]]$mainsnak$datavalue$value$id")))=="Q5"
      & as.integer(str_extract(eval(parse(text = str_c("tmp2$", tmp_titles[k], "$claims$P569[[1]]$mainsnak$datavalue$value$time"))), "1\\d+"))+10<=df$year[i]
      & as.integer(str_extract(eval(parse(text = str_c("tmp2$", tmp_titles[k], "$claims$P570[[1]]$mainsnak$datavalue$value$time"))), "1\\d+"))>=df$year[i]
      ) ids[k] = tmp_titles[k], silent = T)
  }
  df$source_wkid[i] <- paste(ids, collapse = ";")
  print("Found")
}

# for targets
for (i in 1:nrow(df)) {
  print(i)
  tmp <- GET("https://www.wikidata.org/w/api.php", 
             query = list(action = "query",
                          list = "search",
                          srsearch = df$target[i],
                          format = "json"))
  tmp <- content(tmp)$query$search
  if (is_empty(tmp)) next
  # collect instances IDs
  tmp_titles = character(); for (j in 1:length(tmp)) {tmp_titles[j] = tmp[[j]]$title}
  titles_parse <- paste(tmp_titles, collapse = "|")
  # get instances info
  ## https://www.wikidata.org/w/api.php?action=help&modules=wbgetentities
  tmp2 <- GET("https://www.wikidata.org/w/api.php", 
              query = list(action = "wbgetentities",
                           ids = titles_parse,
                           languages = "ru",
                           format = "json"))
  tmp2 <- content(tmp2)$entities
  # instance of: human - filter by it
  ids = character(length = length(tmp_titles))
  for (k in 1:length(tmp_titles)) {
    try(if(
      eval(parse(text = str_c("tmp2$", tmp_titles[k], "$claims$P31[[1]]$mainsnak$datavalue$value$id")))=="Q5"
      & as.integer(str_extract(eval(parse(text = str_c("tmp2$", tmp_titles[k], "$claims$P569[[1]]$mainsnak$datavalue$value$time"))), "1\\d+"))+10<=df$year[i]
      & as.integer(str_extract(eval(parse(text = str_c("tmp2$", tmp_titles[k], "$claims$P570[[1]]$mainsnak$datavalue$value$time"))), "1\\d+"))>=df$year[i]
    ) ids[k] = tmp_titles[k], silent = T)
  }
  df$target_wkid[i] <- paste(ids, collapse = ";")
  print("Found")
}

df$source_wkid <- str_extract_all(df$source_wkid, "Q\\d+")
df$target_wkid <- str_extract_all(df$target_wkid, "Q\\d+")
# creating new enriched database
fwrite(df, file = "data/enriched_data.csv")