import re
from .mysql import insert

############
# Patterns #
############

# Regex patterns for timestamps preceding log events that are used to parse
# into epoch time.

RE_TIMESTAMP = r'(?P<timestamp>(?:\d{4}[-]\d{1,2}[-]\d{1,2}\s\S+))\s*'

RE_LINE_COMMAND = (
    RE_TIMESTAMP +
    r'(?P<device_ip>\S+)[\t\s]+'
    r'(?P<username>\w+)[\t\s]+'
    r'(?P<tty>\S+)[\t\s]+'
    r'(?P<server_ip>(?:Unknown host - non-tty|\S+))[\t\s]+'
    r'(?P<start_stop>\w+)[\t\s]+'
    r'task_id=(?P<task_id>\S*)[\t\s]+'  # task_id is sometimes empty
    r'(?P<av_pairs>.*)'             # A/V pairs are always at the end
)

# All of the default patterns in order from most-to-least common.
LINE_PATTERNS = [
    re.compile(RE_LINE_COMMAND),
]

# This is used to capture and split an A/V pair into a list of strings
RE_AV_PAIR = re.compile(r'([^\s]*)[ ]{2,}')


def cleanup_av_pairs(av_pairs, pattern=None):

    if pattern is None:
        pattern = RE_AV_PAIR

    # Generic cleanup
    av_pairs = av_pairs.replace('  ', ' ')  # remove doble space
    av_pairs = av_pairs.replace('\t', '  ')  # tabs to spaces
    av_pairs = av_pairs.replace('process*', 'process=')  # '*' => '='

    # Non-commands don't have spaces and can simply be .split()
    if 'cmd=' not in av_pairs:
        pairs = av_pairs.split()

    # Commands can have spaces so process them w/ regex.
    else:
        pairs = [av for av in pattern.split(av_pairs) if av]  # Skip ''

    return dict(p.split('=') for p in pairs)


def parse_line(line, patterns=None):
    """Parse a ```line`` based against a list of ``patterns``."""
    if patterns is None:
        patterns = LINE_PATTERNS

    for line_re in patterns:
        match = line_re.match(line)
        if match:
            data = match.groupdict()
            av_pairs = data['av_pairs']
            data['av_pairs'] = cleanup_av_pairs(av_pairs)
            return data

    return None


def import_to_database(acccount_file):

    # Filter Lines by Login, Commands and Disconnections

    f = open(acccount_file, 'r+')

    for line in f:
        a = parse_line(line)

        if a:
            if a['start_stop'] == 'start':
                insert("""INSERT INTO access (tty, start_stop, timestamp, device_ip, username,
                server_ip, service, timezone, task_id)
                VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}')"""
                       .format(a['tty'],
                               a['start_stop'],
                               a['timestamp'],
                               a['device_ip'],
                               a['username'],
                               a['server_ip'],
                               a['av_pairs']['service'],
                               a['av_pairs']['timezone'],
                               a['task_id']))

            elif 'disc-cause' in a['av_pairs']:
                insert("""INSERT INTO access (tty, start_stop, timestamp, device_ip, username,
                server_ip, service, timezone, task_id, `disc-cause`, stop_time, elapsed_time,
                `pre-session-time`, `disc-cause-ext`)
                VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}',
                '{8}', '{9}', '{10}', '{11}', '{12}', '{13}')"""
                       .format(a['tty'],
                               a['start_stop'],
                               a['timestamp'],
                               a['device_ip'],
                               a['username'],
                               a['server_ip'],
                               a['av_pairs']['service'],
                               a['av_pairs']['timezone'],
                               a['task_id'],
                               a['av_pairs']['disc-cause'],
                               a['av_pairs']['stop_time'],
                               a['av_pairs']['elapsed_time'],
                               a['av_pairs']['pre-session-time'],
                               a['av_pairs']['disc-cause-ext']))

            elif 'cmd' in a['av_pairs']:
                insert("""INSERT INTO account (tty, start_stop, timestamp, device_ip, username,
                server_ip, service, timezone, task_id, `priv_lvl`, cmd)
                VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', '{10}')"""
                       .format(a['tty'],
                               a['start_stop'],
                               a['timestamp'],
                               a['device_ip'],
                               a['username'],
                               a['server_ip'],
                               a['av_pairs']['service'],
                               a['av_pairs']['timezone'],
                               a['task_id'],
                               a['av_pairs']['priv-lvl'],
                               a['av_pairs']['cmd']))
            else:
                pass

    f.close()

    # Clear account file

    f = open(acccount_file, 'w')
    f.close()
