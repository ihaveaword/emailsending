from fetch_contacts import get_senders  # 确保文件名正确，若原文件是fetch_concats.py需同步修改导入语句
import csv

# 获取最多1000个发件人，实际可能少于该数（邮箱邮件不足时）
senders = get_senders(max_emails=600)

# ---- 去重核心逻辑 ----
# 方法1: 使用集合去重（无序，速度最快）
# contacts = list(set(senders))

# 方法2: 保留顺序的去重（推荐）
contacts = []
seen = set()  # 用于记录已出现的元素
for sender in senders:
    # 可在此添加额外清理逻辑（如统一转小写、去除前后空格等）
    clean_sender = sender.strip().lower()  # 示例：标准化处理

    if clean_sender not in seen and clean_sender:  # 排除空字符串
        seen.add(clean_sender)
        contacts.append(sender)  # 或用clean_sender根据需求决定

with open("contacts.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(contacts))

# 或保存为CSV

with open("contacts.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["联系人邮箱"])
    writer.writerows([[contact] for contact in contacts])
# ---- 输出结果 ----
print(f"原始发件人数量: {len(senders)}")
print(f"去重后联系人数量: {len(contacts)}")
print("联系人列表:")
print(contacts)
# 保存为文本文件

