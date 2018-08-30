from flask import Blueprint, request, g
from api import require_apikey
from api.blueprints.accounts.controllers import auth
from api.apiutils import *

posts = Blueprint('post', __name__)

@posts.route("/ping")
@require_apikey
def test():
    return "pong"

@posts.route("/<post_id>", methods=["GET"])
@require_apikey
def get_post(post_id):
    return get_by_id("posts", post_id)


@posts.route("/<post_id>/replies", methods=["GET"])
@require_apikey
def get_post_replies(post_id):
    return get_paginated("SELECT post_replies.* \
                          FROM posts \
                          INNER JOIN post_replies \
                          ON posts.id = post_replies.id_parent \
                          WHERE posts.id=%s",
                          selection_fields=[post_id],
                          args=request.args,
                          order_clause="ORDER BY id DESC",
                          order_index_format="post_replies.id <= %s",
                          order_arg="max_id")


@posts.route("/<post_id>/reply_count", methods=["GET"])
@require_apikey
def get_post_reply_count(post_id):
    query = "SELECT count(*) \
             as reply_count \
             from post_replies \
             where id_parent=%s"
    return execute_single_tuple_query(query, (post_id,))


@posts.route("/new", methods=["POST", "PUT"])
@auth.login_required
def make_new_post():
    if request.method == "POST":
      # POST
      content_fields = ['id_user', 'id_network', \
                        'post_text', 'vid_link', \
                        'img_link']
      req_obj = type('', (), {})()
      req_obj.form = request.get_json()
      req_obj.form["id_user"] = g.user.id
      req_obj.get_json = lambda: None
      return execute_post_by_table(req_obj, content_fields, "posts")
    else:
      # PUT
      return execute_put_by_id(request, "posts")


@posts.route("/<post_id>/reply", methods=["POST", "PUT"])
@auth.login_required
def make_new_post_reply(post_id):
    if request.method == "POST":
        # POST
        content_fields = ['id_parent', 'id_user', 'id_network', 'reply_text']
        # First, we make a generic object so we can set attributes (via .form as opposed to ['form'])
        req_obj = type('', (), {})()
        req_obj.form = request.get_json()
        req_obj.form["id_user"] = g.user.id
        req_obj.get_json = lambda: None
        return execute_post_by_table(req_obj, content_fields, "post_replies")
    else:
      # PUT
      return execute_put_by_id(request, "post_replies")

