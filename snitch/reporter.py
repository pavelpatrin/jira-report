import collections
import itertools
import jinja2
import re
from . import utils


@jinja2.evalcontextfilter
def nl2br(eval_ctx, value):
    newline = re.compile(r'(?:\r\n|\r|\n)+')
    chunks = newline.split(jinja2.escape(value))
    result = jinja2.Markup('<br>\n').join(chunks)
    if eval_ctx.autoescape:
        result = jinja2.Markup(result)
    return result


# Register filter.
jinja2.filters.FILTERS['nl2br'] = nl2br


class Reporter(object):
    template = '''
        {% for account, title in accounts.items() %}
        {% if mentions[account] %}
        <b>{{ title }}</b>
        <br>
        <ul>
            {% for task in mentions[account] %}
            <li>
                <a href="{{ jira_url }}/browse/{{ task.key }}">
                    {{ task.key }}: {{ task.title }}
                </a>
                {% for operation in histrepr[account][task.key] %}
                {% if operation | trim %}
                <br>{{ operation | trim | nl2br }}
                {% endif %}
                {% endfor %}
            </li>
            {% endfor %}
        </ul>
        {% endif %}
        {% endfor %}
    '''

    def __init__(self, translations):
        self.translations = translations

    def report(self, jira_url, projects, accounts, history):
        mentions = self._mentions(accounts, history)
        histrepr = self._represent(accounts, history)

        return jinja2.Template(
            self.template,
        ).render(
            jira_url=jira_url,
            projects=projects,
            accounts=accounts,
            mentions=mentions,
            histrepr=histrepr,
        )

    def _mentions(self, accounts, history):
        """ Tasks with any type of activity. """
        result = collections.OrderedDict()
        for account in accounts:
            chain = itertools.chain(
                history.get(account, {}).get('active', []),
                history.get(account, {}).get('stream', []),
                history.get(account, {}).get('workon', []),
            )
            result[account] = sorted(
                {info['key']: info for info in chain}.values(),
                key=lambda x: utils.split_key(x['key']),
            )

        return result

    def _represent(self, accounts, history):
        """ Text representation of history. """
        operations = collections.OrderedDict()

        def get_store(store):
            return history.get(account, {}).get(store, [])

        for account in accounts:
            operations[account] = account_ops = collections.OrderedDict()
            self._represent_active(account_ops, get_store('active'))
            self._represent_stream(account_ops, get_store('stream'))
            self._represent_workon(account_ops, get_store('workon'))

        return operations

    def _represent_active(self, account_ops, active):
        for info in self._sort_by_key(active):
            task_ops = account_ops.setdefault(info['key'], [])
            task_ops.append(self.translations['active'])

    def _represent_stream(self, account_ops, stream):
        stream = {
            (item['key'], item['action']):
                item for item in stream
        }.values()
        for info in self._sort_by_key(stream):
            if info['action'] in self.translations:
                task_ops = account_ops.setdefault(info['key'], [])
                task_ops.append(self.translations[info['action']])

    def _represent_workon(self, account_ops, workon):
        for info in self._sort_by_key(workon):
            task_ops = account_ops.setdefault(info['key'], [])
            task_ops.append(info['comment'])

    def _sort_by_key(self, items):
        def key(item):
            return utils.split_key(item['key'])

        return sorted(items, key=key)
