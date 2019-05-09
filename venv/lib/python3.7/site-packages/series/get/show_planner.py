from datetime import datetime

from series.get.handler import ShowHandler, S
from series.condition import LambdaCondition
from series.tvdb.data import TvdbShow, TvdbEpisode
from series.get import Show
from series.tvdb.api import show_by_id, search_show, current_episodes

from golgi.config import configurable

from amino import __, IO, do, Do, Maybe


@configurable(series=['monitor'], show_planner=['check_interval'])
class ShowPlanner(ShowHandler):
    ''' Queries a tv db for episode schedules.
    If a show currently has no next episode, e.g. because it has just
    aired, the tv db service is queried once a day until there is an
    airdate.
    '''

    def __init__(self, releases, shows, *a, **kw):
        super().__init__(shows, 1, 'show planner', *a, **kw)
        self._releases = releases
        self._shows_initialized = False

    def _sanity_check(self):
        if not self._shows_initialized:
            self._init()

    def _init(self):
        for name in self._monitor:
            self._init_show(name)
        self._shows_initialized = True

    def _init_show(self, name):
        if not self._shows.name_exists(name):
            self._add_show(name)

    def _add_show(self, name: str) -> None:
        self.log.debug('Adding show for "{}"'.format(name))
        tvdb_show = search_show(name).attempt.join.to_maybe.flat_map(lambda a: a.head)
        def add(s: TvdbShow) -> None:
            show = self._shows.add(name, s)
            self._update_show(show, s)
        tvdb_show.cata(add, lambda: self.log.debug('Adding show failed.'))

    def _handle(self, show):
        self._handle_io(show).fatal

    @do(IO[None])
    def _handle_io(self, show: Show) -> Do:
        show.last_check = datetime.now()
        tvdb_show = yield show_by_id(show.etvdb_id)
        yield tvdb_show.cata(
            IO.delay(lambda e: self.log.error(f'Show `{show.name}` couldn\'t be found anymore: {e}')),
            lambda t: self._update_show(show, t),
        )

    @do(IO[None])
    def _update_show(self, show: Show, tvdb_show: TvdbShow) -> Do:
        self.log.debug('Updating show {}'.format(tvdb_show.name))
        data = {}
        if tvdb_show.ended:
            data['ended'] = True
            self.log.warn('Show has ended: {}'.format(show.name))
        else:
            data = yield self._fetch_next_episode(show, tvdb_show)
        self._shows.update(show.id, data)

    @do(IO[dict])
    def _fetch_next_episode(self, show: Show, tvdb_show: TvdbShow) -> Do:
        data = {}
        self.log.debug('Fetching next episode for "{}"'.format(show.name))
        current = yield current_episodes(tvdb_show.id)
        def handle_current(latest: Maybe[TvdbEpisode], next: Maybe[TvdbEpisode]) -> None:
            latest.foreach(lambda a: data.update(latest_episode=a.number, latest_season=a.season))
            def set_date(epi: TvdbEpisode, date: int) -> None:
                data['next_episode_stamp'] = date
                data['season'], data['next_episode'] = epi.season, epi.number
                self.log.debug(f'Found season {epi.season} episode {epi.number}')
            (next & next.flat_map(lambda a: a.airdate)).map2(set_date).get_or(lambda: self.log.debug('no next episode'))
        current.map2(handle_current).get_or(lambda e: self.log.debug(f'Fetching next episode failed: {e}.'))
        return data

    @property
    def _conditions(self):
        return (
            ~S('has_next_episode') & ~S('ended') &
            LambdaCondition('recheck interval',
                            __.can_recheck(self._check_interval))
        )

    def activate_id(self, id):
        super().activate_id(id)
        self._shows.update_by_id(id, last_check_stamp=0)

__all__ = ['ShowPlanner']
