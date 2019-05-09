from datetime import datetime

from amino import Dat, List, Maybe, Try

from series.util import datetime_to_unix


class ShowCodec(Dat['ShowCodec']):

    def __init__(self, id: int, seriesName: str, overview: Maybe[str], status: str, firstAired: str) -> None:
        self.id = id
        self.seriesName = seriesName
        self.overview = overview
        self.status = status
        self.firstAired = firstAired


class SummaryCodec(Dat['SummaryCodec']):

    def __init__(self, airedEpisodes: int, airedSeasons: List[int]) -> None:
        self.airedEpisodes = airedEpisodes
        self.airedSeasons = airedSeasons


class EpisodeCodec(Dat['EpisodeCodec']):

    def __init__(self, airedEpisodeNumber: int, airedSeason: int, firstAired: str) -> None:
        self.airedEpisodeNumber = airedEpisodeNumber
        self.airedSeason = airedSeason
        self.firstAired = firstAired


class EpisodeMetadataCodec(Dat['EpisodeMetadataCodec']):

    def __init__(self, airedEpisodeNumber: int, airedSeason: int, episodeName: str, overview: str) -> None:
        self.airedEpisodeNumber = airedEpisodeNumber
        self.airedSeason = airedSeason
        self.episodeName = episodeName
        self.overview = overview


class TvdbShow(Dat['TvdbShow']):

    @staticmethod
    def from_codec(data: ShowCodec) -> 'TvdbShow':
        return TvdbShow(
            data.id,
            data.seriesName,
            data.overview,
            data.status.lower() == 'ended',
            data.firstAired,
        )

    def __init__(self, id: int, name: str, overview: Maybe[str], ended: bool, year: str) -> None:
        self.id = id
        self.name = name
        self.overview = overview
        self.ended = ended
        self.year = year


class TvdbEpisode(Dat['TvdbEpisode']):

    @staticmethod
    def from_codec(data: EpisodeCodec) -> 'TvdbEpisode':
        airdate = Try(lambda: datetime.fromisoformat(data.firstAired))
        stamp = airdate.map(datetime_to_unix)
        return TvdbEpisode(data.airedEpisodeNumber, data.airedSeason, stamp.to_maybe)

    def __init__(self, number: int, season: int, airdate: Maybe[int]) -> None:
        self.number = number
        self.season = season
        self.airdate = airdate


class TvdbSeason(Dat['TvdbSeason']):

    def __init__(self, number: int, episodes: List[TvdbEpisode]) -> None:
        self.number = number
        self.episodes = episodes


class TvdbSeasonSummary(Dat['TvdbSeasonSummary']):

    def __init__(self, episodes: int, seasons: int) -> None:
        self.episodes = episodes
        self.seasons = seasons


class TvdbEpisodeMetadata(Dat['TvdbEpisodeMetadata']):

    @staticmethod
    def from_codec(data: EpisodeMetadataCodec) -> 'TvdbEpisodeMetadata':
        return TvdbEpisodeMetadata(data.airedEpisodeNumber, data.airedSeason, data.episodeName, data.overview)

    def __init__(self, number: int, season: int, title: str, overview: str) -> None:
        self.number = number
        self.season = season
        self.title = title
        self.overview = overview


__all__ = ('TvdbShow', 'TvdbEpisode', 'TvdbSeason', 'TvdbSeasonSummary', 'ShowCodec', 'SummaryCodec', 'EpisodeCodec',
           'EpisodeMetadataCodec', 'TvdbEpisodeMetadata',)
