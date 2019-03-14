import scrapy

class ConferenceSpider(scrapy.Spider):
    name = "conference"
    
    def start_requests(self):
        seasons = ['2019', '2018', '2017', '2016', '2015', '2014', '2013', '2012', '2011', '2010', '2009', '2008', '2007', '2006', '2005']
        url_preseason = 'http://www.espn.com/nba/standings/_/seasontype/pre/season/'
        url_conference = 'http://www.espn.com/nba/standings/_/season/'
        url_divison_firsthalf = 'http://www.espn.com/nba/standings/_/season/'
        url_divison_lasthalf = '/group/division'
        url_standings_firsthalf = 'http://www.espn.com/nba/standings/_/season/'
        url_standings_lasthalf = '/group/league'

        for url in urls_conference:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split('/')[-1] # season label
        filename = 'quotes-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
