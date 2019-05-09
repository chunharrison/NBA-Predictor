# coding: utf-8

from golgi import configurable
from tek.errors import ParseError

from amino import IO, do, Do

from series.library.handler import BaseHandler
from series.library.model.season import Season
from series.library.model.series import Series
from series.tvdb.data import TvdbEpisodeMetadata
from series.tvdb.api import guess_show, season_metadata, episode_metadata


@configurable(library=['metadata_interval'])
class Metadata(BaseHandler):

    def __init__(self, library, player):
        super().__init__(library, self._metadata_interval, 'metadata service')
        self._library = library
        self._player = player
        self._min_failed = 0

    def _handle(self, item):
        data = {}
        handler = (self._handle_season if isinstance(item, Season) else self._handle_episode)
        try:
            self.log.info('Fetching metadata for {}…'.format(item))
            handler(item).fatal
        except Exception as e:
            self.log.error(e)
            data = dict(metadata_failures=item.metadata_failures + 1)
        else:
            data = dict(metadata_fetched=True)
        self._library.alter_object(item, data)

    @do(IO[None])
    def _handle_season(self, season) -> Do:
        if not season.series.tvdb_id:
            yield self.update_tvdb_id(season.series)
        if season.series.tvdb_id:
            data = yield season_metadata(season.series.tvdb_id, season.number)
            data.map(lambda epis: epis.map(lambda epi: self._update_episode(season.series, epi)))


    @do(IO[None])
    def _handle_episode(self, episode) -> Do:
        if not episode.series.tvdb_id:
            yield self.update_tvdb_id(episode.series)
        if episode.series.tvdb_id:
            data = yield episode_metadata(episode.series.tvdb_id,
                                          episode.season.number,
                                          episode.number)
            data.map(lambda epi: self._update_episode(episode.season.series, epi))

    @do(IO[None])
    def update_tvdb_id(self, series: Series) -> Do:
        response = yield guess_show(series.name)
        may_show = yield IO.from_either(response)
        show = yield IO.from_maybe(may_show, lambda: f'could not find a tvdb show for {series.name}')
        yield IO.delay(self._library.alter_series, series.name, dict(tvdb_id=show.id))

    def _update_episode(self, series, data: TvdbEpisodeMetadata):
        self._library.alter_episode(
            series,
            data.season,
            data.number,
            dict(title=data.title, overview=data.overview, metadata_fetched=True),
        )

    def _qualify(self, item):
        fails = item.metadata_failures
        return fails is not None and fails == self._min_failed and fails < 15

    @property
    def _candidates(self):
        candidates = (self._seasons or self._new_episodes or
                      self._failed_episodes)
        counts = [c.metadata_failures for c in candidates
                  if c.metadata_failures is not None]
        self._min_failed = min(counts or [0])
        return candidates

    @property
    def _new_episodes(self):
        return [e for e in self._library.new_episodes if not
                e.metadata_fetched]

    @property
    def _seasons(self):
        return self._library.seasons(extra=dict(metadata_fetched=False))

    @property
    def _failed_episodes(self):
        return []


__all__ = ['Metadata']
