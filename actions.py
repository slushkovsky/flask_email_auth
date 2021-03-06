from email_auth.exc import LoginFailError, WrongTokenError, \
                           InvalidUserIdError, UnknownEmailError
from email_auth.models import UserEmailAuth, ConfirmEmailMessage, \
                              ResetPasswordMessage

def register_new_user(user, with_confirm=True, next_url=None): 
    UserEmailAuth._add(user)

    if with_confirm: 
        ConfirmEmailMessage._new(user_id=user.id, next=next_url, autosend=True)
    
def check_user(u): 
    try: 
        if UserEmailAuth.query.filer_by(email=u.email).one() != u.password:
            raise LoginFailError()
    except sqlalchemy.orm.exc.NoResultFound:
        raise LoginFailError()


def request_pass_reset(email): 
    try: 
        user = UserEmailAuth.query.filter_by(email=email).one()
    except sqlalchemy.orm.exc.NoResultFound: 
        raise UnknownUserEmailError()

    ForgotPasswordMessage._new(user_id=user.id, autosend=True)

def __get_msg_by_token(token, model): 
    try: 
        return model.query.filter_by(token=token).one()
    except sqlalchemy.orm.exc.NoResultFound: 
        raise WrongTokenError()

def get_confirm_msg(token): 
    return __get_msg_by_token(token, ConfirmEmailMessage)

def get_reset_msg(token):
    return __get_msg_by_token(token, ResetPasswordMessage)

def __get_user_by_msg(msg): 
    try: 
        UserEmailAuth.query.filter_by(id=msg.user_id).one()
    except sqlalchemy.orm.exc.NoResultFound: 
        raise InvalidUserId()

def confirm_user(msg_token): 
    msg = get_confirm_msg(msg_token)
    user = __get_user_by_msg(msg)

    user.confirmed = True

    db.delete(msg) 

    return msg.next

def reset_password_by_msg(msg, new_password): 
    user = get_user_by_msg(msg)
    user.reset_password(new_password)

    db.delete(msg) 

    return msg.next
    

