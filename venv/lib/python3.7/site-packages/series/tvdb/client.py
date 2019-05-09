import requests

from amino import IO, Map, Either, List, Right, Left, do, Do, Dat, Maybe, Nil
from amino.json.decoder import decode_json_type, decode_json_type_json
from amino.json.data import Json, JsonError

from typing import TypeVar, Type, Callable, Any, Dict, Generic

A = TypeVar('A')
P = TypeVar('P')
api_key = 'Y08E38CQDT92BQ5T'
auth_token = None
base_url = 'https://api.thetvdb.com'


def url(path: str) -> str:
    return f'{base_url}/{path}'


@do(IO[None])
def auth() -> Do:
    response = yield IO.delay(requests.post, url('login'), json=Map(apikey=api_key))
    body = yield IO.delay(lambda: response.json())
    token_field = yield (
        IO.failed(f'invalid response payload structure from the tvdb api auth endpoint: {body}')
        if not isinstance(body, dict) else
        IO.pure(Map(body).lift('token'))
    )
    token = yield IO.from_maybe(token_field, f'no token in the tvdb api auth response: {body}')
    global auth_token
    auth_token = token


def headers() -> dict:
    return {
        'accept-language': 'en',
        'authorization': f'Bearer {auth_token}',
    }


@do(IO[str])
def request(path: str, params: Map[str, str]) -> Do:
    response = yield IO.delay(requests.get, url(path), params=params, headers=headers())
    status = response.status_code
    if status == 401:
        yield auth()
        yield request(path, params)
    elif status == 200:
        yield IO.delay(lambda: response.text)
    else:
        yield IO.failed(f'unexpected response code {status} from the tvdb api for {path}')


@do(IO[Either[JsonError, A]])
def data_query(
        path: str,
        params: Map[str, str],
        payload_tpe: type,
        decode_data: Callable[[Any], Either[JsonError, A]],
) -> Do:
    response = yield request(path, params)
    data = decode_json_type(response, payload_tpe)
    return data.flat_map(decode_data)


class Links(Dat['Links']):

    def __init__(self, next: Maybe[int]) -> None:
        self.next = next


class JsonPayload(Dat['JsonPayload']):

    def __init__(self, data: Json) -> None:
        self.data = data


def query(tpe: Type[A], path: str, **params: Dict[str, str]) -> IO[Either[JsonError, A]]:
    return data_query(path, Map(params), JsonPayload, lambda a: decode_json_type_json(a.data, tpe))


class JsonListPayload(Dat['JsonListPayload']):

    def __init__(self, data: List[Json], links: Maybe[Links]) -> None:
        self.data = data
        self.links = links


class ListResult(Generic[A], Dat['ListResult[A]']):

    def __init__(self, data: List[A], next: Maybe[int]) -> None:
        self.data = data
        self.next = next


def decode_list(tpe: Type[A]) -> Callable[[JsonListPayload], Either[JsonError, ListResult[A]]]:
    @do(Either[JsonError, ListResult[A]])
    def decode_list(payload: JsonListPayload) -> Do:
        data = yield payload.data.traverse(lambda a: decode_json_type_json(a, tpe), Either)
        return ListResult(data, payload.links.flat_map(lambda a: a.next))
    return decode_list


@do(IO[Either[JsonError, List[A]]])
def query_list(tpe: Type[A], path: str, **params: Dict[str, str]) -> Do:
    response = yield data_query(
        path,
        Map(params),
        JsonListPayload,
        decode_list(tpe),
    )
    @do(IO[Either[JsonError, List[A]]])
    def unpack_and_recurse(result: ListResult[A]) -> Do:
        next_data = yield (
            result.next
            .map(lambda a: query_list(tpe, path, page=a, **params))
            .get_or_strict(IO.pure(Right(Nil)))
        )
        return next_data.map(lambda a: result.data + a)
    yield response.cata(lambda a: IO.pure(Left(a)), unpack_and_recurse)


@do(Either[JsonError, A])
def validate_query_one(result: Either[JsonError, List[A]], params: Dict[str, str]) -> Do:
    items = yield result
    err = lambda what: JsonError(items, f'{what} matched for {params}')
    def multi() -> Either[JsonError, A]:
        return Left(err('multiple records'))
    yield (
        items
        .detach_head
        .to_either(lambda: err(items, 'no record'))
        .flat_map2(lambda h, t: Right(h) if t.empty else multi())
    )


@do(IO[Either[JsonError, A]])
def query_one(tpe: Type[A], path: str, **params: Dict[str, str]) -> Do:
    items = yield query_list(tpe, path, **params)
    return validate_query_one(items, params)


__all__ = ('api_key', 'auth', 'query', 'query_list', 'query_one',)
