import asyncio

from app.connectors.mast import MastDataUnavailable
from app.routers import fusion


def test_campaign_falls_back_to_curated_label_when_metadata_api_is_down(monkeypatch):
    async def down(shot_id):
        raise MastDataUnavailable("API MAST indisponible")

    monkeypatch.setattr(fusion, "fetch_shot_metadata", down)
    assert asyncio.run(fusion._campaign_label(28461, "M9")) == "M9"
    assert asyncio.run(fusion._campaign_label(28461, None)) is None


def test_campaign_prefers_the_api_value_when_available(monkeypatch):
    async def up(shot_id):
        return {"campaign": "M7"}

    monkeypatch.setattr(fusion, "fetch_shot_metadata", up)
    assert asyncio.run(fusion._campaign_label(28461, "M9")) == "M7"
