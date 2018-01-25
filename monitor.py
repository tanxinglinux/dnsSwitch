# -*- coding: utf-8 -*-

import sys
import time
import json
import codecs
import pyodbc
import urllib2
import os.path

conf = {
    'ROOT': 'D:/server/by_Server_All',
    'SERVER': '10.172.28.67,1433',
    'SERVER_BAK': '10.172.28.81,1433',
    'SERVER_PlatformDB': '10.81.84.163',
    'DATABASE': 'DataBaseBY',
    'UID': 'mgzy',
    'PASSWD': 'VrA4TCCSm9WQx2XL',
    'MAC': 'B2EBEDCE80517F4AEB1AA4E85349247D'
}


def analysis_conf(path):
    config = {}
    result = ''
    content = codecs.open(path, 'r', 'utf-16').read().encode('utf-8')
    for line in content.split('\n'):
        if '网狐棋牌' not in line and '/' not in line and ';' not in line and 3 < len(line.strip()):
            result += line.replace('\r', '') + ' '
    for each in result.split('['):
        if 0 < len(each):
            title = each[:each.index(']')]
            content = each[each.index(']'):].replace(']', '').replace('= ', '=').replace(' =', '=').strip()
            tmp = {}
            for item in content.split(' '):
                tmp[item.split('=')[0].strip()] = item.split('=')[1].strip()
            config[title] = tmp
    return config

addr = []

def analysis_addr(path):
    for line in open(path, 'r').readlines():
        try:
            ip = line[line.index('=') + 1:].strip()
            if 0 < len(ip):
                addr.append(ip)
        except:
            pass
    return addr


def get_online(sid):
    if os.path.isdir('%s/GameServer_%s/Application' % (conf['ROOT'], sid)):
        try:
            return open('%s/GameServer_%s/Application/Online/%s.txt' % (conf['ROOT'], sid, sid), 'r').read()
        except:
            pass
    return 0

def mssql_query(sql):
    try:
        conn = pyodbc.connect('DRIVER={SQL Server}; SERVER=%s; DATABASE=%s; UID=%s; PWD=%s' % (
        conf['SERVER'], conf['DATABASE'], conf['UID'], conf['PASSWD']))
    except:
        conn = pyodbc.connect('DRIVER={SQL Server}; SERVER=%s; DATABASE=%s; UID=%s; PWD=%s' % (
        conf['SERVER_BAK'], conf['DATABASE'], conf['UID'], conf['PASSWD']))
    cursor = conn.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def mssql_PlatformDB(sql):
    try:
        conn = pyodbc.connect('DRIVER={SQL Server}; SERVER=%s; DATABASE=%s; UID=%s; PWD=%s' % (
        conf['SERVER_PlatformDB'], "PlatformDB", "readonly", "9QCZnp2odonfWJsx"))
    except:
        conn = pyodbc.connect('DRIVER={SQL Server}; SERVER=%s; DATABASE=%s; UID=%s; PWD=%s' % (
        conf['SERVER_PlatformDB'], "PlatformDB", conf['UID'], conf['PASSWD']))
    cursor = conn.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def remotecheck(host):
    try:
        return urllib2.urlopen('http://139.199.59.233:15123/remotecheck?host=%s' % host, timeout=25).read()
    except:
        return 2

def get_roommem(sid):
    if os.path.isdir('%s/GameServer_%s/Application' % (conf['ROOT'], sid)):
        try:
            nowtime = time.strftime("%Y-%m-%d", time.localtime())
            path = ('%s/GameServer_%s/Application/Online/mem_%s_%s.txt' % (conf['ROOT'], sid, sid, nowtime))
            with open(path, 'rb') as fh:
                first = next(fh)
                offs = -100
                while True:
                    fh.seek(offs, 2)
                    lines = fh.readlines()
                    if len(lines) > 1:
                        last = lines[-1]
                        break
                    offs *= 2
                a = last.replace("\n", "").rstrip()
                return a[a.index("vir:") + 4:len(a) - 1]

        except:
            pass
    return 0


