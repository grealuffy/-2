import json
import urllib.parse
import tkinter as tk
from tkinter import ttk
import requests
from bs4 import BeautifulSoup
import os
import markdown
import re
import html2text
import sys
from tkinter import *
from tkinter import messagebox
from ttkthemes import ThemedTk
import time
import threading
from tkinter import filedialog
# -*- coding: utf-8 -*-

headers = {
    "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.76",
    "Cookie" : "__client_id=2360b421df2f527b41ed60839427e7b9ce944580; login_referer=https%3A%2F%2Fwww.luogu.com.cn%2Fproblem%2FP1021; _uid=1093704"
}
def convert_html_to_markdown(html_content):
    # 创建HTML转换器
    converter = html2text.HTML2Text()
    # 输出Markdown中的链接应该包含在<>中。
    # 如果不需要，可以删除或者注释掉下面这行
    converter.wrap_links = False
    # 转换HTML为Markdown
    markdown_text = converter.handle(html_content)
    return markdown_text
def extract_strings(input_str):
    # 使用非贪婪匹配(?:.*?)和re.DOTALL标志来匹配包括换行符在内的所有字符
    pattern = r'"(.*?)"'
    return re.findall(pattern, input_str, re.DOTALL)
# URL和选择器应该根据实际目标站点修改
def fetch_questions(year,dif,keywords):
    questions=[]
    keywords=str(keywords)
    for start_num in range (1000,1050,1):
        q_id=f"P{start_num}"
        response0 = requests.get(f"https://www.luogu.com.cn/problem/P{start_num}", headers=headers)
        html0=response0.content
        soup0 = BeautifulSoup(html0, 'html.parser')
        all_titles0 = soup0.findAll("title")
        all_titles1 = soup0.findAll("script")
        if year!="全部年份":
            for title in all_titles0:
                link=str(title.string)
                if link.find(year)!=-1:
                    flag=1
                    break
                else:
                    flag=0
                    break
        else:
            flag=1
        if flag==0:
            continue
        for title in all_titles0:
            link=str(title.string)
            if link.find(keywords)!=-1:
                flag=1
                break
            else:
                flag=0
                break
        if flag==0:
            continue
        if dif!=-1:
            for title in all_titles1:
                if title.string is not None:
                    strings=extract_strings(str(title.string))
                    string=str(strings[0])
                    encoded_data=string
                    decoded_data = urllib.parse.unquote(encoded_data)
                    decoded_data = decoded_data.replace('\/','/')
                    unicode_decoded_data = decoded_data.encode('utf-8').decode('unicode_escape')
                    formatted_data = json.dumps(unicode_decoded_data,indent=4,ensure_ascii=False)
                    pattern0 = r'\\"difficulty\\":(\w+)'
                    matches0 = re.findall(pattern0, formatted_data)
                    if int(matches0[0])==dif:
                        flag=1
                        break
                    else:
                        flag=0
                        break
        elif dif==-1:
            flag=1
        if flag==0:
            continue
        for title0 in all_titles0:
            title1=title0.string
            questions.append({'id': q_id,'title': title1,})
    return questions

def save_questions(questions, year,difficulty, keywords):
    if year!="全部年份":
        folder_name = f"{difficulty}-{year}-{keywords}"
    else:
        folder_name = f"{difficulty}-{keywords}"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    print(questions)
    for q in questions:
        response0 = requests.get(f"https://www.luogu.com.cn/problem/{q['id']}", headers=headers)
        html0=response0.content
        soup0 = BeautifulSoup(html0, 'html.parser')
        q_folder = os.path.join(folder_name, f"{q['id']}-{q['title']}")
        if not os.path.exists(q_folder):
            os.makedirs(q_folder)
        with open(os.path.join(q_folder, f"{q['id']}-{q['title']}.md"), 'w',encoding='utf-8') as f:
            f.write(convert_html_to_markdown(str(soup0)))
        print('题目解码结果已保存为Markdown文件:', f"{q['id']}-{q['title']}.md")
        response = requests.get(f"https://www.luogu.com.cn/problem/solution/{q['id']}", headers=headers)
        html=response.content
        soup = BeautifulSoup(html, 'html.parser')
        all_titles = soup.findAll("script")
        pattern2 = r'%22id%22%3A(.*?)%2C%22identifier'
        for title in all_titles:
            if title.string is not None:
                strings=extract_strings(str(title.string))
                string=str(strings[0])
                id = re.findall(pattern2,string)
                response2 = requests.get(f"https://www.luogu.com.cn/blog/_post/{id[0]}", headers=headers)
                html2=response2.content
                soup2 = BeautifulSoup(html2, 'html.parser')
                with open(os.path.join(q_folder, f"{q['id']}-{q['title']}-题解.md"), 'w',encoding='utf-8') as f:
                    f.write(convert_html_to_markdown(str(soup2)))
                print('题解解码结果已保存为Markdown文件:', f"{q['id']}-{q['title']}-题解.md")

