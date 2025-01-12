from models import db, User

def create_user(email, profile_picture=None):
    new_user = User(email=email, profile_picture=profile_picture)
    db.session.add(new_user)
    db.session.commit()

def get_user_by_email(email):
    user = User.query.filter_by(email=email).first()
    if user:
        return {
            'id': user.id,
            'email': user.email,
            'profile_picture': user.profile_picture
        }
    return None

def update_user_profile_picture(email, profile_picture):
    user = User.query.filter_by(email=email).first()
    if user:
        user.profile_picture = profile_picture
        db.session.commit()
        return True
    return False