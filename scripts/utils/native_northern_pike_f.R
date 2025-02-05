remove_native_nPike<-function(x){
  bc_watersheds <- sf::st_read(paste0(onedrive_wd,"CNF/watershed_groups.gpkg"), quiet = TRUE)
  bc_watersheds <- bc_watersheds |> sf::st_transform(4326)
  pike_watersheds<- bc_watersheds |> 
    dplyr::filter(stringr::str_detect(WATERSHED_GROUP_NAME, c("Peace|Liard|Yukon|Alsek|Taku|Makenzie")))
  bbox <- sf::st_bbox(pike_watersheds)
  
  x <- x %>%
    dplyr::mutate(X = sf::st_coordinates(.)[,1],  # Extract longitude
           Y = sf::st_coordinates(.)[,2]) %>%  # Extract latitude
    dplyr::filter(!(Species == "Northern pike" & Y > bbox["ymin"] & X > bbox["xmin"])) %>%
    dplyr::select(-X, -Y)  # Remove temporary columns  
  rm(bc_watersheds, pike_watersheds, bbox)
  return(x)
}


