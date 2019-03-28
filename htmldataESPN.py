import scrapy
import os
import errno

class HTMLDataSpider(scrapy.Spider):
    name = "htmldata"

    seasons = ['2019', '2018', '2017', '2016', '2015', '2014', '2013', '2012', '2011', '2010', '2009', '2008', '2007', '2006', '2005']

    # page url
    url_preseason_base = 'http://www.espn.com/nba/standings/_/seasontype/pre/season/'
    url_conference_base = 'http://www.espn.com/nba/standings/_/season/'
    url_division_base_firsthalf = 'http://www.espn.com/nba/standings/_/season/'
    url_division_base_lasthalf = '/group/division/'
    url_standings_base_firsthalf = 'http://www.espn.com/nba/standings/_/season/'
    url_standings_base_lasthalf = '/group/league/'

    # folder names
    preseason_dir = '../../../dataHTML/preseaonHTML'
    conference_dir = '../../../dataHTML/conferenceHTML'
    division_dir = '../../../dataHTML/divisionHTML'
    standings_dir = '../../../dataHTML/standingsHTML'
    
    def start_requests(self):
        for season in self.seasons:
            # preseason
            url_preseason = self.url_preseason_base + season
            file_preseason = 'preseason-' + season + '.html'
            self.log(url_preseason)
            yield scrapy.Request(url=url_preseason, 
                                callback=self.parse,
                                meta={'directory': self.preseason_dir, 'filename': file_preseason})

            # conference
            url_conference = self.url_conference_base + season
            file_conference = 'conference-' + season + '.html'
            self.log(url_conference)
            yield scrapy.Request(url=url_conference, 
                                callback=self.parse,
                                meta={'directory': self.conference_dir, 'filename': file_conference})

            # division
            url_division = self.url_division_base_firsthalf + season + self.url_division_base_lasthalf
            file_division = 'division-' + season + '.html'
            self.log(url_division)
            yield scrapy.Request(url=url_division, 
                                callback=self.parse,
                                meta={'directory': self.division_dir, 'filename': file_division})

            # standings
            url_standings = self.url_standings_base_firsthalf + season + self.url_standings_base_lasthalf
            file_standings = 'standings-' + season + '.html'
            self.log(url_standings)
            yield scrapy.Request(url=url_standings,
                                callback=self.parse,
                                meta={'directory': self.standings_dir, 'filename': file_standings})


    def parse(self, response):
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
