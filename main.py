import random
import time
import os
import sys
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageDraw, ImageFont, ImageTk
import threading
import requests
import json
from zhdate import ZhDate  # 需要先安装：pip install zhdate

def resource_path(relative_path):
    """ 获取资源的绝对路径 """
    try:
        # PyInstaller创建临时文件夹，将路径存储在_MEIPASS中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class FortuneGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title('AI抽签模拟器')
        self.window.geometry('400x800')
        
        # 设置窗口样式
        self.window.configure(bg='#F0F8FF')
        
        # 创建标题
        title = tk.Label(
            self.window,
            text='AI抽签模拟器',
            font=('华文楷体', 24),
            bg='#F0F8FF',
            fg='#4A4A4A'
        )
        title.pack(pady=20)
        
        # 创建说明文字
        desc = tk.Label(
            self.window,
            text='点击下方按钮开始抽签',
            font=('微软雅黑', 12),
            bg='#F0F8FF',
            fg='#666666'
        )
        desc.pack(pady=10)
        
        # 创建抽签按钮
        self.draw_button = tk.Button(
            self.window,
            text='开始抽签',
            font=('微软雅黑', 14),
            command=self.draw_fortune,
            width=15,
            height=2,
            bg='#4A4A4A',
            fg='white',
            relief='flat'
        )
        self.draw_button.pack(pady=20)
        
        # 创建卡片显示区域
        self.card_label = tk.Label(
            self.window,
            bg='#F0F8FF'
        )
        self.card_label.pack(pady=10)
        
        # 创建退出按钮
        quit_button = tk.Button(
            self.window,
            text='退出',
            font=('微软雅黑', 10),
            command=self.window.quit,
            width=10,
            bg='#F0F8FF',
            fg='#666666',
            relief='flat'
        )
        quit_button.pack(pady=10)
        
        # Kimi API 配置
        self.kimi_api_key = "sk-qMMYH2hTpfRWrAbQqN7ZUCDjBH7XMHcAAvWIXBXLx79OUYpy"
        self.kimi_api_url = "https://api.moonshot.cn/v1/chat/completions"
        
        # 设置窗口图标
        try:
            icon_path = resource_path("icon.ico")
            self.window.iconbitmap(icon_path)
        except:
            pass
            
    def generate_fortune(self, level):
        """使用Kimi生成签文和解释"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.kimi_api_key}"
        }
        
        prompt = f"""请以幽默风趣的方式生成一个{level}运势的签文和解释。
要求：
1. 签文：4-8个字的古风格言
2. 解释：用现代年轻人的视角，用生活化的比喻来解释这个运势
3. 风格要诙谐有趣，略带一点"致郁系"的批判性
4. 解释要用比喻的方式，比如"就像xxx一样..."

格式如下：
签文：[4-8字的古风格言]
解释：[200个字符以内的现代年轻人视角的解释]    

