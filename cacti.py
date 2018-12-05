#!/usr/bin/python
#coding:utf-8

#from subprocess import Popen,PIPE
import re
import os,sys
import paramiko
import xlrd,xlwt
from xlutils.copy import copy
reload(sys)
sys.setdefaultencoding('utf-8') #set default encoding to utf-8

class GetLinuxMessage:
#登录远程Linux系统
    def session(self, host, port="22", username="root", password="123456"):

        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, int(port), username, password)
            print "Login %s is successful" % host
            return ssh
        except Exception as e:
            print e.message
#获取Linux主机名
    def get_hostname(self,client):
        cmd_hostname = "hostname"
        #client = self.session(host, port, username, password)
        stdin, stdout, stderr = client.exec_command(cmd_hostname)
        hostname = stdout.read()
        return hostname

#获取Linux网络ipv4信息
#   def get_ifconfig(self, host, port=22, username="root", password="123456"):
#       client = self.session(host, port, username, password)
#       stdin, stdout, stderr = client.exec_command("ifconfig")
#       data = stdout.read()
        #ret = re.compile('((?:1[0-9][0-9]\.)|(?:25[0-5]\.)|(?:2[0-4][0-9]\.)|(?:[1-9][0-9]\.)|(?:[0-9]\.)){3}((1[0-9][0-9])|(2[0-4][0-9])|(25[0-5])|([1-9][0-9])|([0-9]))')
#       ret = re.compile('(?:19[0-9]\.)((?:1[0-9][0-9]\.)|(?:25[0-5]\.)|(?:2[0-4][0-9]\.)|(?:[1-9][0-9]\.)|(?:[0-9]\.)){2}((1[0-9][0-9])|(2[0-4][0-9])|(25[0-5])|([1-9][0-9])|([0-9]))')
#       match = ret.search(data).group()
#       return matchr

#获取Linux系统版本信息
    def get_version(self, client):

        #client = self.session(host, port, username, password)
        stdin, stdout, stderr = client.exec_command("cat /etc/redhat-release")
        data = stdout.read()
        return data
#获取Linux系统CPU信息
    def get_cpu(self, client):

        cpunum = 0
        processor = 0
        #client = self.session(host, port, username, password)
        stdin, stdout, stderr = client.exec_command("cat /proc/cpuinfo")
        cpuinfo = stdout.readlines()
        #with stdout.read() as cpuinfo:
        for i in cpuinfo:
            if i.startswith('physical id'):
                cpunum = i.split(":")[1]
            if i.startswith('processor'):
                processor = processor + 1
            if i.startswith('model name'):
                cpumode = i.split(":")[1]
        return int(cpunum)+1, processor,cpumode

#获取Linux系统memory信息
    def get_memory(self, client):

        #client = self.session(host, port, username, password)
        stdin, stdout, stderr = client.exec_command("cat /proc/meminfo")
        meminfo = stdout.readlines()
        #with open('/proc/meminfo') as meminfo:
        for i in meminfo:
            if i.startswith('MemTotal'):
                memory = int(i.split()[1].strip())
                memory = '%.f' %(memory / 1024.0) + 'MB'
            else:
                pass
        return memory

#获取Linux系统网卡信息
    def get_ethernet(self, client):

        #client = self.session(host, port, username, password)
        stdin, stdout, stderr = client.exec_command("lspci")
        data = stdout.read()
        ret = re.compile('Eth[^\d].*')
        eth = ret.search(data).group()
        return eth
#获取MAC地址
    def get_macaddr(self,client):
        stdin, stdout, stderr = client.exec_command("/sbin/ifconfig")
        for line in stdout:
            if 'Ether' in line:
                mac = line.split()[4]
                break
        return mac

if __name__ == '__main__':
    #打开EXCEL工作表
    filename = 'D:\work\\template_host.xlsx'
    rb = xlrd.open_workbook(filename)
    wb = copy(rb)
    sheet = wb.get_sheet(0)
    row = 3  #起始行
    col = 0  #起始列
    fdown = open('D:\work\\ip_down.txt',"w+")
    fd = open('D:\work\\ip.txt')
    for line in fd:
        host = line.strip()
        #host = raw_input("please input the hostname: ")
        result = GetLinuxMessage()
        try:
            result_client = result.session(host)
            result1 = result.get_hostname(result_client)
        except Exception as e:
            print  "can't connect to %s" %host
            fdown.write(host+"\r\n")
            continue
        # print
        # print ('主机名：%s' %result1.strip())
        # result2 = result.get_ifconfig(host)
        # print ('主机IP：%s' %result2)
        result3 = result.get_version(result_client)
        # print ('版本信息：%s' %result3.strip())
        result4, result5, result6 = result.get_cpu(result_client)
        # print ('物理CPU数量：%s' %result4)
        # print ('逻辑CPU数量：%s' %result5)
        # print ('物理CPU型号：%s' %result6.strip())
        result7 = result.get_memory(result_client)
        # print ('物理内存：%s' %result7)
        result8 = result.get_ethernet(result_client)
        # print ('网卡型号：%s' %result8)
        result9 = result.get_macaddr(result_client)
        info = [result1.strip(),"linux","centos",result3.strip(),"64",result5,result4,result6.strip(),result7.strip(),"",result9.strip(),host ]

        for i in info :
            sheet.write(row, col, i)
            col+=1
        row+=1
        col=0
    os.remove(filename)
    wb.save(filename)
    fdown.close()