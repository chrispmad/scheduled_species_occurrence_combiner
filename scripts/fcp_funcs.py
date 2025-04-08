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

# Do all authentication stuff up to when they call my cell phone.
def login_until_MFA_call(driver):
    login_creds = pd.read_csv("login_creds.csv")

    username_slot = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "loginfmt")))
    next_button = driver.find_element(By.CLASS_NAME, "win-button")

    username_slot.send_keys(login_creds["username"])

    time.sleep(3)
    next_button.click()

    password_slot = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "passwd")))
    password_slot.send_keys(login_creds["password"])
    time.sleep(0.5)
    sign_in_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "win-button")))
    time.sleep(0.5)
    sign_in_button.click()
    time.sleep(0.5)

    sign_in_another_way_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "signInAnotherWay")))
    time.sleep(0.5)
    sign_in_another_way_button.click()
    time.sleep(1.5)

    MFA_options = driver.find_element(By.ID,"idDiv_SAOTCS_Proofs").find_elements(By.CLASS_NAME,"tile")
    text_my_cell = MFA_options[2]
    text_my_cell.click()

def download_excel_if_possible(driver,excel_files):
    for excel_file in excel_files:
        try: 
            print("Found one or more xls / xlsx file(s)! Clicking now...")
            time.sleep(2)
            excel_file.click()
            # Go through all the rigamarole of saving this doc...
            # Switch to the proper iframe.
            iframe = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "iframe"))
            )
            time.sleep(0.75)
            driver.switch_to.frame(iframe)
            # Find the "File" Button in the top ribbon.
            time.sleep(1)
            file_button =  WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID,'FileMenuFlyoutLauncher'))
            )
            time.sleep(1)
            # Click the file button.
            file_button.click()
            time.sleep(0.5)
            # Wait for the Export button to show up
            create_copy_button = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.NAME, "Create a Copy"))
            )
            time.sleep(1.5)
            create_copy_button.click()
            csv_download_button = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.NAME, "Download a Copy"))
            )
            time.sleep(7)
            csv_download_button.click()
            time.sleep(15)
            driver.switch_to.default_content()

        except:
            print("Hello posterity!")
