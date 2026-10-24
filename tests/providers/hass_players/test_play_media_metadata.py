"""Tests for the metadata a Home Assistant player is handed with a play command."""

from __future__ import annotations

from typing import Any

from music_assistant_models.player import PlayerMedia

from tests.providers.hass_players.test_external_playback import _make_player

IMAGE_URL = "http://10.0.0.5:8097/imageproxy?path=cover.jpg"


async def _played_extra(media: PlayerMedia, hass_domain: str | None = None) -> dict[str, Any]:
    """
    Play the media on a mocked player and return the `extra` sent to Home Assistant.

    :param media: The media to play.
    :param hass_domain: The Home Assistant integration the player entity belongs to.
    """
    player = _make_player()
    if hass_domain:
        player._extra_data["hass_domain"] = hass_domain
    await player.play_media(media)
    extra: dict[str, Any] = player.hass.call_service.call_args.kwargs["service_data"]["extra"]
    return extra


async def test_artwork_is_sent_as_thumb_for_dlna_renderers() -> None:
    """The album art reaches integrations that read `thumb`, such as DLNA renderers."""
    media = PlayerMedia(uri="library://track/1", title="MA Track", image_url=IMAGE_URL)

    extra = await _played_extra(media, hass_domain="dlna_dmr")

    assert extra.get("thumb") == IMAGE_URL


async def test_cast_gets_only_its_own_metadata_keys() -> None:
    """Google Cast keeps its artwork in the cast metadata, without a duplicate from `thumb`."""
    media = PlayerMedia(uri="library://track/1", title="MA Track", image_url=IMAGE_URL)

    extra = await _played_extra(media, hass_domain="cast")

    assert "thumb" not in extra
    assert extra["metadata"]["imageUrl"] == IMAGE_URL
    assert extra["metadata"]["images"] == [{"url": IMAGE_URL}]


async def test_no_thumb_without_artwork() -> None:
    """Media without artwork sends no empty `thumb`."""
    extra = await _played_extra(
        PlayerMedia(uri="library://track/1", title="MA Track"), hass_domain="dlna_dmr"
    )

    assert "thumb" not in extra
