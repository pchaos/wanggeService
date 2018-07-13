# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : tags.py

Description : table with n items per row using custom modulo tag
As a quick, simple way to take a list of items make a table with n items per row I added a custom template filter for modulo of an integer.

To make the custom filter first create a "templatetags" directory in your application folder then add an empty file called "init.py" in that new directory. Finally add a file "tags.py" with the above code in it.

In the template you load your custom filter with {% load tags %} and then you can make a table with n elements per row using a simple for loop and in if statement.

This works because if ( for_loop.counter modulo n ) is zero ("if not" evaluates to True on zero values), then it makes a new table row. You might note that if the number of items in list is a multiple of n, there will be an empty row at the end... preventing that adds needless complexity so I left that out!

#put following in your template and change mod:5
#according to the number of cells per table row desired

{% load tags %}

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
import datetime

register = template.Library()


@register.filter(name='mod')
def mod(value, arg):
    """ 取模

    :param value:
    :param arg:
    :return:
    """
    return value % arg


@register.filter(name='diefu')
def diefu(value, arg):
    """ 计算跌幅
    计算公式： (value - arg) / value * 100%

    :param value:
    :param arg:
    :return:  arg相对value的跌幅百分比
    """
    if value:
        return round((value - arg) / value * 100, 2)
    else:
        return None


@register.filter(name='diffday')
def diffday(startDay, endDay):
    """ 计算startDay与endDay之间的间隔天数
    计算公式： (endDay - startday).days

    :param startDay:
    :param endDay:
    :return:  startDay与endDay之间的间隔天数
    """
    if startDay and endDay:
        return (endDay - startDay).days
    else:
        return None


@register.filter(name='changePage')
def changePage(url, page):
    """ 重新组织page格式

    :param url:
    :param page:
    :return:
    """
    pg = 'page='
    if page:
        if pg in url:
            params = url[url.index(pg):].split('&')
            s = ''
            for para in params:
                if not (pg in para):
                    s += para + '&'
            s += 'page={}'.format(page)
            return url[:url.index(pg)] + s
        else:
            # 没有显式page页
            if '?' in url:
                s = url + '&page={}'.format(page)
            else:
                s = url + '?page={}'.format(page)
            return s
    else:
        return url


@register.filter(name='addDays')
def addDays(day, days):
    """ 计算day+days天
        计算公式

    :param day:
    :param days:
    :return:
    """
    if day:
        return day + datetime.timedelta(days=days)
    return day


@register.filter(name='range')
def _range(_min, args=None):
    """ Usage:

{% load tags %}

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
