import scrapy

class ConferenceSpider(scrapy.Spider):
    name = "conference"

    seasons = ['2019', '2018', '2017', '2016', '2015', '2014', '2013', '2012', '2011', '2010', '2009', '2008', '2007', '2006', '2005']

    # page url
    url_preseason_base = 'http://www.espn.com/nba/standings/_/seasontype/pre/season/'
    url_conference_base = 'http://www.espn.com/nba/standings/_/season/'
    url_divison_base_firsthalf = 'http://www.espn.com/nba/standings/_/season/'
    url_divison_base_lasthalf = '/group/division'
    url_standings_base_firsthalf = 'http://www.espn.com/nba/standings/_/season/'
    url_standings_base_lasthalf = '/group/league'

    # folder names
    preseason_dir = '../../../preseaonHTML'
    conference_dir = '../../../conferenceHTML'
    division_dir = '../../../divisonHTML'
    standings_dir = '../../../standingsHTML'
    
    def start_requests(self):
        for season in self.seasons:
            # preseason
            url_preseason = self.url_preseason_base + season
            yield scrapy.Request(url=url_preseason, callback=self.parse)

            # conference
            url_conference = self.url_conference_base + season
            yield scrapy.Request(url=url_conference, callback=self.parse)

            # divison
            url_divison = self.url_division_base_firsthalf + season + self.url_divison_base_lasthalf
            yield scrapy.Request(url=url_divison, callback=self.parse)

            # standings
            url_standings = self.url_standings_base_firsthalf + season + self.url_standings_base_lasthalf
            yield scrapy.Request(url=url_standings, callback=self.parse)

    def parse(self, response):
        page = response.url[35:].replace('/', '-') # season label
        filename = '%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
