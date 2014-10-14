munin-plugins
=============

A set of extra munin plugins



## icinga_health / icinga_multi

The only required configuration option is the `url` parameter:

    [icinga*]
    env.url http://your.server/icinga/cgi-bin/tac.cgi

If your server requires basic authentication, you should use the `user` and `password` setting:

    env.user some-user
    env.password strong-password

If you always get `0.0`, make sure that user has permission on all your services/hosts in Icinga's `cgi.cfg`


*Note:* Do not enable `icinga_health` and `icinga_multi` at the same time - the _multi plugin covers the _health plugin.
