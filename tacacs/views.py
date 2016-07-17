import subprocess
import os
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .mysql import *
from .create_pwd import create_tac_pwd
from .create_config_file import create_config_file
from .account import import_to_database


def login_page(request):

    if request.method == 'POST':

        user = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=user, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('index')
            else:
                # Return a 'disabled account' error message
                return render(request, 'registration/login.html', {'account_status': 'disable'})
        else:
            # Return an 'invalid login' error message.
            return render(request, 'registration/login.html', {'account_status': 'invalid'})

    else:
        return render(request, 'registration/login.html', {})


def logout_page(request):
    logout(request)
    return redirect('/')


def restart_process():
    subprocess.call(["MISC/daemon.sh restart"], shell=True)


def check_process():
    status = subprocess.Popen(['ps -A | grep tac_plus'], shell=True, stdout=subprocess.PIPE)
    return status.stdout.read().decode("utf-8")


def index(request):

    if not request.user.is_authenticated():
        return render(request, 'registration/login.html', {})

    statistics = select("""SELECT
    (SELECT COUNT(*) FROM users ) as users,
    (SELECT COUNT(*) FROM groups ) as groups,
    (SELECT COUNT(*) FROM cmd_sets ) as cmd_sets,
    (SELECT count(*) FROM access WHERE start_stop = 'start') as access,
    (SELECT count(*) FROM account) as account""")

    if request.method == 'POST':

        form = request.POST

        if form['job'] == 'apply_config':

            f = open('MISC/TACACS', 'w+')
            f.write(create_config_file())
            f.close()

            print(os.path.dirname(os.path.realpath(__file__)))

            restart_process()

            return render(request, 'tacacs/index.html', {'statistics': statistics,
                                                         'status': check_process()})
        else:
            return render(request, 'tacacs/index.html', {'statistics': statistics,
                                                         'status': check_process()})

    else:

        return render(request, 'tacacs/index.html', {'statistics': statistics,
                                                     'status': check_process()})


def change_pwd(request):

    message = ""

    if request.method == 'POST':

        form = request.POST

        hash = select("SELECT passwd FROM users WHERE user_name = '{0}'".format(form['username']))

        if hash:
            hash = hash[0][0]
            old_pwd = create_tac_pwd(form['password'])

            if old_pwd != hash:
                message = "invalid"

            elif form['new_password'] != form['new_password_again']:
                message = "different"

            else:
                new_pwd = create_tac_pwd(form['new_password'])
                update("UPDATE users SET passwd = '{0}' WHERE user_name = '{1}'".format(new_pwd, form['username']))
                message = "success"

    return render(request, 'registration/change_pwd.html', {'message': message})


def users(request):

    if not request.user.is_authenticated():
        return render(request, 'registration/login.html', {})

    user_list = select("""SELECT u.user_id, u.user_name, g.group_name
    FROM users u INNER JOIN groups g ON u.group_id = g.group_id ORDER BY g.group_name""")

    group_list = select("""SELECT group_id, group_name FROM groups""")

    if request.method == 'POST':
        form = request.POST

        if form['job'] == 'create_user':
            insert("""INSERT INTO `users` (`user_name`, `group_id`, `passwd`) VALUES ('{0}', '{1}', '{2}')"""
                   .format(form['username_add'], form['group_id'], create_tac_pwd(form['password_add'])))

            user_list = select("""SELECT u.user_id, u.user_name, g.group_name
            FROM users u INNER JOIN groups g ON u.group_id = g.group_id ORDER BY g.group_name""")

            return render(request, 'tacacs/users/users.html', {'user_list': user_list})

        if form['job'] == 'edit_user':
            user_name_groupid = select("""SELECT user_name, group_id FROM users  WHERE user_id='{0}'"""
                                       .format(form['user_id_edit']))

            return render(request, 'tacacs/users/edit_user.html', {'user': user_name_groupid[0][0],
                                                                   'group': user_name_groupid[0][1],
                                                                   'groups': group_list,
                                                                   'user_id': form['user_id_edit']})

        if form['job'] == 'save_user':
            update("""UPDATE users SET passwd = '{0}', group_id ='{1}' WHERE user_id = '{2}'"""
                   .format(create_tac_pwd(form['new_password']), form['new_group'], form['username_edit']))

            user_list = select("""SELECT u.user_id, u.user_name, g.group_name
            FROM users u INNER JOIN groups g ON u.group_id = g.group_id ORDER BY g.group_name""")

            return render(request, 'tacacs/users/users.html', {'user_list': user_list})

        if form['job'] == 'delete_user':
            delete("""DELETE FROM users WHERE user_id = '{0}'""".format(form['user_id_del']))

            user_list = select("""SELECT u.user_id, u.user_name, g.group_name
            FROM users u INNER JOIN groups g ON u.group_id = g.group_id ORDER BY g.group_name""")

            return render(request, 'tacacs/users/users.html', {'user_list': user_list})

    if '/tacacs/users/create_user.html' in request.path:
        return render(request, 'tacacs/users/create_user.html', {'groups': group_list})

    else:
        return render(request, 'tacacs/users/users.html', {'user_list': user_list})


