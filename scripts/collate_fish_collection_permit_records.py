#%% 

import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import re  # Regular expressions!
import time
import os
import shutil
import glob
from datetime import datetime
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import random
# Import functions!
import fcp_funcs as fcp_funcs

#%% 
driver = webdriver.Chrome()
url = "https://bcgov.sharepoint.com/sites/WLRS-FDS/Lists/Project%20Registration%20and%20Sub/AllItems.aspx"
driver.get(url)

#%% 
fcp_funcs.login_until_MFA_call(driver)
#%% 
# Do the sign in on your phone!
time.sleep(60)

#%% 
# Are we still on the right website after signing in? If not, go back to it.
if driver.current_url == "https://bcgov.sharepoint.com/":
    driver.get(url=url)
    time.sleep(5)


#%% 
# Filter for just those rows that have attachments!
# attachment_filter_button = driver.find_element(By.ID, 'diidSort0Attachments')
attachment_filter_button = driver.find_elements(By.CLASS_NAME, 'ms-headerSortTitleLink')[1]
attachment_filter_button.click()
time.sleep(2)
# Here's the "Yes" filter button
filter_button_yes = driver.find_element(By.CLASS_NAME,"ms-core-menu-box").find_elements(By.CLASS_NAME,"ms-core-menu-link")[4]
filter_button_yes.click()
time.sleep(1)
try:
    driver.find_element(By.CLASS_NAME,"ms-core-menu-box").find_element(By.ID,'fmi_cls')
    print("Button found!")
    driver.find_element(By.CLASS_NAME,"ms-core-menu-box").find_element(By.ID,'fmi_cls').click()
except:
    print("No close button found - maybe it closed itself!")

# Jot down the URL that includes our filter!
url_with_filter_applied = driver.current_url

#%% 
# Snag table on first page so we can find the total count of projects to download.
table = driver.find_element(By.CLASS_NAME, "ms-listviewtable")  # Adjust this selector if needed
data = []
rows = table.find_elements(By.TAG_NAME, "tr")
total_rows = int(rows[1].text.strip('Count= '))
if rows[1].text.startswith('Count'):
    del rows[1]

remake_df_master = False

# Get full list of project names (on the page we are on).
# This is redone if we ever want to start this project from scratch.
project_titles = []
for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        project_titles.append([col.text for col in cols[:2]])
# Clean up project titles.
project_titles = pd.DataFrame(project_titles)
project_titles = project_titles.iloc[1:, 1]

# Look for master tracker .csv file. If it exists, read it in. If it doesn't, create it here.
if glob.glob('../data/fish_permit_collections_projects_and_downloads_tracker.csv'):
    print("Master tracker .csv file located.")
    master_tracker = pd.read_csv('../data/fish_permit_collections_projects_and_downloads_tracker.csv')
else:
    master_tracker = pd.DataFrame({
        'project_title': project_titles,
        'has_been_downloaded': False
    })

# Download excel files for all projects without files yet in Downloads folder.
row_number = 0
page_counter = 1
total_counter = 1
current_page = 1

