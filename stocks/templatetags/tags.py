# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : tags.py

Description : table with n items per row using custom modulo tag
As a quick, simple way to take a list of items make a table with n items per row I added a custom template filter for modulo of an integer.

To make the custom filter first create a "templatetags" directory in your application folder then add an empty file called "init.py" in that new directory. Finally add a file "myapp_tags.py" with the above code in it.

In the template you load your custom filter with {% load pictures_tags %} and then you can make a table with n elements per row using a simple for loop and in if statement.

This works because if ( for_loop.counter modulo n ) is zero ("if not" evaluates to True on zero values), then it makes a new table row. You might note that if the number of items in list is a multiple of n, there will be an empty row at the end... preventing that adds needless complexity so I left that out!

#put following in your template and change mod:5
#according to the number of cells per table row desired

{% load pictures_tags %}

<table>
<tr>
{% for item in list %}
  <td>
  <!--CELL CONTENT-->
  </td>
  {% if not forloop.counter|mod:5 %}
    </tr><tr>
  {% endif %}
{% endfor %}
</tr>
</table>

@Author :       pchaos

date：          2018-6-28
-------------------------------------------------
Change Activity:
               2018-6-28:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
__author__ = 'pchaos'

from django import template

register = template.Library()


@register.filter
def mod(value, arg):
    return value % arg


@register.filter(name='range')
def _range(_min, args=None):
    """ Usage:

{% load range %}

<p>stop 5

{% for value in 5|range %}

{{ value }}

{% endfor %}

</p>

<p>start 5 stop 10

{% for value in 5|range:10 %}

{{ value }}

{% endfor %}

</p>

<p>start 5 stop 10 step 2

{% for value in 5|range:"10,2" %}

{{ value }}

{% endfor %}

</p>

Output

<p>stop 5

0 1 2 3 4

</p>

<p>start 5 stop 10

5 6 7 8 9

</p>

<p>start 5 stop 10 step 2

5 7 9

</p>

    :param _min:
    :param args:
    :return:
    """
    _max, _step = None, None
    if args:
        if not isinstance(args, int):
            _max, _step = map(int, args.split(','))
        else:
            _max = args
    args = filter(None, (_min, _max, _step))
    return range(*args)