def groups(request):

    if not request.user.is_authenticated():
        return render(request, 'registration/login.html', {})

    if request.method == 'POST':
        form = request.POST

        if form['job'] == 'create_group':
            insert("""INSERT INTO groups (group_name, cmd_set_id , priv_lvl, idle_time, timeout)
            VALUES ('{0}', '{1}', '{2}', '{3}', '{4}')"""
                   .format(form['group_add'], form['cmd_set_id'], form['priv_lvl'], form['idle_time'], form['timeout']))

            group_list = select("""SELECT g.group_id, g.group_name, g.priv_lvl, g.idle_time, g.timeout, cs.cmd_set_name
            FROM groups g INNER JOIN cmd_sets cs ON g.cmd_set_id = cs.cmd_set_id ORDER BY g.group_name""")

            return render(request, 'tacacs/groups/groups.html', {'group_list': group_list})

        if form['job'] == 'edit_group':
            group_edit = select("""SELECT g.group_id, g.group_name, cs.cmd_set_name, g.priv_lvl, g.idle_time, g.timeout
            FROM groups g INNER JOIN cmd_sets cs ON g.cmd_set_id = cs.cmd_set_id
            WHERE group_id = '{0}' ORDER BY g.group_name""".format(form['group_id']))

            cmd_set_list = select("""SELECT DISTINCT cmd_set_id, cmd_set_name FROM cmd_sets""")

            return render(request, 'tacacs/groups/edit_group.html', {'group_id': group_edit[0][0],
                                                                     'group_name': group_edit[0][1],
                                                                     'sel_cmd_set_id': group_edit[0][2],
                                                                     'priv_lvl': group_edit[0][3],
                                                                     'idle_time': group_edit[0][4],
                                                                     'timeout': group_edit[0][5],
                                                                     'cmd_set_list': cmd_set_list,
                                                                     'range': range(1, 16)})

        if form['job'] == 'save_group':
            update("""UPDATE groups SET cmd_set_id = '{0}', priv_lvl = '{1}', idle_time ='{2}', timeout = '{3}'
            WHERE group_id = '{4}'"""
                   .format(form['cmd_set_id'], form['priv_lvl'], form['idle_time'], form['timeout'], form['group_id']))

            group_list = select("""SELECT g.group_id, g.group_name, g.priv_lvl, g.idle_time, g.timeout, cs.cmd_set_name
            FROM groups g INNER JOIN cmd_sets cs ON g.cmd_set_id = cs.cmd_set_id ORDER BY g.group_name""")

            return render(request, 'tacacs/groups/groups.html', {'group_list': group_list})

        if form['job'] == 'delete_group':

            delete("""DELETE FROM groups WHERE group_id = '{0}'""".format(form['group_del']))

            group_list = select("""SELECT g.group_id, g.group_name, g.priv_lvl, g.idle_time, g.timeout, cs.cmd_set_name
            FROM groups g INNER JOIN cmd_sets cs ON g.cmd_set_id = cs.cmd_set_id ORDER BY g.group_name""")

            return render(request, 'tacacs/groups/groups.html', {'group_list': group_list})

    if '/tacacs/groups/create_group.html' in request.path:
        cmd_set_list = select("SELECT DISTINCT cmd_set_id, cmd_set_name FROM cmd_sets")

        return render(request, 'tacacs/groups/create_group.html', {'cmd_set_list': cmd_set_list,
                                                                   'range': range(1, 16)})

    else:
        group_list = select("""SELECT g.group_id, g.group_name, g.priv_lvl, g.idle_time, g.timeout, cs.cmd_set_name
        FROM groups g INNER JOIN cmd_sets cs ON g.cmd_set_id = cs.cmd_set_id ORDER BY g.group_name""")
        
        return render(request, 'tacacs/groups/groups.html', {'group_list': group_list})


