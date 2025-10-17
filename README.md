之前有一个一直名单，群发邮件的需求。我写了一个程序，
github地址：[https://github.com/ihaveaword/emailsending](https://github.com/ihaveaword/emailsending)
## 两个功能
 - main.py实现功能：已知contacts.txt(联系人)名单，实现群发功能
 - contacts.py：可以提取当前邮箱中收件箱的邮箱号，并进去去重

fetch_contacts.py 定义get_senders函数，可以查询邮箱中的最近多少人给你发消息，亲测设置为1000没有问题，大于几千完全可以使用。
### 注意：
fetch_contacts.py contacts.py放同一文件夹，有函数互相引用
发送时间间隔已经调试好，不要自己随便调，发的太快会被系统判定为垃圾邮箱冻结几小时
登陆代码也是调好了很久，供各位参考

## 核心代码如下
main.py
```bash
# git@github.com:ihaveaword/emailsending.git
# 使用 smtplib 模块发送纯文本邮件
import smtplib
import time  # 👈 新增导入
import ssl
from email.message import EmailMessage
from getpass import getpass

BATCH_SIZE = 10  # 👈 每批发送5封
WAIT_TIME = 70   # 批次间隔秒数(建议大于60秒)
SERVER_TIMEOUT = 30  # 服务器超时时间
success_count = 0  # 成功计数

EMAIL_ADDRESS = input("请输入邮箱地址: ").strip()
EMAIL_PASS=None
if EMAIL_PASS is None:
    # 绕开IDE的getpass显示问题
    print("请在此输入授权码 >>> ", end='', flush=True)  # 强制显示输入提示
    try:
        # 尝试兼容IDE的输入方式
        EMAIL_PASS = input()
    except:
        # 回退到getpass
        EMAIL_PASS = getpass("请输入邮箱授权码: ").strip()

# 使用ssl模块的context加载系统允许的证书，在登录时进行验证
context = ssl.create_default_context()

with open(r'E:\desktop\助管工作\emailsending\emailcode\contacts.txt', 'r', encoding='utf-8') as f:
    contacts = [line.strip() for line in f if line.strip()]

# contacts = ['1509853371@qq.com', '1245700643@qq.com']
subject = "你好"
body = "这是一个邮件发送测试，无需回复"
# msg = EmailMessage()
# msg['subject'] = subject  # 邮件标题
# msg['From'] = EMAIL_ADDRESS  # 邮件发件人
# msg['To'] = contacts  # 邮件的收件人
# msg.set_content(body)  # 使用set_content()方法设置邮件的主体内容

# 读取附件内容（在循环外只需一次读取，避免重复IO操作）
filename = r'E:\图片\极乐迪斯科\海报.jpg'
with open(filename, 'rb') as f:
    filedata = f.read()  # 提前读取附件二进制数据

# 使用同一个SMTP连接批量发送（高效）
for idx in range(0, len(contacts), BATCH_SIZE):
    batch = contacts[idx:idx+BATCH_SIZE]
    print(f"当前批次 {idx // BATCH_SIZE + 1}：处理 {len(batch)} 封邮件")  # 🆕添加批次确认

    try:
        with smtplib.SMTP_SSL("smtp.163.com", 465, context=context) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASS)

            for contact in batch:
                # ------------------------------
                # 每封邮件独立创建对象（关键！）
                # ------------------------------
                msg = EmailMessage()
                msg['Subject'] = subject  # 邮件标题（注意Subject首字母大写规范）
                msg['From'] = EMAIL_ADDRESS  # 邮件发件人
                msg['To'] = contact  # 逐个发送，收件人只能看到自己
                msg.set_content(body)  # 正文内容

                # 添加附件（复用已读取的filedata）
                msg.add_attachment(
                    filedata,
                    maintype='image',
                    subtype='jpeg',
                    filename='海报.jpg'  # 可自定义显示的附件名
                )
                try:
                    smtp.send_message(msg)
                    success_count += 1
                    print(f"[>] 已发送 {success_count} 封 | {contact}")
                except Exception as e:
                    print(f"[!] 发送失败 {contact}：{str(e)}")
            # time.sleep(WAIT_TIME)  # 👈正确的等待位置（应在外层with之后）
        # 批次间隔（仅成功批次后等待）
        print(f"—— 完成批次 {idx // BATCH_SIZE + 1} —— 即将等待 {WAIT_TIME}s ——")
        time.sleep(WAIT_TIME)

    except smtplib.SMTPServerDisconnected:
        print("[!] 连接意外断开，将重连继续发送下一批次...")
        print(f"[!] 批次 {idx // BATCH_SIZE + 1} 连接断开，剩余联系人将继续发送")
        # 自动继续循环执行下一批次
```

fetch_contacts.py

```bas
import imaplib
import time
from email.header import decode_header
from email.utils import parseaddr
import email.message
from email import message_from_bytes
from getpass import getpass

def get_senders(max_emails, EMAIL_USER=None, EMAIL_PASS=None):
    if EMAIL_USER is None:
        EMAIL_USER = input("请输入邮箱地址: ").strip()
    if EMAIL_PASS is None:
        # 绕开IDE的getpass显示问题
        print("请在此输入授权码 >>> ", end='', flush=True)  # 强制显示输入提示
        try:
            # 尝试兼容IDE的输入方式
            EMAIL_PASS = input()
        except:
            # 回退到getpass
            EMAIL_PASS = getpass("请输入邮箱授权码: ").strip()
# def get_senders(max_emails):
    EMAIL_HOST = 'imap.163.com'

    imaplib.Commands = {**imaplib.Commands, 'ID': ('NONAUTH',)}  # 👈 新增此行

    with imaplib.IMAP4_SSL(EMAIL_HOST, 993) as imap:
        def send_imap_id():
            args = (
                b'("name" "myname" "version" "1.0.0" '
                b'"vendor" "myclient" "support-email" "test@test.com")'
            )
            typ, data = imap._simple_command('ID', args)
            if typ != 'OK':
                print("警告：服务器未接受ID参数")

        send_imap_id()

        print("正在登录...")
        imap.login(EMAIL_USER, EMAIL_PASS)
        time.sleep(1)

        print("选择INBOX...")
        status, _ = imap.select('"INBOX"')
        if status != "OK":
            raise Exception(f"选择INBOX失败: {status}")

        status, msg_ids = imap.search(None, "ALL")
        if status != "OK":
            raise Exception("SEARCH失败")

        imap.noop()

        email_ids = msg_ids[0].split()[:max_emails]
        senders = []

        for email_id in email_ids:
            typ, msg_data = imap.fetch(email_id, '(BODY.PEEK[HEADER.FIELDS (FROM)])')

            if typ == "OK" and msg_data and msg_data[0]:
                raw_header = msg_data[0][1]
                msg = message_from_bytes(raw_header)
                # 关键修改：将Header对象转为字符串再解析
                from_header = str(msg.get('From', ''))
                _, addr = parseaddr(from_header)  # parseaddr现在接收字符串
                senders.append(addr)

        return senders

if __name__ == "__main__":
    senders = get_senders(max_emails=10)
    print(f"前{len(senders)}封邮件发件人：")
    for idx, sender in enumerate(senders, 1):
        print(f"{idx}. {sender}")
```