while total_counter < total_rows:

    for row in rows:
        # Random wait time.
        time.sleep(random.randrange(1,3) / 2)
        print("Currently on row " + str(row_number+1))

        the_project_name = master_tracker.iloc[row_number]["project_title"]
        row_already_downloaded = master_tracker.iloc[row_number]['has_been_downloaded']

        # Check to see if this project title is present in the master tracker. If not, add the row!
        project_already_in_master_tracker = sum(master_tracker['project_title'].str.contains(the_project_name)) > 0
        
        if project_already_in_master_tracker == False:
            new_row_for_master_tracker = pd.DataFrame({'project_title': [the_project_name], 'has_been_downloaded': False})
            master_tracker =pd.concat([new_row_for_master_tracker, master_tracker], ignore_index=True)

        # The following paragraph finds excel files and downloads them, renames them and then moves them to 
        # the data folder in the project "scheduled_species_occurrence_combiner".
        if row_already_downloaded == False:
            project_link = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT,the_project_name)))
            project_link.click()
            time.sleep(1)
            # Find the iframe for the dialogue box.
            iframe_with_excel = driver.find_element(By.CLASS_NAME,"ms-dlgFrame")
            driver.switch_to.frame(iframe_with_excel)
            time.sleep(1.5)
            # Is there any excel file here to be mined?
            excel_files = driver.find_elements(By.XPATH, "//a[contains(@href, '.xls')]")
            time.sleep(0.5)
            if excel_files:
                #fcp_funcs.download_excel_if_possible(driver,excel_files)
                download_excel_if_possible(driver,excel_files)
            
            # Return to Filtered SharePoint page.
            driver.get(url_with_filter_applied)

            # Rename the file we just downloaded.
            latest_file = max(glob.glob("C:/Users/CMADSEN/Downloads/*xlsx"), key = os.path.getctime)

            if latest_file:
                new_filename = "C:/Users/CMADSEN/Downloads/" + the_project_name + ".xlsx"
                os.rename(latest_file, new_filename)
                # Move the file to the proper folder.
                shutil.move(src = new_filename,
                            dst = "C:/Users/CMADSEN/Downloads/LocalR/long_term_projects/scheduled_species_occurrence_combiner/data/fish_collection_permit_excel_files/" + the_project_name + '.xlsx')

            # Do we have a downloaded file with the proper name in scheduled_species_occurrence_combiner?
            if glob.glob("C:/Users/CMADSEN/Downloads/LocalR/long_term_projects/scheduled_species_occurrence_combiner/data/fish_collection_permit_excel_files/" + the_project_name + '.xlsx'):
                print("File successfully downloaded and saved to proper folder.")
                master_tracker.iloc[row_number,1] = True
        
        master_tracker.to_csv('../data/fish_permit_collections_projects_and_downloads_tracker.csv', index=False)
        row_number += 1
        total_counter += 1
        time.sleep(1.5)

    if page_counter == 100:
        print("Clicking button for next page!")
        next_page_button = driver.find_element(By.XPATH,'//*[@title="Next"]')
        next_page_button.click()
        current_page += 1
        time.sleep(3)
        page_counter = 1

        table = driver.find_element(By.CLASS_NAME, "ms-listviewtable")  # Adjust this selector if needed
        data = []
        rows = table.find_elements(By.TAG_NAME, "tr")
        if rows[1].text.startswith('Count'):
            del rows[1]
        project_titles = []
        for row in rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                project_titles.append([col.text for col in cols[:2]])
        # Clean up project titles.
        project_titles = pd.DataFrame(project_titles)
        project_titles = project_titles.iloc[1:, 1]
    # Have we finished all 100 on this page?




















df_master = pd.read_csv('../data/fish_permit_collections_projects.csv')

#%% 
# Should we read in the master dataframe, if it already exists, rather than remaking it?
if remake_df_master == False & os.path.isfile('../data/fish_permit_collections_projects.csv'):
    df_master = pd.read_csv('../data/fish_permit_collections_projects.csv')
    # Drop index rows!
    df_master = df_master[df_master.columns[~df_master.columns.str.contains("Unnamed")]]
    # Drop duplicate rows of projects, if any.
    df_master = df_master.drop_duplicates(subset='col_1', keep='first')
    # Are there any new rows that aren't in our df_master?
    print("Combining rows of first page's results to test if any rows are new to our master dataframe")
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        data.append([col.text for col in cols])
    df = pd.DataFrame(data)
    print("We've made the pandas dataframe for page 1 of results")
    df_new_rows = df[~df[1].isin(df_master["col_1"])]
    df_new_rows = df_new_rows.dropna(subset=[1])
    df_new_rows = df_new_rows[~df_new_rows[1].str.contains("Count")]
    # Update column names.
    df_new_rows['downloads_checked'] = False
    df_new_rows = df_new_rows.drop(columns=df_new_rows.columns[0])
    df_new_rows.columns = df_master.columns
    df_master = pd.concat([df_new_rows, df_master], ignore_index=True)
    df_master.to_csv('../data/fish_permit_collections_projects.csv')
    

