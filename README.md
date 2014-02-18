blackbird-httpd
===============

[![Build Status](https://travis-ci.org/Vagrants/blackbird-httpd.png?branch=development)](https://travis-ci.org/Vagrants/blackbird-httpd)

get httpd stats by using server-status.

config file
-----------

| name                    | default        | type                | notes                               |
|-------------------------|----------------|---------------------|-------------------------------------|
| host                    | 127.0.0.1      | string              | httpd host                          |
| port                    | 80             | interger(1 - 65535) | httpd lisetn port                   |
| timeout                 | 3              | interger(0 - 600)   | timeout for connection              |
| status_uri              | /server-status | string              | server sttaus uri                   |
| info_uri                | /server-info   | string              | server info   uri                   |
| user                    | None           | string              | username for basic authentication   |
| password                | None           | string              | password for basic authentication   |
| ssl                     | False          | boolean             | use ssl for connection              |
| response_check_host     | 127.0.0.1      | string              | httpd host for L7 response check    |
| response_check_port     | 80             | interger(1 - 65535) | httpd port for L7 response check    |
| response_check_timeout  | 3              | interger(0 - 600)   | timeout for L7 response check       |
| response_check_vhost    | localhost      | string              | httpd vhost for L7 response check   |
| response_check_uagent   | blackbird response check | string    | user agent for L7 response check    |
| response_check_ssl      | False          | boolean             | use ssl for L7 response check       |

Please see the "httpd.cfg"
