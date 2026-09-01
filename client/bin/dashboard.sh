#!/bin/sh
# KPW1 信息屏客户端 - KUAL 入口
# 使用: 搜索框输入 ;dashboard  或  通过 KUAL 启动

BIN="/mnt/us/kindle-dashboard/bin"
LOG="/mnt/us/kindle-dashboard/dashboard.log"
PIDFILE="/var/run/dashboard.pid"

mkdir -p "$(dirname $LOG)"

is_running() {
    [ -f "$PIDFILE" ] && kill -0 "$(cat $PIDFILE)" 2>/dev/null
}

start() {
    if is_running; then
        echo "Already running (pid $(cat $PIDFILE))"
        return
    fi
    nohup "$BIN/dashboard-daemon.sh" >> "$LOG" 2>&1 &
    echo $! > "$PIDFILE"
    echo "Started (pid $(cat $PIDFILE))"
}

stop() {
    if [ -f "$PIDFILE" ]; then
        kill "$(cat $PIDFILE)" 2>/dev/null
        rm -f "$PIDFILE"
        echo "Stopped"
    else
        echo "Not running"
    fi
}

status() {
    if is_running; then
        echo "Running (pid $(cat $PIDFILE))"
        tail -5 "$LOG" 2>/dev/null
    else
        echo "Not running"
    fi
}

fetch_once() {
    "$BIN/fetch-and-show.sh" once
}

case "$1" in
    start) start ;;
    stop) stop ;;
    restart) stop; start ;;
    status) status ;;
    once) fetch_once ;;
    *) echo "Usage: $0 {start|stop|restart|status|once}"; exit 1 ;;
esac