def cmd_sets(request):

    if not request.user.is_authenticated():
        return render(request, 'registration/login.html', {})

    if request.method == 'POST':

        form = request.POST

        if form['job'] == 'edit_cmd_set':

            cmd_list = select("""SELECT cs.cmd_set_id, cs.cmd_set_name, cs.cmd_default_action,
            c.cmd_order,c.action,c.cmd,c.parameter
            FROM cmds c INNER JOIN cmd_sets cs ON c.cmd_set_id = cs.cmd_set_id
            WHERE cs.cmd_set_name = '{0}' ORDER BY c.cmd_order""".format(form['cmd_set_name']))

            return render(request, 'tacacs/cmd_sets/edit_cmd_set.html', {'cmd_list': cmd_list, 
                                                                         'cmd_set_id': cmd_list[0][0], 
                                                                         'name': cmd_list[0][1], 
                                                                         'default_action': cmd_list[0][2]})

        if form['job'] == 'save_cmd_set':

            update("""UPDATE cmd_sets SET cmd_default_action = '{0}' WHERE cmd_set_id = '{1}'"""
                   .format(form['default_action'], form['cmd_set_id']))

            delete("""DELETE FROM cmds WHERE cmd_set_id = '{0}'""".format(form['cmd_set_id']))

            for i in range(1, int(form['num_lines']) + 1):
                insert("""INSERT INTO cmds (`cmd_set_id`, `cmd_order`, `action`, `cmd`, `parameter`)
                VALUES ('{0}', '{1}', '{2}', '{3}', '{4}')"""
                       .format(form['cmd_set_id'], form['order_' + str(i)], form['action_' + str(i)],
                               form['command_' + str(i)], form['parameter_' + str(i)]))

            cmd_set_list = select("SELECT cmd_set_name, cmd_default_action FROM cmd_sets ORDER BY cmd_set_name")

            return render(request, 'tacacs/cmd_sets/cmd_sets.html', {'cmd_set_list': cmd_set_list})

        if form['job'] == 'create_cmd_set':

            insert("""INSERT INTO cmd_sets (`cmd_set_name`, `cmd_default_action`)
            VALUES ('{0}','{1}')""".format(form['cmd_set_name'], form['default_action']))

            cmd_id = select("SELECT cmd_set_id FROM cmd_sets WHERE cmd_set_name = '{0}'".format(form['cmd_set_name']))

            for i in range(1, int(form['num_lines']) + 1):
                insert("""INSERT INTO cmds (`cmd_set_id`, `cmd_order`, `action`, `cmd`, `parameter`)
                VALUES ('{0}', '{1}', '{2}', '{3}', '{4}')"""
                       .format(cmd_id[0][0],
                               form['order_' + str(i)],
                               form['action_' + str(i)],
                               form['command_' + str(i)],
                               form['parameter_' + str(i)]))

            cmd_set_list = select("SELECT cmd_set_name, cmd_default_action FROM cmd_sets ORDER BY cmd_set_name")

            return render(request, 'tacacs/cmd_sets/cmd_sets.html', {'cmd_set_list': cmd_set_list})

        if form['job'] == 'delete_cmd_set':

            cmd_set_id = select("""SELECT cmd_set_id FROM cmd_sets
            WHERE cmd_set_name = '{0}'""".format(form['cmd_set_name']))

            delete("DELETE FROM cmds WHERE cmd_set_id = '{0}'".format(cmd_set_id))

            delete("DELETE FROM cmd_sets WHERE cmd_set_name = '{0}'".format(form['cmd_set_name']))

            cmd_set_list = select("SELECT cmd_set_name, cmd_default_action FROM cmd_sets")
            return render(request, 'tacacs/cmd_sets/cmd_sets.html', {'cmd_set_list': cmd_set_list})

    if '/tacacs/cmd_sets/create_cmd_set.html' in request.path:
        return render(request, 'tacacs/cmd_sets/create_cmd_set.html', {})

    else:
        cmd_set_list = select("SELECT cmd_set_name, cmd_default_action FROM cmd_sets ORDER BY cmd_set_name")
        return render(request, 'tacacs/cmd_sets/cmd_sets.html', {'cmd_set_list': cmd_set_list})


