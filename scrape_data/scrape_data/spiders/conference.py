import scrapy
import os
import errno

class ConferenceSpider(scrapy.Spider):
    name = "conference"

    seasons = ['2019', '2018', '2017', '2016', '2015', '2014', '2013', '2012', '2011', '2010', '2009', '2008', '2007', '2006', '2005']

    # page url
    url_preseason_base = 'http://www.espn.com/nba/standings/_/seasontype/pre/season/'
    url_conference_base = 'http://www.espn.com/nba/standings/_/season/'
    url_division_base_firsthalf = 'http://www.espn.com/nba/standings/_/season/'
    url_division_base_lasthalf = '/group/division/'
    url_standings_base_firsthalf = 'http://www.espn.com/nba/standings/_/season/'
    url_standings_base_lasthalf = '/group/league/'

    # folder names
    preseason_dir = '../../../dataCSV/preseaonCSV'
    
    def start_requests(self):
        # conference
        url_conference = self.url_conference_base + season
        file_conference = 'conference-' + season + '.csv'
        self.log(url_conference)
        yield scrapy.Request(url=url_conference, 
                            callback=self.parse,
                            meta={'directory': self.conference_dir, 'filename': file_conference})


    def parse(self, response):
        table_wrapper = response.xpath('//table[contains(@class, "Table2__table__wrapper")]')
        team_names = table_wrapper.xpath('//a[contains(@href, "/nba/team/_/name/")]/text()').getall()
        cell_values = table_wrapper.css('.stat-cell::text').getall()
        cells 



        # make the directory & the file
        directory = response.meta['directory']
        filename = directory + '/' + response.meta['filename']
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise

        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