示例：
签文：云开雾散，柳暗花明
解释：就像删掉前任微信的那一刻，人生豁然开朗。命运的代码终于开始不报错了。"""

        data = {
            "model": "moonshot-v1-8k",
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个擅长写幽默签文的AI，特别了解年轻人的生活。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.8
        }

        try:
            response = requests.post(self.kimi_api_url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            content = result['choices'][0]['message']['content'].strip()
            
            # 解析返回的文本
            lines = content.split('\n')
            sign = lines[0].replace('签文：', '').strip()
            explanation = lines[1].replace('解释：', '').strip()
            
            return sign, explanation
            
        except Exception as e:
            print(f"Kimi API调用失败: {str(e)}")
            raise

    def create_fortune(self):
        # 定义运势等级及其权重
        weights = {
            '大吉': 0.1,
            '中吉': 0.3,
            '小吉': 0.3,
            '平': 0.2,
            '凶': 0.1
        }
        
        # 根据权重随机选择运势等级
        fortune_level = random.choices(
            list(weights.keys()),
            weights=list(weights.values())
        )[0]
        
        try:
            # 使用Kimi生成签文和解释
            fortune_text, explanation = self.generate_fortune(fortune_level)
        except Exception as e:
            print(f"AI生成失败: {e}")
            # 如果AI生成失败，使用备用的预设内容
            fallback_fortunes = {
                '大吉': ('云开雾散，柳暗花明', '就像删掉前任微信的那一刻，人生豁然开朗。'),
                '中吉': ('春风化雨，润物无声', '好运来得像个靠谱的室友，不声不响帮你打扫了房间。'),
                '小吉': ('守得云开，见月明朗', '像是熬夜追剧时突然发现快递还没签收，虽有小波折但终见转机。'),
                '平': ('宁静致远，淡定自若', '像是周一收到周五才需要的工作安排，慌也没用，不如先喝杯咖啡。'),
                '凶': ('暂遇困境，静待转机', '像是发现钱包丢了但还没有被盗刷，危机中暗藏转机。记得及时挂失。')
            }
            fortune_text, explanation = fallback_fortunes[fortune_level]
        
        return fortune_level, fortune_text, explanation

    def draw_fortune(self):
        # 禁用按钮并显示等待状态
        self.draw_button.config(state='disabled')
        self.draw_button.config(text='正在抽签...')
        self.window.update()
        
        # 使用线程避免界面卡顿
        def generate():
            level, text, explanation = self.create_fortune()
            self.window.after(0, lambda: self.update_display(level, text, explanation))
        
        threading.Thread(target=generate, daemon=True).start()

    def update_display(self, level, text, explanation):
        # 生成并显示卡片
        self.create_and_display_card(level, text, explanation)
        
        # 恢复按钮
        self.draw_button.config(state='normal')
        self.draw_button.config(text='再抽一次')

    def create_and_display_card(self, level, text, explanation):
        # 创建图片
        width, height = 400, 600
        margin = 20
        
        # 蒙德里安风格的背景色
        bg_colors = ['#FFFFFF', '#F5F5F5', '#FAFAFA']
        accent_colors = {
            '大吉': '#E63946',  # 红色
            '中吉': '#F4A261',  # 橙色
            '小吉': '#2A9D8F',  # 青色
            '平': '#457B9D',    # 蓝色
            '凶': '#6D6875'     # 灰色
        }
        
        # 创建画布
        image = Image.new('RGB', (width, height), random.choice(bg_colors))
        draw = ImageDraw.Draw(image)
        
        try:
            # 使用相对路径加载字体
            title_font = ImageFont.truetype(resource_path('fonts/STXINGKA.TTF'), 42)
            level_font = ImageFont.truetype(resource_path('fonts/simkai.ttf'), 36)
            text_font = ImageFont.truetype(resource_path('fonts/simkai.ttf'), 28)
            explanation_font = ImageFont.truetype(resource_path('fonts/simkai.ttf'), 18)
            date_font = ImageFont.truetype(resource_path('fonts/simkai.ttf'), 20)
        except:
            # 备用字体处理
            try:
                # 尝试使用系统字体
                title_font = ImageFont.truetype('simhei.ttf', 42)
                level_font = ImageFont.truetype('simhei.ttf', 36)
                text_font = ImageFont.truetype('simhei.ttf', 28)
                explanation_font = ImageFont.truetype('simhei.ttf', 18)
                date_font = ImageFont.truetype('simhei.ttf', 20)
            except:
                title_font = ImageFont.load_default()
                level_font = ImageFont.load_default()
                text_font = ImageFont.load_default()
                explanation_font = ImageFont.load_default()
                date_font = ImageFont.load_default()
        
        # 绘制现代风格的装饰线条
        accent_color = accent_colors[level]
        draw.rectangle([(0, 0), (8, height)], fill=accent_color)  # 左侧强调条
        
        # 增加顶部留白，调整标题位置
        title_y = margin + 50  # 增加顶部留白
        draw.text((width/2, title_y), '今日运势', font=title_font, fill='#2F2F2F', anchor='mm')
        
        # 绘制公历日期
        date_y = title_y + 60
        date_str = datetime.now().strftime('%Y年%m月%d日  %H:%M:%S')
        draw.text((width/2, date_y), date_str, font=date_font, fill='#666666', anchor='mm')
     
        # 添加农历日期
        try:
            # 获取当前日期
            today = datetime.now()
            # 转换为农历
            lunar_date = ZhDate.from_datetime(today)
            # 格式化农历日期
            lunar_str = lunar_date.chinese()
            # 使用小一号的字体
            lunar_font = ImageFont.truetype('simkai.ttf', 16)
            draw.text((width/2, date_y + 30), f"农历 {lunar_str}", 
                     font=lunar_font, fill='#888888', anchor='mm')
        except:
            # 如果农历转换失败，使用空格占位保持布局
            pass
        
        # 调整分隔线位置
        line_y = date_y + 60  # 根据农历日期调整位置
        draw.line([(margin+20, line_y), (width-margin-20, line_y)], 
                 fill='#DDDDDD', width=1)
        
        # 调整运势等级位置
        level_y = line_y + 50
        draw.text((width/2, level_y), level, font=level_font, 
                 fill=accent_color, anchor='mm')
        
        # 调整签文位置
        sign_y = level_y + 70
        draw.text((margin+40, sign_y-10), '"', font=text_font, 
                 fill=accent_color, anchor='mm')
        sign_lines = self.wrap_text(text, text_font, width-margin*4)
        for line in sign_lines:
            draw.text((width/2, sign_y), line, font=text_font, 
                     fill='#2F2F2F', anchor='mm')
            sign_y += 40
        draw.text((width-margin-40, sign_y-30), '"', font=text_font, 
                 fill=accent_color, anchor='mm')
        
        # 调整解释文本区域位置
        explanation_y = sign_y + 30
        explanation_box_padding = 20
        lines = self.wrap_text(explanation, explanation_font, width-margin*4)
        
        # 计算剩余空间，确保解释文本区域不会超出底部
        remaining_height = height - explanation_y - margin
        text_height = len(lines) * 25
        box_height = min(text_height + explanation_box_padding * 2, 
                        remaining_height - explanation_box_padding)
        
        # 自动调整字体大小
        while text_height > remaining_height - explanation_box_padding:
            explanation_font_size -= 1  # 减小字体大小
            explanation_font = ImageFont.truetype(resource_path('fonts/simkai.ttf'), explanation_font_size)
            lines = self.wrap_text(explanation, explanation_font, width-margin*4)
            text_height = len(lines) * 25
        
        # 绘制解释文本背景
        draw.rectangle([
            (margin+20, explanation_y),
            (width-margin-20, explanation_y + text_height + explanation_box_padding * 2)
        ], fill='#F8F8F8')
        
        # 绘制解释文本
        text_y = explanation_y + explanation_box_padding
        for line in lines:
            if text_y + 25 > height - margin - explanation_box_padding:
                break
            draw.text((width/2, text_y), line, font=explanation_font, 
                     fill='#4F4F4F', anchor='mm')
            text_y += 25
        
        # 显示图片
        photo = ImageTk.PhotoImage(image)
        self.card_label.configure(image=photo)
        self.card_label.image = photo

    def wrap_text(self, text, font, max_width):
        """改进的文本自动换行函数"""
        words = text
        lines = []
        line = ''
        for char in words:
            # 检查添加下一个字符是否会超出宽度
            if font.getlength(line + char) <= max_width:
                line += char
            else:
                lines.append(line)
                line = char
        if line:  # 添加最后一行
            lines.append(line)
        return lines

if __name__ == '__main__':
    app = FortuneGUI()
    app.window.mainloop() 

    