try:
    if 'room' == sys.argv[1]:
        data = []
        rows = mssql_query(
            "SELECT ServerID, ServerName, ServerPort FROM dbo.GameRoomInfo WHERE ServiceMachine='%s' AND ServerName LIKE '%%]%%'" %
            conf['MAC'])
        for row in rows:
            analysis_addr('%s/GameServer_%s/Application/ServerAddr.ini' % (conf['ROOT'], row.ServerID))

        for each in list(set(addr)):
            tmp = [{"{#SERVERID}": row.ServerID, "{#SERVERNAME}": row.ServerName.encode('utf-8'),
                    "{#SERVERPORT}": row.ServerPort, "{#SLBIP}": each} for row in rows]
            data.extend(tmp)
        print json.dumps({"data": data}, ensure_ascii=False, indent=4)

    elif 'online' == sys.argv[1] and 0 < len(sys.argv[2]):
        print get_online(sys.argv[2])

    elif 'roommem' == sys.argv[1] and 0 < len(sys.argv[2]):
        print get_roommem(sys.argv[2])

    elif 'total' == sys.argv[1]:
        number = 0
        rows = mssql_query(
            "SELECT ServerID FROM dbo.GameRoomInfo WHERE ServiceMachine='%s' AND ServerName LIKE '%%]%%'" % conf['MAC'])
        for each in rows:
            number += int(get_online(each.ServerID))
        print number

    elif 'lcport' == sys.argv[1]:
        data = []
        cport = {}
        if os.path.isdir('%s/CorrespondServer' % conf['ROOT']):
            cport['{#CPORT}'] = \
            analysis_conf('%s/CorrespondServer/Application/ServerParameter.ini' % conf['ROOT'])['Correspond'][
                'ServicePort']
            data.append(cport)
        if os.path.isdir('%s/LoginServer' % conf['ROOT']):
            lport = analysis_conf('%s/LoginServer/Application/ServerParameter.ini' % conf['ROOT'])['LogonServer'][
                'ServicePort']
            lslb = mssql_query('SELECT TOP 1 LoginServer FROM dbo.ClientChannel')[0].LoginServer.split(',')
            for each in lslb:
                if lport in each:
                    tmp = {}
                    tmp['{#LSLBIP}'] = each.replace(':%s' % lport, '').strip()
                    tmp['{#LPORT}'] = lport
                    data.append(tmp)
        print json.dumps({"data": data}, ensure_ascii=False, indent=4)

    elif 'count' == sys.argv[1]:
        print mssql_query("SELECT COUNT(SERVERID) FROM dbo.GameRoomInfo WHERE ServiceMachine='%s' AND ServerName LIKE '%%]%%'" % conf['MAC'])[0][0]

    elif 'sorder' == sys.argv[1]:
        print mssql_PlatformDB("SELECT COUNT(*) FROM PlatformDB.dbo.PPayCoinOrder WHERE PayStatus=2  AND KindID=8 AND DATEDIFF(s,DATEADD(s,convert(int,SuccessTime),'1970-01-01 08:00:00'), GETDATE()) < 1800")[0][0]

    elif 'forder' == sys.argv[1]:
        print mssql_PlatformDB("SELECT COUNT(*) FROM PlatformDB.dbo.PPayCoinOrder WHERE PayStatus=1  AND KindID=8 AND DATEDIFF(s,DATEADD(s,convert(int,CreatedTime),'1970-01-01 08:00:00'), GETDATE()) < 1800")[0][0]

    elif 'x' == sys.argv[1]:
        print mssql_PlatformDB("SELECT SUM(Money) FROM PlatformDB.dbo.PPayCoinOrder WHERE PayStatus=2 AND SuccessTime >=%s" % int(time.mktime(time.strptime(time.strftime('%Y-%m-%d 00:00:00', time.localtime()), '%Y-%m-%d %H:%M:%S'))))[0][0]

    elif 'user' == sys.argv[1]:
        print mssql_query("SELECT COUNT(UserID) FROM dbo.AccountsInfo WHERE IsAndroid <> 1")[0][0]

    elif 'negative' == sys.argv[1]:
        print mssql_query("SELECT COUNT(UserID) FROM dbo.GameScoreInfo WHERE Score < 0")[0][0]

    elif 'portlist' == sys.argv[1]:
        portlist = ""
        rows = mssql_query(
            "SELECT ServerPort FROM dbo.GameRoomInfo WHERE ServiceMachine='%s' AND ServerName LIKE '%%]%%'" % conf[
                'MAC'])
        for row in rows:
            portlist += "%s," % row.ServerPort
        print portlist[:-1]

    elif 'remotecheck' == sys.argv[1]:
        print remotecheck(sys.argv[2])

except Exception, e:
    # print e
    pass

