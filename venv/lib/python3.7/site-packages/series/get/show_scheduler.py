import operator
from datetime import datetime, timedelta

from amino import IO, Maybe, Lists, do, Do, Either
from amino.json.data import JsonError

from series.get.handler import ShowHandler

from series.condition import HandlerCondition, SimpleCondition, LambdaCondition
from series.util import unix_to_datetime
from series.get import Show
from series.tvdb.api import airdate


class AirsToday(HandlerCondition):

    @property
    def _today_thresh(self):
        return datetime.now() - timedelta(hours=16)

    def _check(self, show):
        return show.next_episode_date < self._today_thresh

    def ev(self, show):
        return show.has_next_episode and self._check(show)

    def describe(self, show, target):
        match = self.ev(show)
        good = match == target
        today = (show.next_episode_date > self._today_thresh) and match
        desc = ('today' if today else
                show.next_episode_date.strftime('%F') if
                show.next_episode_stamp > 0 else
                'no date')
        return 'airs today[{}]'.format(self._paint(desc, good))


class CanCatchUp(SimpleCondition):
    ''' *current* is the last aired episode, which includes those aired
    within 24 hours in the future.
    *latest* is the newest release in the db.
    '''

    def __init__(self, latest) -> None:
        self._latest = latest

    def latest_episode(self, show):
        return show.latest_episode_m

    def latest_release(self, show):
        return self._latest(show)

    def ev(self, show):
        return (self.latest_episode(show) & self.latest_release(show)
                ).map2(operator.gt).true

    @property
    def _desc(self):
        return 'latest > downloaded'

    def _repr(self, show, match):
        op = '>' if match else '<'
        def has(release):
            return '{} {} {}'.format(self.latest_episode(show) | -1, op,
                                     release)
        return self.latest_release(show) / has | 'no latest episode'


class ShowScheduler(ShowHandler):

    def __init__(self, releases, shows, **kw):
        super().__init__(shows, 60, 'show scheduler', cooldown=3600, **kw)
        self._releases = releases

    def _handle(self, show: Show) -> None:
        self._handle_io(show).fatal

    @do(IO[None])
    def _handle_io(self, show: Show) -> Do:
        self.log.debug(f'attempting to schedule {show}')
        response = yield airdate(show.etvdb_id, show.season, show.next_episode)
        def error(e: JsonError) -> IO[None]:
            IO.delay(self.log.error, f'failed to parse repsonse for airdate of next episode of `{show}`: {e}')
        def present(ad: int) -> IO[None]:
            return (
                self._handle_invalid_show(show, ad)
                if show.has_next_episode and ad != show.next_episode_stamp else
                self._handle_valid_show(show)
            )
        def absent() -> IO[None]:
            return self._handle_valid_show(show)
        def success(ad: Maybe[int]) -> IO[None]:
            return ad.cata(present, absent)
        yield response.cata(error, success)

    def _handle_valid_show(self, show: Show) -> IO[None]:
        def catch_up(latest_release, latest_episode):
            return (
                Lists.range(latest_release + 1, latest_episode + 1)
                .traverse(lambda e: self._schedule(show, show.latest_season, e), IO)
            )
        def schedule_next():
            return self._schedule(show, show.season, show.next_episode)
        return (
            schedule_next()
            if AirsToday().ev(show) else
            (self._latest(show) & show.latest_episode_m).map2(catch_up).get_or_strict(IO.pure(None))
        )

    @do(IO[None])
    def _handle_invalid_show(self, show: Show, airdate: int) -> Do:
        new_date = unix_to_datetime(airdate).date()
        msg = f'{show.name} {show.season}x{show.next_episode} was rescheduled: {show.next_episode_day} => {new_date}'
        yield IO.delay(self.log.error, msg)
        yield IO.delay(self._update, show, next_episode_stamp=airdate)

    @property
    def _conditions(self):
        return LambdaCondition('next has no release', self._no_next_release) & (AirsToday() | CanCatchUp(self._latest))

    def _latest(self, show):
        return self._releases.latest_for_season(show.canonical_name, show.latest_season)

    def _no_next_release(self, show):
        return not self._latest(show).contains(show.next_episode)

    @do(IO[None])
    def _schedule(self, show: Show, season: int, episode: int) -> Do:
        response = yield airdate(show.etvdb_id, season, episode)
        @do(Either[str, None])
        def schedule() -> Do:
            data = yield response
            airdate = yield data.to_either(lambda: f'no airdate')
            msg = f'Scheduling release "{show.name} {season}x{episode}" on {unix_to_datetime(airdate)}'
            self.log.info(msg)
            self._releases.create(show.canonical_name, season, episode, airdate,
                                  downgrade_after=show.downgrade_after,
                                  search_name=show.search_name)
            if show.season > show.latest_season:
                self._shows.update_by_id(show.id, latest_season=show.season)
            self._commit()
        result = yield IO.delay(schedule)
        yield result.cata(
            lambda e: IO.delay(lambda: self.log.error(f'couldn\'t schedule {show} {season}x{episode}: {e}')),
            IO.pure
        )


__all__ = ['ShowScheduler']
