import asyncio

import httpx
import pytest

from app import http_utils


def client_avec(reponses):
    """Client httpx dont chaque appel consomme le comportement suivant : une exception, ou un code HTTP."""
    appels = {"n": 0}

    def handler(request):
        comportement = reponses[min(appels["n"], len(reponses) - 1)]
        appels["n"] += 1
        if isinstance(comportement, Exception):
            raise comportement
        return httpx.Response(comportement, text="ok")

    return httpx.AsyncClient(transport=httpx.MockTransport(handler)), appels


@pytest.fixture(autouse=True)
def sans_attente(monkeypatch):
    attentes = []

    async def faux_sleep(delai):
        attentes.append(delai)

    monkeypatch.setattr(http_utils.asyncio, "sleep", faux_sleep)
    return attentes


def lancer(reponses, **kw):
    async def corps():
        client, appels = client_avec(reponses)
        async with client:
            r = await http_utils.get_with_retry(client, "https://exemple.test/x", **kw)
        return r, appels["n"]

    return asyncio.run(corps())


def test_erreur_de_connexion_transitoire_est_reessayee(sans_attente):
    """Cas du 28 octobre 2026 : ConnectError('') une ou deux fois, puis la connexion passe."""
    r, n = lancer([httpx.ConnectError(""), httpx.ConnectError(""), 200])
    assert r.status_code == 200 and n == 3 and sans_attente == [1.0, 2.0]


def test_statuts_transitoires_reessayes():
    r, n = lancer([503, 502, 200])
    assert r.status_code == 200 and n == 3


def test_abandon_apres_le_maximum_d_essais():
    with pytest.raises(httpx.ConnectError):
        lancer([httpx.ConnectError("")], max_retries=2)
    with pytest.raises(httpx.HTTPStatusError):
        lancer([503], max_retries=1)


def test_erreur_definitive_non_reessayee():
    with pytest.raises(httpx.HTTPStatusError):
        lancer([404, 200])  # 404 : pas de nouvelle tentative
    _, n = lancer([200])
    assert n == 1


def test_un_succes_au_premier_essai_ne_dort_pas(sans_attente):
    lancer([200])
    assert sans_attente == []
