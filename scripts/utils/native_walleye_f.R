remove_native_walleye <- function(x) {
  # Load native range polygons
  walleye_native_range <- bcdata::bcdc_query_geodata("eaubc-ecological-drainage-units") |>
    bcdata::filter(ECO_DRAINAGE_UNIT %in% c("Upper Liard", "Lower Liard", "Hay", "Lower Peace")) |>
    bcdata::collect() |>
    sf::st_transform(4326)
  
  # Ensure same CRS
  x <- sf::st_transform(x, 4326)
  
  # Identify which Walleye are inside the native range
  is_walleye <- x$Species == "Walleye"
  inside_native <- rep(FALSE, nrow(x))
  inside_native[is_walleye] <- sf::st_intersects(x[is_walleye, ], walleye_native_range, sparse = FALSE)[,1]
  
  # Keep all non-Walleye, and Walleye outside native range
  x_filtered <- x[!inside_native, ]
  
  return(x_filtered)
}