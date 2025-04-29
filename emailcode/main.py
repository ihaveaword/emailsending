# 使用 smtplib 模块发送纯文本邮件
import smtplib
import time  # 👈 新增导入
import ssl
from email.message import EmailMessage

BATCH_SIZE = 10  # 👈 每批发送5封
WAIT_TIME = 70   # 批次间隔秒数(建议大于60秒)
SERVER_TIMEOUT = 30  # 服务器超时时间
success_count = 0  # 成功计数

EMAIL_ADDRESS = "z13503876281@163.com"  # 邮箱的地址
EMAIL_PASSWORD = "QAssy32xrDDFVZrf"  # 授权码

# 使用ssl模块的context加载系统允许的证书，在登录时进行验证
context = ssl.create_default_context()

with open(r'E:\desktop\助管工作\邮件\contacts.txt', 'r', encoding='utf-8') as f:
    contacts = [line.strip() for line in f if line.strip()]

# contacts = ['1509853371@qq.com', '1245700643@qq.com']
subject = "你好"
# body = "邮件主体内容"
# msg = EmailMessage()
# msg['subject'] = subject  # 邮件标题
# msg['From'] = EMAIL_ADDRESS  # 邮件发件人
# msg['To'] = contacts  # 邮件的收件人
# msg.set_content(body)  # 使用set_content()方法设置邮件的主体内容

# 读取附件内容（在循环外只需一次读取，避免重复IO操作）
# filename = r'E:\图片\极乐迪斯科\海报.jpg'
# with open(filename, 'rb') as f:
#     filedata = f.read()  # 提前读取附件二进制数据

# 使用同一个SMTP连接批量发送（高效）
for idx in range(0, len(contacts), BATCH_SIZE):
    batch = contacts[idx:idx+BATCH_SIZE]
    print(f"当前批次 {idx // BATCH_SIZE + 1}：处理 {len(batch)} 封邮件")  # 🆕添加批次确认

    try:
        with smtplib.SMTP_SSL("smtp.163.com", 465, context=context) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

            for contact in batch:
                # ------------------------------
                # 每封邮件独立创建对象（关键！）
                # ------------------------------
                msg = EmailMessage()
                msg['Subject'] = subject  # 邮件标题（注意Subject首字母大写规范）
                msg['From'] = EMAIL_ADDRESS
                msg['To'] = contact  # 逐个发送，收件人只能看到自己
                msg.set_content("这是一个邮件发送测试，无需回复")  # 正文内容

                # 添加附件（复用已读取的filedata）
                # msg.add_attachment(
                #     filedata,
                #     maintype='image',
                #     subtype='jpeg',
                #     filename='海报.jpg'  # 可自定义显示的附件名
                # )
                try:
                    smtp.send_message(msg)
                    success_count += 1
                    print(f"[>] 已发送 {success_count} 封 | {contact}")
                except Exception as e:
                    print(f"[!] 发送失败 {contact}：{str(e)}")
            time.sleep(WAIT_TIME)  # 👈正确的等待位置（应在外层with之后）
        # 批次间隔（仅成功批次后等待）
        print(f"—— 完成批次 {idx // BATCH_SIZE + 1} —— 即将等待 {WAIT_TIME}s ——")
        # time.sleep(WAIT_TIME)

    except smtplib.SMTPServerDisconnected:
        print("[!] 连接意外断开，将重连继续发送下一批次...")
        print(f"[!] 批次 {idx // BATCH_SIZE + 1} 连接断开，剩余联系人将继续发送")
        # 自动继续循环执行下一批次
