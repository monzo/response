import hashlib
import hmac
import logging
from functools import wraps
from time import time

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.handlers.wsgi import WSGIRequest

logger = logging.getLogger(__name__)

slack_signing_secret = settings.SLACK_SIGNING_SECRET


def slack_authenticate(f):
    """
    slack_authenticate is a wrapper to check the request signature.

    usage:

    @slack_authenticate
    def slack_actions():
        pass
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        request = args[0]
        if len(args) < 1 or not type(args[0]) == WSGIRequest:
            logger.error(
                "slack_authenticate annotation used with incorrect args or no args"
            )
            raise ValueError
        if authenticate(request):
            return f(*args, **kwargs)
        else:
            logger.error(f"Denied access to {request.path}")
            raise PermissionDenied

    return wrapper


def authenticate(request):
    """
    authenticate authenticates the request using the signature process provided
    by slack

    see: https://api.slack.com/docs/verifying-requests-from-slack
    """

    if slack_signing_secret == "":
        logger.critical("Signing secret isn't defined")
        return False

    if "HTTP_X_SLACK_REQUEST_TIMESTAMP" not in request.META:
        logger.error("HTTP_X_SLACK_REQUEST_TIMESTAMP not provided")
        return False

    req_timestamp = request.META["HTTP_X_SLACK_REQUEST_TIMESTAMP"]
    if abs(time() - int(req_timestamp)) > 60 * 5:
        logger.error("Invalid request timestamp")
        return False

    if (
        "HTTP_X_SLACK_SIGNATURE" not in request.META
        or request.META["HTTP_X_SLACK_SIGNATURE"] == ""
    ):
        logger.error("HTTP_X_SLACK_SIGNATURE not provided")
        return False

    req_signature = request.META["HTTP_X_SLACK_SIGNATURE"]
    if not verify_signature(
        req_timestamp, req_signature, slack_signing_secret, request.body
    ):
        logger.error("Invalid request signature")
        return False

    return True


def verify_signature(timestamp, signature, secret, data):
    # Verify the request signature of the request sent from Slack
    # Generate a new hash using the app's signing secret and request data

    # Compare the generated hash and incoming request signature
    request_hash = generate_signature(timestamp, secret, data)
    return hmac.compare_digest(request_hash, signature)


def generate_signature(timestamp, secret, data):
    req = str.encode("v0:" + str(timestamp) + ":") + data
    return "v0=" + hmac.new(str.encode(secret), req, hashlib.sha256).hexdigest()
