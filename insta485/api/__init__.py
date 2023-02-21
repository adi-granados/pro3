"""Insta485 REST API."""


from insta485.api.posts import get_post
from insta485.api.likes import delete_like
from insta485.api.likes import post_like
from insta485.model import check_authorized
from insta485.api.posts import get_api
from insta485.api.posts import get_posts
from insta485.api.comments import create_comment
from insta485.api.comments import delete_comment
