from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flaskapp import db, login_manager, app
from flask_login import UserMixin
import timeago
# import random


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


followers = db.Table('followers',
    db.Column('user_id', db.Integer, db.ForeignKey('users.uid')),  # noqa: E501 E128
    db.Column('follows_id', db.Integer, db.ForeignKey('users.uid'))  # noqa: E501 E128
)


likes = db.Table('likes',
    db.Column('post_id', db.Integer, db.ForeignKey('posts.pid')),  # noqa: E501 E128
    db.Column('user_id', db.Integer, db.ForeignKey('users.uid'))  # noqa: E501 E128
)


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    uid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(32), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False,
                           default='default.jpg')

    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)

    follows = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.user_id == uid),
        secondaryjoin=(followers.c.follows_id == uid),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    notifs = db.relationship('Notif', backref='notif_for', lazy=True)

    notif_count = db.Column(db.Integer, default=0)

    def get_notifs(self):
        if self.new_notif():
            limit = len(self.notifs) - self.notif_count
            # print(len(self.notifs), self.notif_count)
            notifs = self.notifs[-limit:]
            notifs.reverse()
            return notifs

    def get_old_notifs(self):
        limit = len(self.notifs) - self.notif_count

        self.notif_count = len(self.notifs)
        db.session.commit()

        if limit == 0:
            notifs = self.notifs[-4:]
        else:
            notifs = self.notifs[-4:-limit]
        notifs.reverse()
        return notifs

    def new_notif(self):
        return len(self.notifs) > self.notif_count

    def post_count(self):
        return len(self.posts)

    def get_id(self):
        return self.uid

    def is_following(self, user):
        notifs = self.follows.filter(followers.c.follows_id == user.uid).count()  # noqa: E501
        return notifs > 0

    def follow(self, user):
        if self.uid != user.uid:
            if not self.is_following(user):
                self.follows.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.follows.remove(user)

    def get_followers(self, user):
        return User.query.filter(User.follows.any(uid=user.uid)).all()

    def get_followers_count(self, user):
        return len(self.get_followers(user))

    def get_followed_posts(self):
        fw_users = [user.uid for user in self.follows.all()]
        fw_users.append(self.uid)       # to include my own posts
        # print(fw_users)
        fw_posts = Post.query.order_by(Post.date_posted.desc()).filter(Post.user_id.in_(fw_users))  # noqa: E501
        return fw_posts

    # def get_user_suggestion(self):
    #     user_follows = self.follows
    #     avoid = [user.uid for user in user_follows]
    #     avoid.append(self.uid)

    #     available_users = User.query.filter(User.uid.notin_(avoid)).all()
    #     if len(available_users) == 0:
    #         return []
    #     elif len(available_users) <= 2:
    #         return available_users

    #     # find sugg users
    #     suggs = []
    #     while len(suggs) < 2:
    #         index = random.randint(0, len(available_users)-1)
    #         user = available_users[index]
    #         if user not in suggs:
    #             suggs.append(user)

    #     # print(suggs)
    #     return suggs
    def get_user_suggestion(self):
        user_follows = self.follows
        avoid = [user.uid for user in user_follows]
        avoid.append(self.uid)

        available_users = User.query.filter(User.uid.notin_(avoid)).all()
        if len(available_users) == 0:
            return []

        # Sort available users by the number of followers in descending order
        available_users.sort(key=lambda user: user.followers.count(),
                             reverse=True)

        # Return the top 3 users with the most followers
        return available_users[:3]

    def get_reset_token(self, expires_sec=300):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.uid}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:  # noqa: E722
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.password}', '{self.image_file}')"  # noqa: E501


class Post(db.Model):
    __tablename__ = 'posts'
    pid = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    media = db.Column(db.String(32), nullable=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # noqa: E501
    user_id = db.Column(db.Integer, db.ForeignKey('users.uid'), nullable=False)

    liked = db.relationship("User", secondary=likes)
    comments = db.relationship('Comment', backref='post', lazy=True)
    notifs = db.relationship('Notif', backref='post', lazy=True)

    def get_likes_count(self):
        return len(self.liked)

    def user_liked(self, user):
        return user in self.liked

    def like_post(self, user):
        if user not in self.liked:
            self.liked.append(user)
            return "like"
        else:
            self.unlike_post(user)
            return "unlike"

    def unlike_post(self, user):
        self.liked.remove(user)

    def comments_count(self):
        return len(self.comments)

    def get_comments(self, limit=0):
        if limit > 0:
            return self.comments[-limit:]

    def get_timeago(self):
        now = datetime.now()
        return timeago.format(self.date_posted, now)

    def __repr__(self):
        return f"Post('{self.content}', '{self.date_posted}')"


class Comment(db.Model):
    __tablename__ = 'comments'
    cid = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.pid'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.uid'), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)   # noqa: E501

    def __repr__(self):
        return f"Comment({self.post_id}, {self.user_id}, '{self.content}', '{self.date_posted}')"  # noqa: E501


class Notif(db.Model):
    __tablename__ = 'notifs'
    nid = db.Column(db.Integer, primary_key=True)
    msg = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.pid'), nullable=False)
    for_uid = db.Column(db.Integer, db.ForeignKey('users.uid'), nullable=False)
    author = db.Column(db.String(20), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # noqa: E501

    @staticmethod
    def add_notif(user, post, n_type):
        notif_for = post.author.uid
        n = Notif(for_uid=notif_for, post_id=post.pid, msg=n_type, author=user.username)  # noqa: E501
        return n

    def __repr__(self):
        return f"{self.author} {self.msg} your post({self.post_id})"
