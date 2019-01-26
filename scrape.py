import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

DATA_CONF_E = []
DATA_CONF_W = []


class BasketballReferenceSearch(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()

    def test_search_years(self):
        driver = self.driver
        driver.get("http://www.basketball-reference.com")
        self.assertIn("Basketball", driver.title)

        elemTab = driver.find_element_by_id("header_leagues")
        elemTab.click()
        assert "No results found." not in driver.page_source

        years_DOM = driver.find_elements_by_xpath("//div[@id='wrap']/div[@id='content']/div[@id='all_stats']/div[2]/div[@id='div_stats']/table[@id='stats']/tbody/tr/th/a")
        years_in_unicode = [year.text for year in years_DOM]
        years_in_ascii = [year.text.encode('utf-8') for year in years_DOM]
        print(years_in_ascii)
        for index, yearText in enumerate(years_in_ascii):
            print("LOOPING : ", index)
            
            current_page = self.driver # current page
            next_year = driver.find_element_by_link_text(yearText) # next season
            next_year.click() # go to the page
            self.assertIn(yearText, driver.title) # make sure redirect was sucessful
            # CONFERENCE STANDINGS
            conference_standings_section = current_page.find_element_by_xpath("/html/body/div[@id='wrap']/div[@id='content']/div[@id='all_standings']/div[@class='section_wrapper']/div[@class='section_content']/div/div/div[@id='all_confs_standings_E']/div")
            ##### EAST 
            teams_E = conference_standings_section.find_elements_by_class_name("/div[@id='div_confs_standings_E']/table[@id='confs_standings_E']/tbody/full_table")
            for team_E in teams_E:
                team_E_data = {}
                team_E_name_outer = team.find_element_by_class_name("left")
                team_E_name = team_E_name_outer.find_element_by_tag_name('a').text.encode("ascii")
                other_data = team.find_elements_by_class_name("right")
                wins = other_data[0].text.encode('utf-8')
                losses = other_data[1].text.encode('utf-8')
                win_loss_pct = other_data[2].text.encode('utf-8')
                gb = other_data[3].text.encode('utf-8')
                pts_per_g = other_data[4].text.encode('utf-8')
                opp_pts_per_g = other_data[5].text.encode('utf-8')
                srs = other_data[6].text.encode('utf-8')

                team_E_data["Team Name"] = team_E_name;
                team_E_data["Wins"] = wins;
                team_E_data["Losses"] = losses;
                team_E_data["Win/Loss PCT"] = win_loss_pct;
                team_E_data["GB"] = gb;
                team_E_data["Points per Game"] = pts_per_g;
                team_E_data["Opponent Points per Game"] = opp_pts_per_g;
                team_E_data["SRS"] = srs;
                DATA_CONF_E.append(team_data)
            ##### WEST
            teams_W = conference_standings_section

            current_page = self.driver # current page
            driver.back()
            driver.implicitly_wait(7)

    def tearDown(self):
        self.driver.close()

if __name__ == "__main__":
    unittest.main()