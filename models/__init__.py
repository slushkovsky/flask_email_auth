from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

from ..utils import module_member, setting_name

EAuthBase = declarative_base()

class _AppSession(EAuthBase):
    __abstract__ = True

    @classmethod
    def _set_session(cls, app_session):
        cls.app_session = app_session

    @classmethod
    def _session(cls):
        return cls.app_session 


    @classmethod
    def query(cls): 
        return cls._session().query(cls)

from .mail import ConfirmEmailMessage, ResetPasswordMessage
from .user import UserEmailAuth

def _new_model(model, **kw): 
    try: 
        return model(**kw)
    except TypeError as e: 
        extra_kw_name = str(e).split(' ')[0].replace('\'', '')
        kw = {k:v for k,v in kw.items() if k != extra_kw_name}

        return _new_model(model, **kw)


def new_user(model_kw): 
    user = _new_model(UserEmailAuth.user_model, **model_kw)

    _AppSession._session().add(user)
    _AppSession._session().commit()

    return user

def init_email_auth(app, db_session): 
    import os
    import sys
    import jinja2
    from flask_mail import Mail

    sys.path.append('../../')
    DEFAULT_CONFIG = 'flask_email_auth.default.base_config'
    
    __import__(DEFAULT_CONFIG)
    m = sys.modules[DEFAULT_CONFIG]
    merged_config = {k:getattr(m, k) for k in dir(m) if not k.startswith('__')}
    merged_config.update(app.config)

    app.config = merged_config

    User = module_member(app.config[setting_name('USER_MODEL')])
    _AppSession._set_session(db_session)
    
    mail = Mail(app)

    __here = lambda path: os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), path))

    app.jinja_loader = jinja2.ChoiceLoader([
        app.jinja_loader,
        jinja2.FileSystemLoader([__here('../default/templates/')]),
    ])

    UserEmailAuth.user_model = User

    UserEmailAuth.user_id = Column(Integer, ForeignKey(User.id),
                                    nullable=False, index=True)
    # UserEmailAuth.user = relationship(User, backref=backref('email_auth',
                                                             # lazy='dynamic'))

