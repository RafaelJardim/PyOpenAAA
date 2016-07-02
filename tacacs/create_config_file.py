from .mysql import *


def create_cmd_set(var1):
    cmd = select("""SELECT cs.cmd_set_name, c.action, c.cmd, c.parameter,
    cs.cmd_default_action, cs.cmd_set_id
    FROM cmds c INNER JOIN cmd_sets cs ON c.cmd_set_id = cs.cmd_set_id
    WHERE c.cmd_set_id = '{0}'""".format(var1))

    cmd_set_name = []
    action = []
    command = []
    parameter = []
    default_action = []

    for row in range(len(cmd)):
        cmd_set_name.append(cmd[row][0])
        action.append(cmd[row][1])
        command.append(cmd[row][2])
        parameter.append(cmd[row][3])
        default_action.append(cmd[row][4])

    i = 0

    cmd_set = ""
    while i <= len(cmd_set_name) - 1:
        if i == 0:
            cmd_set += "cmd = " + command[i] + " {" + "\n"
            cmd_set += "                " + action[i] + " " + parameter[i] + "\n"

        elif (cmd_set_name[i]) in (cmd_set_name[i - 1]):
            if (command[i]) in (command[i - 1]):
                cmd_set += "                " + action[i] + " " + parameter[i] + "\n"
            else:
                cmd_set += "         }"
                cmd_set += "cmd = " + command[i] + " {" + "\n"
                cmd_set += "                " + action[i] + " " + parameter[i] + "\n"

        elif (cmd_set_name[i]) not in (cmd_set_name[i - 1]):
            cmd_set += "         }\n"

            cmd_set += "default service = " + default_action[i]
            cmd_set += "cmd = " + command[i] + " {" + "\n"
            cmd_set += "                " + action[i] + " " + parameter[i] + "\n"

        if i == (len(cmd_set_name) - 1):
            cmd_set += """       }\n    }"""

        i = (i + 1)

    return cmd_set


def create_config_file():
    settings = select("""SELECT * FROM settings""")

    groups = select("""SELECT g.group_name, g.idle_time, g.timeout,
    g.priv_lvl, cs.cmd_default_action, cs.cmd_set_id FROM groups g INNER JOIN cmd_sets cs ON g.cmd_set_id = cs.cmd_set_id""")

    users = select("""SELECT u.user_name, u.passwd, g.group_name
    FROM users u INNER JOIN groups g ON u.group_id = g.group_id""")

    config = """id = spawnd {{
        listen = {{ port = 49 }}
}}

id = tac_plus {{

    date format = "%Y-%m-%d %H:%M:%S"

    accounting log = /var/log/tac_plus/%Y/%m/%d.log

    accounting log = /var/log/tac_plus/account.log

    retire limit = 1000

    password max-attempts = 3

    host = 0.0.0.0/0 {{
        welcome banner = "{0}"
        failed authentication banner = "{1}"
        key = {2}
    }}\n
""".format(settings[0][1], settings[0][2], settings[0][0])

    for row in groups:
        config += """   group = {0} {{
        default service = permit
        service = shell {{
        set idletime = {1}
        set timeout = {2}
        set priv-lvl = {3}
        default command = {4}
        """.format(row[0], str(row[1]), str(row[2]), str(row[3]), row[4])

        config += create_cmd_set(str(row[5])) + "\n}\n\n"

    for row in users:
        config += """   user = {0} {{
            login = crypt {1}
            member = {2}
    }}\n\n""".format(row[0], row[1], row[2])

    config += "\n}"

    return config
