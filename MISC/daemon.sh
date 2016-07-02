#!/bin/bash
# /etc/init.d/daemon

typeset -x PID=$(pgrep tac_plus)

do_start() {
        if [ -f /tmp/pyopneaaa.lock ]
        then
                /usr/local/sbin/tac_plus ./MISC/TACACS &
                sleep 0.3
        else
                /usr/local/sbin/tac_plus ./MISC/TACACS &
                sleep 0.3
				PID=$(pgrep tac_plus)
                echo "Starting PyOpenAAA..."				
				echo "$PID" > /tmp/pyopneaaa.lock
        fi
}

do_stop() {
        kill -15 $PID 2>/dev/null &
        echo "Stopping PyOpenAAA..."
		rm /tmp/pyopneaaa.lock 2> /dev/null
}		

do_restart() {
        if [ -f /tmp/pyopneaaa.lock ]
        then
                kill -15 $PID 2>/dev/null &
                echo "Restarting PyOpenAAA."
                sleep 3
                /usr/local/sbin/tac_plus ./MISC/TACACS &
        else
                do_start
        fi
}

case "$1" in
        start)
                do_start
                ;;
        stop)
                do_stop
                ;;
        restart)
                do_restart
                ;;
        status)
                if [ -f /tmp/pyopneaaa.lock ]
                then
                        echo "PyOpenAAA is running...
Process:
$PID"
                else
                        echo "PyOpenAAA is stopped."
                fi
                ;;
        *)
                echo "Usage: ./pyopenaaa (start|stop|restart|status)"
                ;;
esac