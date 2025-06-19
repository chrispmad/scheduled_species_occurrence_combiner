# Read in function that does all this stuff.
source("scripts/utils/gather_occurrence_records_for_pr_sp.R")
source("scripts/utils/native_northern_pike_f.R")
library(dplyr)
library(bcinvadeR)
# Set up folder paths
lan_root = "//SFP.IDIR.BCGOV/S140/S40203/WFC AEB/General/"
proj_wd = getwd()
onedrive_wd = paste0(stringr::str_extract(getwd(),"C:/Users/[A-Z]+/"),"OneDrive - Government of BC/data/")

occs = gather_occurrence_records_for_pr_sp(
  lan_root = lan_root,
  onedrive_wd = onedrive_wd,
  data = "occurrences",
  redo = T,
  excel_path = paste0(lan_root,"2 SCIENCE - Invasives/SPECIES/5_Incidental Observations/Master Incidence Report Records.xlsx")
)

# Ensure date column is properly formatted for all rows!
occs = occs |> 
  dplyr::mutate(Date = ifelse(stringr::str_detect(Date,"^[0-9]{5}$"), 
                              as.character(openxlsx::convertToDate(Date)),
                              Date))

# Write out observations to LAN folder.
sf::write_sf(
  occs,
  paste0(lan_root,"2 SCIENCE - Invasives/SPECIES/5_Incidental Observations/AIS_occurrences_all_sources.gpkg")
)
