# coding: utf-8

import re
import jinja2


@jinja2.evalcontextfilter
def nl2br(eval_ctx, value):
    newline = re.compile(r'(?:\r\n|\r|\n)+')
    chunks = newline.split(jinja2.escape(value))
    result = jinja2.Markup('<br>\n').join(chunks)
    if eval_ctx.autoescape:
        result = jinja2.Markup(result)
    return result


# Регистрация фильтра
jinja2.filters.FILTERS['nl2br'] = nl2br


class Reporter(object):
    template = '''
        {% for name, mail in team %}
        {% if worklogs[mail] %}
        <b>{{ name }}</b><br>
        <ul>
        {% for worklog in worklogs[mail].values() %}
            <li>
                <a href="{{ worklog.issue.url }}">{{ worklog.issue.key }}: {{ worklog.issue.title }}</a><br>
                {% for comment in worklog.comments %}
                {% if comment %}
                {{ comment | nl2br }}
                {% if not loop.last	%}
                <br>
                {% endif %}
                {% endif %}
                {% endfor %}
            </li>
        {% endfor %}
        </ul>
        {% endif %}
        {% endfor %}
    '''

    def render(self, team, worklogs):
        template = jinja2.Template(self.template)
        return template.render(
            team=team,
            worklogs=worklogs,
        )
