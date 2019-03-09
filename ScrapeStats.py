import unittest

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

import numpy as np
import pandas as pd


class ESPN_NBA_Statistics(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()

    def test_get_data(self):
        # VARIABLES
        page = self.driver
        home_page_url = "http://www.espn.com/nba/standings"
        seaons_years = None # list of seasons
        seaons_data = {} # dictionary with 'data value' corresponding to its approporiate 'season key'

        # HOME PAGE
        page.get(home_page_url)

        # Atrieve List of Years
        seasons_dropdown_xpath =\
        "/html/body/div[@id='espnfitt']/div[@id='DataWrapper']/div[@id='espn-an\
        alytics']/div[@class='bp-mobileMDPlus bp-mobileLGPlus bp-tabletPlus bp-\
        desktopPlus bp-desktopLGPlus']/div/div[@id='fittPageContainer']/div[@cl\
        ass='page-container cf']/div[@class='layout is-9-3']/div[@class='layout\
        __column layout__column--1']/section[@class='bg-clr-white br-4 pa4 mb3'\
        ]/section/div[@class='tabs__wrapper']/div[@class='tabs__content']/secti\
        on/section[@class='flex flex-wrap mv1']/section/div[@class='dropdown mr\
        3'][1]/select[@class='dropdown__select']"
        season_list_dropdown = page.find_element_by_xpath(seasons_dropdown_xpath)
        season_list = season_list_dropdown.find_elements_by_partial_link_text("20")
        season_years = np.array([season.text for season in season_list])
        season_data = dict.fromkeys(season_years)
        print(season_data)

    def tearDown(self):
        self.driver.close()

if __name__ == "__main__":
    unittest.main()
