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