def logs(request):

    if not request.user.is_authenticated():
        return render(request, 'registration/login.html', {})

    try:
        import_to_database("/var/log/tac_plus/account.log")

    except FileNotFoundError:
        print("Log File Not Found!")

    if request.method == 'POST':

        form = request.POST

        if '/tacacs/logs/logs_by_logon.html' in request.path:
            logon = select("""SELECT task_id as task, timestamp as login,device_ip as device,
            server_ip as srv, username as user, tty as term,
            (SELECT timestamp FROM access WHERE timestamp > login AND task_id = task AND start_stop = 'stop'
            AND username = user  AND server_ip = srv AND device_ip = device AND tty = term LIMIT 1) as logout
            FROM access WHERE start_stop = 'start' AND timestamp BETWEEN '{0} 00:00:00' AND '{1} 23:59:59'
            ORDER BY login DESC ;"""
                           .format(form['from_logon'], form['to_logon']))

            return render(request, 'tacacs/logs/logs_by_logon.html', {'logon': logon})

        if '/tacacs/logs/logs_by_cmd.html' in request.path:
            form = request.POST

            if form['logout'] != "":
                commands = select("""SELECT timestamp, timezone, priv_lvl, cmd
                FROM account WHERE timestamp BETWEEN '{0}' AND '{1}' ORDER BY timestamp DESC;"""
                                  .format(form['login'], form['logout']))
            else:
                commands = select("""SELECT timestamp, timezone, priv_lvl, cmd
                    FROM account WHERE timestamp > '{0}' ORDER BY timestamp DESC""".format(form['login']))

            return render(request, 'tacacs/logs/logs_by_cmd.html', {'commands': commands})

    else:
        logon = select("""SELECT timestamp as login, device_ip as device, server_ip as srv,
            username as usr, tty as term, task_id as task,
            (SELECT timestamp FROM access WHERE timestamp > login AND start_stop = 'stop' AND device_ip = device AND
            server_ip = srv AND username = usr AND task_id = task AND tty = term LIMIT 1 ) as logout FROM access
            WHERE start_stop = 'start' ORDER BY login DESC LIMIT 5;""")

        return render(request, 'tacacs/logs/logs.html', {'logon': logon})


def settings(request):

    if not request.user.is_authenticated():
        return render(request, 'registration/login.html', {})

    config = select("SELECT * FROM settings")

    if request.method == 'POST':

        form = request.POST

        login_msg = form['login_msg'].replace("\\n", "\\\\n")
        login_msg = login_msg.replace("\\t", "\\\\t")

        update("UPDATE settings SET shared_key = '{0}',  login_msg = '{1}', fail_msg = '{2}', time_zone = '{3}', "
               "custom_config = '{4}'".format(form['shared_key'],
                                              login_msg,
                                              form['fail_msg'],
                                              form['time_zone'],
                                              form['custom_config']))

        config = select("SELECT * FROM settings")

        return render(request, 'tacacs/settings/settings.html', {'pre_shared_key': config[0][0],
                                                                 'login_msg': config[0][1],
                                                                 'fail_msg': config[0][2],
                                                                 'time_zone': config[0][3],
                                                                 'custom_config': config[0][4],
                                                                 'status': 'save'})

    return render(request, 'tacacs/settings/settings.html', {'pre_shared_key': config[0][0],
                                                             'login_msg': config[0][1],
                                                             'fail_msg': config[0][2],
                                                             'time_zone': config[0][3],
                                                             'custom_config': config[0][4],
                                                             'status': ''})


def help_page(request):

    if not request.user.is_authenticated():
        return render(request, 'registration/login.html', {})

    else:
        return render(request, 'help/help.html', {})
