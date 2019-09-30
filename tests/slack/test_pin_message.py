import datetime
import unittest
from unittest.mock import patch

import pytest
from faker import Faker

from response.core.models import TimelineEvent
from response.slack.event_handlers import handle_pin_added, handle_pin_removed
from response.slack.models import PinnedMessage
from tests.factories import ExternalUserFactory, IncidentFactory

faker = Faker()


class TestPinnedMessage(unittest.TestCase):
    @pytest.mark.django_db
    @patch("response.slack.models.pinned_message.get_user_profile")
    def test_add_and_remove_pin(self, get_user_profile):
        incident = IncidentFactory.create()
        user = ExternalUserFactory.create()

        get_user_profile.return_value = {"name": user.display_name}

        text = faker.paragraph(nb_sentences=2, variable_nb_sentences=True)
        handle_pin_added(
            incident,
            {"item": {"message": {"user": user.external_id, "ts": 123, "text": text}}},
        )
        get_user_profile.assert_called_with(user.external_id)

        message = PinnedMessage.objects.get(incident=incident, message_ts=123)
        assert message.text == text

        handle_pin_removed(
            incident,
            {"item": {"message": {"user": user.external_id, "ts": 123, "text": text}}},
        )

        get_user_profile.assert_called_with(user.external_id)

        with pytest.raises(PinnedMessage.DoesNotExist):
            PinnedMessage.objects.get(incident=incident, message_ts=123)
            TimelineEvent.objects.get(
                incident=incident, timestamp=datetime.fromtimestamp(123)
            )
