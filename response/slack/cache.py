import logging

from django.conf import settings
from django.db import transaction

from response.core.models import ExternalUser
from response.slack.client import SlackError

logger = logging.getLogger(__name__)


def update_user_cache():
    cursor = None
    while cursor != "":
        response = settings.SLACK_CLIENT.get_paginated_users(limit=200, cursor=cursor)

        users = response["members"]

        logger.info(f"Updating {len(users)} users in the cache")
        with transaction.atomic():
            for user in users:
                ExternalUser.objects.update_or_create_slack(
                    external_id=user["id"],
                    defaults={
                        "display_name": user["profile"]["display_name_normalized"]
                        or user["name"],
                        "full_name": user["profile"]["real_name"] or user["name"],
                        "email": user["profile"].get("email", None),
                    },
                )
        cursor = response["response_metadata"].get("next_cursor")


def get_user_profile(external_id):
    """
    Gets a slack user profile:
        - from the DB cache if available
        - or else from the Slack API
    """
    if not external_id:
        return None

    try:
        external_user = ExternalUser.objects.get(external_id=external_id)
        logger.info(f"Got user {external_id} from DB cache")

        return {
            "id": external_user.external_id,
            "name": external_user.display_name,
            "fullname": external_user.full_name,
            "email": external_user.email,
        }
    except ExternalUser.DoesNotExist:
        # profile from slack
        try:
            user_profile = settings.SLACK_CLIENT.get_user_profile(external_id)
        except SlackError:
            logger.error(f"Failed to get user {external_id} from DB cache or Slack")
            raise

        # store it in the DB
        ExternalUser.objects.get_or_create_slack(
            external_id=user_profile["id"],
            defaults={
                "display_name": user_profile["name"],
                "full_name": user_profile["fullname"],
                "email": user_profile["email"],
            },
        )

        logger.info(f"Got user {external_id} from Slack and cached in DB")
        return user_profile


def get_user_profile_by_email(email):
    """
    Gets a slack user profile:
        - from the DB cache if available
        - or else from the Slack API
    """
    if not email:
        raise SlackError("Can't fetch user without an email")

    try:
        external_user = ExternalUser.objects.get(email=email)
        logger.info(f"Got user with email {email} from DB cache")

        return {
            "id": external_user.external_id,
            "name": external_user.display_name,
            "fullname": external_user.full_name,
            "email": external_user.email,
        }
    except ExternalUser.DoesNotExist:
        # profile from slack
        try:
            user_profile = settings.SLACK_CLIENT.get_user_profile_by_email(email)
        except SlackError:
            logger.error(
                f"Failed to get user with email {email} from DB cache or Slack"
            )
            raise

        # store it in the DB
        ExternalUser.objects.get_or_create_slack(
            external_id=user_profile["id"],
            defaults={
                "display_name": user_profile["name"],
                "full_name": user_profile["fullname"],
                "email": user_profile["email"],
            },
        )

        logger.info(f"Got user with email {email} from Slack and cached in DB")
        return user_profile
