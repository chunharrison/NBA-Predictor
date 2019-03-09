import unittest

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException    

import numpy as np
import pandas as pd

import time


class BacketballReferenceSearch(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()


    def test_get_data(self):

        # VARIABLES
        page = self.driver
        home_page_url = "http://www.basketball-reference.com"
        seaons_years = None # list of seasons
        seaons_data = {} # dictionary with 'data value' corresponding to its approporiate 'season key'
        missing_data = {} # list of seasons that didn't have the data
        
        # HOME PAGE
        page.get(home_page_url)
        # SEASONS/LEAGUES TAB
        seasons_tab = page.find_element_by_id("header_leagues")
        seasons_tab.click()

        # Atrieve List of Years
        seasons_list = page.find_elements_by_xpath("//div[@id='wrap']/div[@id='content']/div[@id='all_stats']/div[2]/div[@id='div_stats']/table[@id='stats']/tbody/tr/th/a")
        seaons_years = np.array([season.text for season in seasons_list])
        seasons_data = dict.fromkeys(seaons_years)

        for season_year in seaons_years:
            if season_year == "2003-04":
                break; # 2003-04 and older seaons have out-dated divisional allignment

            missing_sections = []

            # go to season page    
            link = page.find_element_by_link_text(season_year)
            link.click()

            # CONFERENCE 
            if checkElementExistsCSSSelector("div.standings_confs"):
                dataframe_final_E = self.getConferenceData("E")
                # print("DATAFRAME E: ", dataframe_final_E)
                csv_name_E = "data/conference/" + season_year + "-eastern-conference.csv"
                dataframe_final_E.to_csv(csv_name_E)
                dataframe_final_W = self.getConferenceData("W")
                # print("DATAFRAME W: ", dataframe_final_W)
                csv_name_W = "data/conference/" + season_year + "-western-conference.csv"
                dataframe_final_W.to_csv(csv_name_W)
            else:
                missing_sections.append("Conference")
            
            # DIVISION
            if checkElementExistsCSSSelector("div.standings_divs"):
                


            # go back
            page.execute_script("window.history.go(-1)")
            time.sleep(0.5)

    def checkElementExistsCSSSelector(self, selector):
        page = self.driver
        try:
            page.find_element_by_css_selector(selector)
        except NoSuchElementException:
            return false
        return true

    def getConferenceData(self, region):
        page = self.driver
        # conference_standings_section = page.find_element_by_xpath("/html/body/div[@id='wrap']/div[@id='content']/div[@id='all_standings']/div[@class='section_wrapper']/div[@class='section_content']/div[@class='standings_confs table_wrapper']")
        # # table
        # xpath_table = "/div[" + section + "]/div[@id=\'all_confs_standings_" + region
        # xpath_table += "\']/div[@class='table_outer_container']/div[@id=\'div_confs_standings_" + region
        # xpath_table += "\']/table[@id=\'confs_standings_" + region + "\']"
        # print(xpath_table)
        element_id = "div_confs_standings_" + region
        stat_table = page.find_element_by_id("div_confs_standings_E")
        # table head
        stat_labels = stat_table.find_elements_by_xpath("table/thead/tr/th")
        # table body
        stat_values = stat_table.find_elements_by_xpath("table/tbody/tr")

        # variables
        num_columns = len(stat_labels)
        num_rows = len(stat_values)

        # column
        dataframe_columns = np.array([label.text for label in stat_labels])
        # rows
        dataframe_rows = np.empty([num_rows, num_columns], dtype=object) # empty x by y grid

        for row_index, stat_value_row in enumerate(stat_values):
              # since team name is coded in a different tag 'td', add to 'rows' sperately
              team_name = stat_value_row.find_element_by_tag_name("a")
            #   print("team_name.text:", team_name.text)
              dataframe_rows[row_index, 0] = team_name.text
              # rest of the values
              team_stats = stat_value_row.find_elements_by_tag_name("td")
              for column_index, stat_value in enumerate(team_stats):
                #   print("stat_value.text:", stat_value.text)
                  dataframe_rows[row_index, column_index+1] = stat_value.text.encode('ascii', 'ignore').decode('utf-8')

        return pd.DataFrame(dataframe_rows, columns=dataframe_columns)


    def tearDown(self):
        self.driver.close()


if __name__ == "__main__":
    unittest.main()
