from golgi.config import configurable
from series.logging import Logging

from amino import IO, Map

from series.api_client import ClientBase, ApiClientMeta, command, ApiClient


@configurable(library_client=['rest_api_port', 'rest_api_url'])
class LibClient(ClientBase, metaclass=ApiClientMeta):

    @property
    def client(self):
        return ApiClient(self._rest_api_url, self._rest_api_port)

    @command('series season episode', 'Create an episode with the supplied metadata')
    def create_episode(self, cmd):
        series, season, episode = cmd.args
        data = dict(episode=episode)
        path = 'series/{}/seasons/{}/episodes'.format(series, season)
        return IO.delay(self.client.post, path, body=data)

    @command('series season episode subfps', 'Set the episode\'s subfps')
    def subfps(self, cmd):
        series, season, episode, subfps = cmd.args
        data = dict(subfps=subfps)
        path = 'series/{}/seasons/{}/episodes/{}'.format(series, season, episode)
        return IO.delay(self.client.put, path, body=data)

    def set_episode_new(self, cmd, new):
        series = cmd.args.head.get_or_fail('no show specified')
        data = cmd.args.lift(1).map(lambda a: Map(season=a)).get_or_strict(Map())
        data1 = cmd.args.lift(2).map(lambda a: data ** Map(episode=a)).get_or_strict(data)
        endpoint = 'new' if new else 'seen'
        path = f'series/{series}/mark_{endpoint}'
        return IO.delay(self.client.put, path, body=data1)

    @command('show season episode[-episode]', 'mark one episode or a range of episodes as seen')
    def mark_episode_seen(self, cmd):
        return self.set_episode_new(cmd, False)

    @command('show season episode[-episode]', 'mark one episode or a range of episodes as new')
    def mark_episode_new(self, cmd):
        return self.set_episode_new(cmd, True)

__all__ = ('LibClient',)