#%% 
# Check that we are on the proper page (maybe unnecessary)
if driver.current_url != url_with_filter_applied:
    driver.get(url_with_filter_applied)
    time.sleep(1)
current_row_across_pages = 0
current_page = 1
# While there's still total rows to fill in...
while current_row_across_pages < total_rows:

    # Grab all the table bits, pandify them to a dataframe, append to our df_master dataframe.
    table = driver.find_element(By.CLASS_NAME, "ms-listviewtable")
    # table = driver.find_element(By.ID, "Hero-WPQ1")
    data = []
    rows = table.find_elements(By.TAG_NAME, "tr")
    # Remove first row if it's just the row count.
    if rows[1].text.startswith('Count'):
        del rows[1]
    number_rows = 0
    for row in rows:
        number_rows += 1
        cols = row.find_elements(By.TAG_NAME, "td")
        data.append([col.text for col in cols])
    print("Finished counting up number of rows for page " + str(current_page) + "'s results")
    df = pd.DataFrame(data)
    print("We've made the pandas dataframe for page " + str(current_page) + " of results")
    
    df = df.drop(columns=df.columns[0])
    df.columns = [f"col_{i+1}" for i in range(df.shape[1])]
    df = df[~df["col_1"].isin(["None"])]  # Remove rows where col_1 is exactly "None"
    df = df.dropna(subset=["col_1"])  # Drop rows where col_1 is NA (null values)
    # initialize a column to track which rows have been checked for their excel download.
    df['downloads_checked'] = False
    df = df[~df["col_1"].isin(df_master["col_1"])] # Ensure we don't already have any of these projects in 
    # the df_master table.
    if current_row_across_pages == 0 & remake_df_master == True:
        df_master = df
        print("We've initialized a new 'df_master'")
    else:
        df_master = pd.concat([df_master,df])
        print("We've appended a new page's results to df_master")

    df_master.to_csv("../data/fish_permit_collections_projects.csv")

    current_row = 0
    # Download all links on a given SharePoint page.
    for row in rows:
        # Update tracker numbers
        current_row += 1
        current_row_across_pages += 1
        # Random wait time.
        time.sleep(random.randrange(1,3) / 2)
        print("Currently on row " + str(current_row_across_pages) + ' of ' + str(total_rows))

        project_name = df_master.iloc[current_row-1]["col_1"]
        row_already_downloaded = df_master.iloc[current_row-1]['downloads_checked']

        if row_already_downloaded == False:
            project_link = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT,project_name)))
            project_link.click()
            time.sleep(1)
            # Find the iframe for the dialogue box.
            iframe_with_excel = driver.find_element(By.CLASS_NAME,"ms-dlgFrame")
            driver.switch_to.frame(iframe_with_excel)
            time.sleep(1.5)
            # Is there any excel file here to be mined?
            excel_files = driver.find_elements(By.XPATH, "//a[contains(@href, '.xls')]")
            time.sleep(0.5)
            if excel_files:
                fcp_funcs.download_excel_if_possible(driver,excel_files)
            df_master.loc[current_row_across_pages-1,'downloads_checked'] = True
            df_master.to_csv("../data/fish_permit_collections_projects.csv")
            # Return to Filtered SharePoint page.
            driver.get(url_with_filter_applied)
        time.sleep(1.5)
        
    # Have we finished the final row of this page in SharePoint? If so, click on the 
    # next page button to load up more projects.
    if current_row == number_rows & current_row_across_pages < total_rows:
        print("Clicking button for next page!")
        next_page_button = driver.find_element(By.XPATH,'//*[@title="Next"]')
        next_page_button.click()
        current_page += 1
        time.sleep(1)
# %%
 