# 获取输入并开始爬虫
def fetch_and_save():
    if not save_path.get():
        messagebox.showwarning("警告", "请先选择保存路径!")
        return
    difficulty = difficulty_var.get()
    keywords = keyword_entry.get()
    year = year_var.get()
    # 记录代码运行开始时间
    start_time = time.time()
    if difficulty == "暂无评定":
        dif = 0
    elif difficulty == "入门":
        dif = 1
    elif difficulty == "普及-":
        dif = 2
    elif difficulty == "普及/提高-":
        dif = 3
    elif difficulty == "普及+/提高":
        dif = 4
    elif difficulty == "提高+/省选-":
        dif = 5
    elif difficulty == "省选/NOI-":
        dif = 6
    elif difficulty == "NOI/NOI+/CTSC":
        dif = 7
    else:
        dif = -1
    
    questions = fetch_questions(year, dif, keywords)
    total_questions = len(questions)
    save_count = 0

    for question in questions:
        save_questions([question], year,difficulty, keywords)
        save_count += 1
        progress = int((save_count / total_questions) * 100)
        progress_var.set(progress)
        time.sleep(0.1)  # 控制进度条刷新速度，可以根据实际情况调整
     # 记录代码运行结束时间
    end_time = time.time()

    # 计算代码运行时间
    run_time = end_time - start_time

    # 输出代码运行时间
    print(f"代码运行时间：{run_time:.5f}秒")
    messagebox.showinfo("提示：", "已完成全部筛选并保存在相应目录下")  # 完成操作后的提示信息
   

def start_fetching_thread():
    thread = threading.Thread(target=fetch_and_save)
    thread.start()

root = ThemedTk(theme='arc')  # 使用'arc'主题
root.title('题目爬取窗口')
root.geometry('600x400')  # 设定默认大小

# 配置样式
style = ttk.Style()
style.configure('TButton', font=('Arial', 12, 'bold'))
style.configure('TLabel', font=('Arial', 12))

frame = ttk.Frame(root, padding='10 10 10 10')  # 增加了padding间距
frame.grid(column=0, row=0, sticky=(W, E, N, S))
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# 年份
year_var = StringVar()
year_var.set('全部年份')
year_label = ttk.Label(frame, text='年份:')
year_label.grid(column=0, row=0, sticky=W)
year_options = ['全部年份', '全部年份','2023', '2022', '2021', '2020','2019', '2018', '2017', '2016','2015', '2014', '2013', '2012','2011', '2010', '2009', '2008','2007', '2006', '2005', '2004','2003', '2002', '2001', '2000','1999', '1998', '1997']
year_menu = ttk.OptionMenu(frame, year_var, *year_options)
year_menu.grid(column=1, row=0, sticky=W)

# 难度
difficulty_var = StringVar()
difficulty_var.set('所有难度')
difficulty_label = ttk.Label(frame, text='难度:')
difficulty_label.grid(column=2, row=0, sticky=W)
difficulty_options = ['所有难度','所有难度', '暂无评定', '入门',
                      '普及-', '普及/提高-', '普及+/提高', '提高+/省选-', '省选/NOI-', 'NOI/NOI+/CTSC']
difficulty_menu = ttk.OptionMenu(frame, difficulty_var, *difficulty_options)
difficulty_menu.grid(column=3, row=0, sticky=W)

# 关键字
keyword_label = ttk.Label(frame, text='关键词:')
keyword_label.grid(column=4, row=0, sticky=W)
keyword_entry = ttk.Entry(frame)
keyword_entry.grid(column=5, row=0, sticky=W+E)

# 进度条
progress_var = DoubleVar()
progress_bar = ttk.Progressbar(frame, variable=progress_var, maximum=100)
progress_bar.grid(column=0, row=1, columnspan=6, sticky=W+E)

# 定义一个变量来储存保存路径
save_path = StringVar()

# 保存路径选择和开始按钮
path_label = ttk.Label(frame, textvariable=save_path)
path_label.grid(column=0, row=4, sticky=W)
choose_button = ttk.Button(frame, text='选择保存路径', command=lambda: save_path.set(filedialog.askdirectory()))
choose_button.grid(column=3, row=4, sticky=W)

# 按钮
fetch_button = ttk.Button(frame, text='开始爬取', style='TButton', command=start_fetching_thread)
fetch_button.grid(column=0, row=2, columnspan=6, pady=10)  # 修改为列跨度为6，以中心对齐

for child in frame.winfo_children():
    child.grid_configure(padx=5, pady=5)  # 增加了水平和垂直间距

root.mainloop()
