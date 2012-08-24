import redis
from django.utils.encoding import force_unicode
from django.contrib.sessions.backends.base import SessionBase, CreateError
from django.conf import settings


class SessionStore(SessionBase):
    """
    Implements Redis database session store.
    """

    def __init__(self, session_key=None):
        super(SessionStore, self).__init__(session_key)

        if hasattr(settings, 'SESSION_REDIS'):
            # Dict config settings

            kwargs = {
                'port': settings.SESSION_REDIS.get('PORT', 6379),
                'db': settings.SESSION_REDIS.get('DB', 0),
                'password': settings.SESSION_REDIS.get('PASSWORD'),
            }

            host = settings.SESSION_REDIS.get('HOST', '')
            if host.startswith('/'):
                # Assume an unix socket path
                kwargs['unix_socket_path'] = host
            else:
                kwargs['host'] = host

            self._key_prefix = settings.SESSION_REDIS.get('PREFIX', '')

        else:
            # Legacy style settings

            kwargs = {
                'port': getattr(settings, 'SESSION_REDIS_PORT', 6379),
                'db': getattr(settings, 'SESSION_REDIS_DB', 0),
                'password': getattr(settings, 'SESSION_REDIS_PASSWORD', ''),
            }

            unix_socket_path = getattr(settings, 'SESSION_REDIS_UNIX_DOMAIN_SOCKET_PATH', None)
            if unix_socket_path is None:
                kwargs['host'] = getattr(settings, 'SESSION_REDIS_HOST', 'localhost')
            else:
                kwargs['unix_socket_path'] = getattr(settings, 'SESSION_REDIS_UNIX_DOMAIN_SOCKET_PATH', '/var/run/redis/redis.sock')

            self._key_prefix = getattr(settings, 'SESSION_REDIS_PREFIX', '')

        self.server = redis.StrictRedis(**kwargs)

    def load(self):
        try:
            session_data = self.server.get(self.get_real_stored_key(self._get_or_create_session_key()))
            return self.decode(force_unicode(session_data))
        except:
            self.create()
            return {}

    def exists(self, session_key):
        return self.server.exists(self.get_real_stored_key(session_key))

    def create(self):
        while True:
            self._session_key = self._get_new_session_key()
            
            try:
                self.save(must_create=True)
            except CreateError:
                continue
            self.modified = True
            return

    def save(self, must_create=False):
        if must_create and self.exists(self._get_or_create_session_key()):
            raise CreateError
        data = self.encode(self._get_session(no_load=must_create))
        if redis.VERSION[0] >= 2:
            self.server.setex(self.get_real_stored_key(self._get_or_create_session_key()), self.get_expiry_age(), data)
        else:
            self.server.set(self.get_real_stored_key(self._get_or_create_session_key()), data)
            self.server.expire(self.get_real_stored_key(self._get_or_create_session_key()), self.get_expiry_age())

    def delete(self, session_key=None):
        if session_key is None:
            if self.session_key is None:
                return
            session_key = self.session_key
        try:
            self.server.delete(self.get_real_stored_key(session_key))
        except:
            pass

    def get_real_stored_key(self, session_key):
        """Return the real key name in redis storage
        @return string
        """

        if not self._key_prefix:
            return session_key
        return ':'.join([self._key_prefix, session_key])
