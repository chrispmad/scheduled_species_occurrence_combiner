library(tidyverse)
library(dplyr)
library(sf)
library(bcinvadeR)
lan_root = "//SFP.IDIR.BCGOV/S140/S40203/WFC AEB/General/"
proj_wd = getwd()
onedrive_wd = "//SFP.IDIR.BCGOV/S140/S40203/WFC AEB/General/2 SCIENCE - Invasives/AIS_R_Projects/LargeDataFiles/CNF/"

common_names<-"Northern Pike"
# not what we need
fish_occs<-grab_aq_occ_data("Northern Pike")

common_names = c(stringr::str_to_lower(common_names),
                 stringr::str_to_sentence(common_names),
                 stringr::str_to_title(common_names),
                 stringr::str_to_upper(common_names),
                 paste0(common_names,' '))


#lets query each one individually, first FDIS
common_names_title = common_names
cql_query = stringr::str_squish(paste0('SPECIES_NAME LIKE ',paste0("'",common_names_title,"'", collapse = ' or SPECIES_NAME LIKE ')))

bcg_records = bcdata::bcdc_query_geodata('aca81811-4b08-4382-9af7-204e0b9d2448') |>
  # bcdata::filter(SPECIES_NAME %in% common_names) |>
  bcdata::filter(bcdata:::CQL(cql_query)) |>
  #bcdata::filter(POINT_TYPE_CODE == 'Observation') |>
  # bcdata::filter(bcdata:::CQL("SPECIES_NAME LIKE '% shad' OR SPECIES_NAME LIKE '% shad %'")) |>
  bcdata::collect() |>
  #sf::st_transform(crs = output_crs) |>
  #dplyr::select(Date = 'OBSERVATION_DATE', Species = 'SPECIES_NAME', Location = 'GAZETTED_NAME') |>
  dplyr::mutate(DataSource = 'BCG fish layer') |>
  #dplyr::mutate(Date = as.character(Date)) |>
  dplyr::select(DataSource, dplyr::everything()) 

ids = bcg_records |> 
  dplyr::filter(OBSERVATION_DATE == "2003-01-01")

ids_reduced = ids |> 
  select(DataSource,OBSERVATION_DATE,POINT_TYPE_CODE, FISH_OBSERVATION_POINT_ID, SOURCE, SOURCE_REF)


## now the old fish layer


id2 = bcg_records |> 
  dplyr::filter(OBSERVATION_DATE == "2010-10-16")




cql_query = stringr::str_squish(paste0('ENGLISH_NAME LIKE ',paste0("'",common_names_title,"'", collapse = ' or ENGLISH_NAME LIKE ')))

old_fish = bcdata::bcdc_query_geodata('d9613096-b2fe-43b4-9be1-d82a3b805082') |>
  # bcdata::filter(ENGLISH_NAME %in% common_names) |>
  bcdata::filter(bcdata:::CQL(cql_query)) |>
  bcdata::collect() |>
  #sf::st_transform(crs = output_crs) |>
  dplyr::mutate(Species = stringr::str_to_title(ENGLISH_NAME)) |>
  dplyr::mutate(Location = ifelse(is.na(BCGNIS_NAME),LOCATION_INFORMATION,stringr::str_to_title(BCGNIS_NAME))) |>
  #dplyr::select(Species, Date = COLLECTION_DATE, Location) |>
  #dplyr::mutate(Date = as.character(Date)) |>
  dplyr::mutate(DataSource = 'Old BCG AIS layer') |>
  dplyr::select(DataSource, dplyr::everything())


old_fish_date = old_fish |> 
  dplyr::filter(COLLECTION_DATE == "2010-10-16")


write.csv(old_fish_date, "./output/northern_pike_old_fish_layer.csv") 
