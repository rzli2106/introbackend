import json

from flask import Flask, request, jsonify

app = Flask(__name__)

posts = {
    #1: {"post_id": 1, "upvotes": "1" "title": "a", "link": "b", "username": "rzli2106"}
}

comments_on_post = {}

post_id_counter = 0

post_comment_id_counter = 0


@app.route("/")
def reddit():
    return "Hello, welcome to Reddit"

# your routes here

# get all post
@app.route("api/posts/")
def get_posts():
        res = {"posts": list(posts.values())}
        return json.dumps(res), 200

# create a post
@app.route("api/posts/", methods=["POST"])
def create_post():
     global post_id_counter

     body = json.loads(request.data)
     title = body["title"]
     link = body["link"]
     username = body["username"]

     if title not in body or link not in body or username not in body:
          return json.dumps({"error": "Missing title, link or username"}), 404

     post = {"id": post_id_counter, "upvotes": 1, "title": title, "link": link,  "username": username}

     posts[posts_id_counter] = post
     comments_on_post[posts_id_counter] = []
     posts_id_counter += 1
     return json.dumps(posts), 201

# get a specific post
@app.route("api/posts/<int:post_id>")
def get_post(post_id):
     post = posts.get(post_id)
     if not post:
          return json.dumps({"error": "Post not found"}), 404
     return json.dumps(post), 200


# delete a specific
@app.route("api/posts/<int:post_id>/", methods = ["DELETE"])
def delete_post(post_id):
     post = posts.get(post_id, None)
     if not post:
          return json.dumps({"error": "Post not found"}), 404
     del posts[post_id]
     return json.dumps(post), 200

#Get comments for a specific post
@app.route("api/posts/<int:post_id>/comments/")
def get_comments(post_id):
     post = posts.get(post_id)
     if not post:
          return json.dumps({"error": "Post does not exist"}), 404
     return json.dumps(comments_on_post[post_id]), 200

#Post a comment for a specific post
@app.route("api/posts/<int:post_id>/comments/", methods=["POST"])
def post_comment(post_id):
     global post_comment_id_counter

     post = posts.get(post_id)
     if not post:
          return json.dumps({"error": "Post does not exist"}), 404
     body = json.loads(request.data)
     text = body["text"]
     username = body["username"]

     if text not in body or username not in body:
          return json.dumps({"error": "Missing body or username"}), 404

     comment = {"id": post_comment_id_counter, "upvotes": 1, "text": text, "username": username}

     comments_on_post[post.id].append(comment)
     post_comment_id_counter += 1

     return json.dumps(comment), 201

#Edit a comment for a specific post
@app.route("api/posts/<int:post_id>/comments/<int:comment_id>", methods = ["POST"])
def edit_comment(post_id, comment_id):
     if post_id not in posts:
          return json.dumps({"error": "Post does not exist"}), 404
     
     body = json.loads(request.data)
     text = body["text"]
     if text not in body:
          return json.dumps({"error": "Editing comment requires text"}), 404
     
     for comment in comments_on_post[post_id]:
          if comment["id"] == comment_id:
               comment["text"] = body["text"]
               return json.dumps(comment), 200



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
