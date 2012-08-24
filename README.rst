django-redis-sessions
=======================
Redis database backend for your sessions


------------
Installation
------------

1. Run ``pip install django-redis-sessions`` or alternatively  download the tarball and run ``python setup.py install``,

For Django < 1.4 run ``pip install django-redis-sessions==0.3``

2. Set ``redis_sessions.session`` as your session engine, like so::

    SESSION_ENGINE = 'redis_sessions.session'

3. Optional settings::

Create a dictionary ``SESSION_REDIS`` in your ``settings.py`` file. The following keys is available.

**HOST**

    Which host to use when connecting to the database. An empty string means localhost.
    If this value starts with a forward slash ('/'), redis will connect via a Unix socket to the specified socket.
    For example::
    
        SESSION_REDIS = {
            'HOST': '/var/run/redis.sock',
        }

**PORT**

    The port to use when connecting to the database.

**PASSWORD**

    The password to use when connecting to the database.

**DB**

    The index of the database to use.

**PREFIX**

    String prefix for keys in the database.

An example::

    SESSION_REDIS = {
        'HOST': '192.168.1.2',
        'PORT': 6739,
        'PASSWORD': '123',
        'DB': 5,
        'PREFIX': 'sessions',
    }

4. That's it

See: http://pypi.python.org/pypi/django-redis-sessions
