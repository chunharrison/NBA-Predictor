import operator
from typing import Tuple, Callable, TypeVar

from difflib import SequenceMatcher

from amino import do, Do, IO, Either, List, Try, Left, Maybe, Just, Nothing
from amino.json.data import JsonError
from amino.util.numeric import parse_int

from series.tvdb.client import query_list, query, query_one
from series.tvdb.data import (TvdbShow, TvdbSeason, TvdbSeasonSummary, TvdbEpisode, ShowCodec, SummaryCodec,
                              EpisodeCodec, TvdbEpisodeMetadata, EpisodeMetadataCodec)
from series.util import now_unix

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')


def map_et(e: Either[A, B], f: Callable[[B], IO[Either[A, C]]]) -> IO[Either[A, C]]:
    return e.cata(lambda a: IO.pure(Left(a)), f)


@do(IO[Either[str, List[TvdbShow]]])
def search_show(name: str) -> Do:
    response = yield query_list(ShowCodec, 'search/series', name=name)
    return response.map(lambda data: data.map(TvdbShow.from_codec))


@do(IO[Either[JsonError, TvdbShow]])
def show_by_id(id: int) -> Do:
    response = yield query(ShowCodec, f'series/{id}')
    return response.map(TvdbShow.from_codec)


@do(Either[JsonError, TvdbSeasonSummary])
def analyse_summary(data: SummaryCodec) -> Do:
    num_epi = yield parse_int(data.airedEpisodes)
    seasons = yield data.airedSeasons.traverse(parse_int, Either)
    yield (
        Try(lambda: max(seasons))
        .map(lambda sc: TvdbSeasonSummary(num_epi, sc))
        .lmap(lambda a: JsonError(data, 'no seasons'))
    )


@do(IO[Either[JsonError, TvdbSeasonSummary]])
def season_summary(id: int) -> Do:
    response = yield query(SummaryCodec, f'series/{id}/episodes/summary')
    return response.flat_map(analyse_summary)


def season_result(number: int, response: List[EpisodeCodec]) -> TvdbSeason:
    return TvdbSeason(number, response.map(TvdbEpisode.from_codec))


@do(IO[Either[JsonError, TvdbSeason]])
def season(id: int, number: int) -> Do:
    response = yield query_list(EpisodeCodec, f'series/{id}/episodes/query', airedSeason=number)
    return response.map(lambda a: season_result(number, a))


@do(IO[Either[JsonError, TvdbSeason]])
def latest_season(id: int) -> Do:
    summary = yield season_summary(id)
    yield map_et(summary, lambda s: season(id, s.seasons))


CurrentEpisodes = Tuple[Maybe[TvdbEpisode], Maybe[TvdbEpisode]]


def closer(
        to_now: Callable[[int, int], bool],
        to_prev: Callable[[int, int], bool],
        now: int,
        prev: Maybe[TvdbEpisode],
) -> bool:
    def later(candidate: int) -> bool:
        prev_date = prev.flat_map(lambda a: a.airdate)
        return to_now(candidate, now) and not prev_date.exists(lambda a: to_prev(a, candidate))
    return later


def later(now: int, prev: Maybe[TvdbEpisode]) -> bool:
    return closer(operator.lt, operator.gt, now, prev)


def earlier(now: int, prev: Maybe[TvdbEpisode]) -> bool:
    return closer(operator.gt, operator.lt, now, prev)


def find_current_in_season(now: int, season: TvdbSeason) -> CurrentEpisodes:
    def folder(z: CurrentEpisodes, a: TvdbEpisode) -> CurrentEpisodes:
        prev_before, prev_after = z
        prev = Just(a) if a.airdate.exists(later(now, prev_before)) else prev_before
        after = Just(a) if a.airdate.exists(earlier(now, prev_after)) else prev_after
        return prev, after
    return season.episodes.fold_left((Nothing, Nothing))(folder)


@do(IO[Either[JsonError, CurrentEpisodes]])
def current_episodes(id: int) -> Do:
    season = yield latest_season(id)
    now = yield IO.delay(lambda: now_unix())
    return season.map(lambda a: find_current_in_season(now, a))


@do(IO[Either[JsonError, TvdbEpisode]])
def episode(id: int, sn: int, en: int) -> Do:
    data = yield query_one(EpisodeCodec, f'series/{id}/episodes/query', id=id, airedSeason=sn, airedEpisode=en)
    return data.map(TvdbEpisode.from_codec)


@do(IO[Either[JsonError, Maybe[int]]])
def airdate(id: int, sn: int, en: int) -> Do:
    response = yield episode(id, sn, en)
    return response.map(lambda a: a.airdate)


@do(IO[Either[JsonError, TvdbEpisodeMetadata]])
def episode_metadata(id: int, sn: int, en: int) -> Do:
    data = yield query_one(EpisodeMetadataCodec, f'series/{id}/episodes/query', id=id, airedSeason=sn, airedEpisode=en)
    return data.map(TvdbEpisodeMetadata.from_codec)


@do(IO[Either[JsonError, List[TvdbEpisodeMetadata]]])
def season_metadata(id: int, sn: int) -> Do:
    data = yield query_list(EpisodeMetadataCodec, f'series/{id}/episodes/query', airedSeason=sn)
    return data.map(lambda a: a.map(TvdbEpisodeMetadata.from_codec))


def name_match(target: str, candidate: TvdbShow) -> float:
    matcher = SequenceMatcher()
    matcher.set_seq2(target.lower())
    matcher.set_seq1(candidate.name.lower())
    return matcher.ratio()


@do(IO[Either[JsonError, Maybe[TvdbShow]]])
def guess_show(name: str) -> Do:
    candidates = yield search_show(name)
    return candidates.map(lambda a: a.sort_by(lambda b: name_match(name, b)).last)


__all__ = ('search_show', 'show_by_id', 'season', 'latest_season', 'current_episodes', 'airdate', 'episode_metadata',
           'season_metadata',)
