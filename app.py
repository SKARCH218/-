import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import binascii
import os
import csv

# 개인식별번호 생성 함수
def draw_centered_text(draw, text, font, center_position, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position = (center_position[0] - text_width // 2, center_position[1] - text_height // 2)
    draw.text(position, text, font=font, fill=fill)

def make_ticket(name, grade, template_path, output_path, font_path, publisher, date, seat):
    code = f"{date.year}_{date.month}_{date.day}_{name}_{grade}"
    hex_code = binascii.hexlify(code.encode()).decode()

    base = Image.open(template_path).convert("RGBA")
    draw = ImageDraw.Draw(base)

    font_large = ImageFont.truetype(font_path, 44)
    font_incode = ImageFont.truetype(font_path, 30)
    font_date = ImageFont.truetype(font_path, 44)

    text_color = (0, 50, 0)

    draw_centered_text(draw, grade, font_large, (230, 500), text_color)
    draw_centered_text(draw, seat, font_large, (565, 500), text_color)
    draw_centered_text(draw, hex_code, font_incode, (1280, 500), text_color)

    date_text = f"{date.year}년 {date.month}월 {date.day}일 {publisher}"
    draw_centered_text(draw, date_text, font_date, (330, 712), text_color)

    os.makedirs(output_path, exist_ok=True)
    save_path = os.path.join(output_path, f"{name}_ticket.png")
    base.save(save_path)

    # CSV 기록
    os.makedirs("data", exist_ok=True)
    with open("data/history.csv", "a", newline='', encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow([publisher, name, grade, hex_code, "16진수", seat])

    return save_path

def generate_ticket():
    name = name_entry.get().strip()
    publisher = publisher_entry.get().strip()
    grade = grade_var.get()
    seat = seat_entry.get().strip()

    if not all([name, publisher, seat]):
        messagebox.showerror("오류", "이름, 발행인, 좌석번호를 모두 입력해주세요.")
        return

    if grade not in ["freepass", "freepass+"]:
        messagebox.showerror("오류", "등급을 선택해주세요.")
        return

    if use_today_var.get():
        date = datetime.today()
    else:
        try:
            y = int(year_entry.get())
            m = int(month_entry.get())
            d = int(day_entry.get())
            date = datetime(y, m, d)
        except Exception:
            messagebox.showerror("오류", "유효한 날짜를 입력해주세요.")
            return

    try:
        output_path = "output"
        template_path = os.path.join("template", "template.png")
        font_path = os.path.join("font", "DungGeunMo.ttf")

        save_path = make_ticket(name, grade, template_path, output_path, font_path, publisher, date, seat)
        messagebox.showinfo("완료", f"티켓이 생성되었습니다:\n{save_path}")
    except Exception as e:
        messagebox.showerror("에러 발생", str(e))

def toggle_date_inputs():
    state = "disabled" if use_today_var.get() else "normal"
    year_entry.config(state=state)
    month_entry.config(state=state)
    day_entry.config(state=state)

def toggle_name_selection():
    if use_list_var.get():
        name_entry.config(state="readonly")
        name_combo.config(state="readonly")
        name_entry.delete(0, tk.END)
        name_entry.insert(0, name_combo.get())
    else:
        name_entry.config(state="normal")
        name_combo.config(state="disabled")

def update_name_entry(event):
    if use_list_var.get():
        name_entry.config(state="normal")
        name_entry.delete(0, tk.END)
        name_entry.insert(0, name_combo.get())
        name_entry.config(state="readonly")

def load_names_from_csv(path):
    names = []
    with open(path, encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        next(reader)  # 헤더 스킵
        for row in reader:
            if len(row) >= 3:
                names.append(row[2].strip())
    return names

# ---------------- GUI 구성 -------------------

root = tk.Tk()
root.title("하꼬의숲 프리패스권 이미지 생성기")
root.geometry("450x500")
root.resizable(False, False)

# 이름 선택
tk.Label(root, text="이름").pack(pady=(10, 0))
use_list_var = tk.BooleanVar(value=True)
tk.Checkbutton(root, text="CSV 목록에서 선택", variable=use_list_var, command=toggle_name_selection).pack()

name_combo = ttk.Combobox(root, state="readonly", width=30)
name_combo['values'] = load_names_from_csv("data/data.csv")
name_combo.bind("<<ComboboxSelected>>", update_name_entry)
name_combo.pack()

name_entry = tk.Entry(root, width=30, state="readonly")
name_entry.pack()

# 발행인
tk.Label(root, text="발행인").pack(pady=(10, 0))
publisher_entry = tk.Entry(root, width=30)
publisher_entry.pack()

# 좌석번호
tk.Label(root, text="좌석번호 (예: A1)").pack(pady=(10, 0))
seat_entry = tk.Entry(root, width=10)
seat_entry.pack()

# 등급 선택
tk.Label(root, text="등급 선택").pack(pady=(10, 0))
grade_var = tk.StringVar()
grade_combo = ttk.Combobox(root, textvariable=grade_var, values=["freepass", "freepass+"], state="readonly")
grade_combo.pack()

# 날짜 선택
tk.Label(root, text="날짜 선택").pack(pady=(10, 0))
use_today_var = tk.BooleanVar(value=True)
tk.Checkbutton(root, text="오늘 날짜 사용", variable=use_today_var, command=toggle_date_inputs).pack()

date_frame = tk.Frame(root)
date_frame.pack(pady=(5, 0))

tk.Label(date_frame, text="연도").grid(row=0, column=0)
year_entry = tk.Entry(date_frame, width=5, state="disabled")
year_entry.grid(row=0, column=1, padx=5)

tk.Label(date_frame, text="월").grid(row=0, column=2)
month_entry = tk.Entry(date_frame, width=3, state="disabled")
month_entry.grid(row=0, column=3, padx=5)

tk.Label(date_frame, text="일").grid(row=0, column=4)
day_entry = tk.Entry(date_frame, width=3, state="disabled")
day_entry.grid(row=0, column=5, padx=5)

# 생성 버튼
tk.Button(root, text="티켓 생성", command=generate_ticket, bg="green", fg="white", width=20).pack(pady=20)

# GUI 시작
root.mainloop()
