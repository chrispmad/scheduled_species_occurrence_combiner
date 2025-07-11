gather_occurrence_records_for_pr_sp = function(lan_root, onedrive_wd, data = c("occurrences","species list"), species_list = NA, redo = F, excel_path = ""){
  
  pr_sp = readxl::read_excel(paste0(lan_root,"2 SCIENCE - Invasives/SPECIES/AIS_priority_species.xlsx"),
                             skip = 20)
  
  names(pr_sp) <- c("group","status","name","genus","species")
  
  # If the user provides a reduced list of species (vector of full dataframe with column Species),
  # run for JUST THOSE species; otherwise, run for ALL species in pr_sp excel file.
  if(is.vector(species_list) | is.data.frame(species_list)){
    if(is.vector(species_list) & !is.na(species_list)){
      pr_sp = pr_sp |> 
        dplyr::filter(stringr::str_to_sentence(name) %in% stringr::str_to_sentence(unique(species_list)))
    }
    if(is.data.frame(species_list)){
      pr_sp = pr_sp |> 
        dplyr::filter(stringr::str_to_sentence(name) %in% stringr::str_to_sentence(species_list$Species))
    }
  }
  # if(is.vector(species_list)){
  #   if(is.na(species_list)){
  #     pr_sp = pr_sp
  #   }
  
  # Just for our species of interest.
  pr_sp = pr_sp |>
    dplyr::filter(group == 'Fish' | name %in% c("Whirling disease") | stringr::str_detect(name, '(mussel|crayfish|mystery snail|mudsnail|clam|jellyfish|shrimp|waterflea)')) |> 
    # Split out grouped species names into separate rows.
    dplyr::mutate(name = stringr::str_squish(name)) |>
    dplyr::filter(name != 'Bullhead') |>
    dplyr::arrange(name)
  
  # Add a couple alternate ways of spelling species common names.
  alternate_spellings_tbl = 
    tidyr::tibble(
      group = c('Fish','Fish','Fish','Fish','Other invertebrates','Fish',
                'Other invertebrates','Other invertebrates',
                'Other invertebrates','Other invertebrates',
                'Fish','Fish'),
      status = c('Provincial EDRR','Provincial EDRR','Management','Management','Management','Management',
                 'Provincial Containment','Provincial Containment','Provincial Containment','Management',
                 'Provincial Containment','Prevent'),
      name = c('Oriental weather loach','Rosy red fathead minnow','Pumpkinseed sunfish','Carp','Common Freshwater Jellyfish','Bluegill sunfish',
               'Asian clam','Golden clam','Good luck clam','Asiatic clam','Yellow pickerel',
               'Mosquitofish'),
      genus = c('Misgurnus','Pimephales','Lepomis','Cyprinus','Craspedacusta','Lepomis',
                'Corbicula','Corbicula','Corbicula','Corbicula','Sander','Gambusia'),
      species = c('anguillicaudatus','promelas','gibbosus','carpio','sowerbyi','macrochirus',
                  'fluminea','fluminea','fluminea','fluminea','vitreus','affinis')
    )
  
  pr_sp = pr_sp |> 
    dplyr::bind_rows(
      alternate_spellings_tbl |> 
        dplyr::filter(paste0(genus,species) %in% unique(paste0(pr_sp$genus,pr_sp$species)))
    )
  
  # Ensure species' common names are Sentence case.
  pr_sp$name = stringr::str_to_sentence(pr_sp$name)
  
  if(data == "species list"){
    if("Northern pike" %in% pr_sp$Species){
      pr_sp = remove_native_nPike(pr_sp)
    }
    return(pr_sp)
  } else {
    
    # Do record search for all species of interest! This takes a minute.
    occ_dat_search_results = pr_sp$name |>
      lapply(\(x) {
        tryCatch(grab_aq_occ_data(x, 
                                  excel_path = excel_path),
                 error=function(e)return(NULL))
      })
    
    occ_dat_res_b = dplyr::bind_rows(occ_dat_search_results)
    occ_dat_res_b = dplyr::mutate(occ_dat_res_b, Species = stringr::str_to_sentence(Species))
    
    # Just include records that had coordinates within BC's bounding box.
    occ_dat_res_b = occ_dat_res_b |>
      sf::st_transform(3005) |>
      sf::st_filter(sf::st_as_sfc(sf::st_bbox(dplyr::summarise(bcmaps::bc_bound())))) |>
      sf::st_transform(4326)
    
    # For species with multiple common names, homogenize the names to fit whatever
    # is present in 'priority_species_table.xlsx' file.
    occ_dat_res_b = occ_dat_res_b |>
      dplyr::mutate(Species = dplyr::case_when(
        # Species == 'Oriental weatherfish' ~ 'Oriental weather loach',
        Species == 'Oriental weather loach' ~ 'Oriental weatherfish',
        Species == 'Rosy red fathead minnow' ~ 'Fathead minnow',
        Species == 'Mosquitofish' ~ 'Western mosquitofish',
        Species %in% c('Pumpkinseed sunfish','Pumpkinseed Sunfish') ~ 'Pumpkinseed',
        Species == 'Common freshwater jellyfish' ~ 'Peach blossom jellyfish',
        Species == 'Bluegill sunfish' ~ 'Bluegill',
        Species == 'Yellow pickerel' ~ 'Walleye',
        Species %in% c("Asian clam","Asiatic clam","Golden clam","Good luck clam") ~ 'Freshwater clam',
        Species %in% c("Carp","European Carp","Common Carp") ~ "Common carp",
        T ~ Species
      ))
    
    # In case we've picked up some Asian Carp or other species that
    # we might not actually want because they're not (yet?) in BC, drop those.
    occ_dat_res_b = occ_dat_res_b |>
      dplyr::filter(!Species %in% c("Asian Carp","Grass Carp","Silver Carp","Black Carp",
                                    "Bighead Carp"))
    if("Northern pike" %in% occ_dat_res_b$Species){
      
      occ_dat_res_b = remove_native_nPike(occ_dat_res_b)
    }
    return(occ_dat_res_b)
  }
}


# Write out observations to "J:\2 SCIENCE - Invasives\SPECIES\5_Incidental Observations"
