import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import os

# Глобальные переменные для хранения исходного изображения
original_image = None
current_image = None

def display_image(img):
    """Функция отображает изображение внутри интерфейса Tkinter."""
    global img_label
    if img is not None:
        # OpenCV использует BGR, а Tkinter и Pillow требуют RGB
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_pil.thumbnail((800, 600))
        img_tk = ImageTk.PhotoImage(image=img_pil)
        
        # Обновляем картинку в существующем виджете
        img_label.config(image=img_tk)
        img_label.image = img_tk  # Чтобы фото не удалялось из памяти

def load_image():
    """Функция загружает изображение с диска."""
    global original_image, current_image
    file_path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.jpg *.jpeg *.png")]
    )
    if file_path:
        try:
            file_path = os.path.normpath(file_path)
            original_image = cv2.imread(file_path)
            if original_image is None:
                raise Exception("Не удалось прочитать файл изображения.")
            current_image = original_image.copy()
            display_image(current_image)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить изображение:\n{str(e)}")

def capture_camera():
    """Функция для снимка с веб-камеры."""
    global original_image, current_image
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Ошибка", "Не удалось получить доступ к веб-камере.")
        return
    
    ret, frame = cap.read()
    cap.release()
    
    if ret:
        original_image = frame
        current_image = original_image.copy()
        display_image(current_image)
        messagebox.showinfo("Успех", "Снимок с веб-камеры успешно сделан.")
    else:
        messagebox.showerror("Ошибка", "Не удалось сделать снимок.")

def show_channel():
    """Функция показывает выбранный цветовой канал (R, G, B) от исходного изображения."""
    global original_image, current_image
    if original_image is None:
        messagebox.showinfo("Информация", "Сначала загрузите или захватите изображение.")
        return
    
    channel = simpledialog.askstring("Канал", "Введите канал (R, G или B):")
    if not channel:
        return
    
    channel = channel.upper()
    if channel not in ['R', 'G', 'B']:
        messagebox.showerror("Ошибка", "Некорректный канал. Введите R, G или B.")
        return
    
    # Всегда берем каналы от исходного изображения
    r, g, b = cv2.split(original_image)
    zero = np.zeros_like(b)
    
    if channel == 'B':
        current_image = cv2.merge([b, zero, zero])
    elif channel == 'G':
        current_image = cv2.merge([zero, g, zero])
    elif channel == 'R':
        current_image = cv2.merge([zero, zero, r])
        
    display_image(current_image)
    

def crop_image():
    """Функция выполняет обрезку изображения, по введённым значениям пользователя."""
    global current_image
    if current_image is None:
        messagebox.showinfo("Информация", "Сначала загрузите или захватите изображение.")
        return
    try:
        height, width = current_image.shape[:2]
        x_str = simpledialog.askstring("Обрезка", f"Введите начальный X (0-{width}):")
        if not x_str: return
        y_str = simpledialog.askstring("Обрезка", f"Введите начальный Y (0-{height}):")
        if not y_str: return
        w_str = simpledialog.askstring("Обрезка", "Введите ширину области:")
        if not w_str: return
        h_str = simpledialog.askstring("Обрезка", "Введите высоту области:")
        if not h_str: return
        
        x, y, w, h = int(x_str), int(y_str), int(w_str), int(h_str)
        if x < 0 or y < 0 or w <= 0 or h <= 0 or (x + w) > width or (y + h) > height:
            messagebox.showerror("Ошибка", "Координаты выходят за пределы изображения.")
            return
            
        current_image = current_image[y:y+h, x:x+w]
        display_image(current_image)
    except ValueError:
        messagebox.showerror("Ошибка", "Пожалуйста, введите корректные целые числа.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось обрезать изображение:\n{str(e)}")

def enhance_brightness():
    """Функция повышает яркость изображения, по введёному значению от пользователя."""
    global current_image
    if current_image is None:
        messagebox.showinfo("Информация", "Сначала загрузите или захватите изображение.")
        return
    value_str = simpledialog.askstring("Яркость", "Введите значение увеличения яркости (0-255):")
    if not value_str: return
    try:
        value = int(value_str)
        if value < 0 or value > 255:
            messagebox.showerror("Ошибка", "Значение должно быть в диапазоне от 0 до 255.")
            return
        
        current_image = np.clip(current_image.astype(np.int32) + value, 0, 255).astype(np.uint8)
        display_image(current_image)
    except ValueError:
        messagebox.showerror("Ошибка", "Пожалуйста, введите целые число.")

def draw_circle():
    """Функция рисует круг красным цветом (пользователь задёт радиус и координаты)."""
    global current_image
    if current_image is None:
        messagebox.showinfo("Информация", "Сначала загрузите или захватите изображение.")
        return
    try:
        height, width = current_image.shape[:2]
        x_str = simpledialog.askstring("Круг", f"Введите X центра (0-{width}):")
        if not x_str: return
        y_str = simpledialog.askstring("Круг", f"Введите Y центра (0-{height}):")
        if not y_str: return
        r_str = simpledialog.askstring("Круг", "Введите радиус круга:")
        if not r_str: return
        
        cx, cy, radius = int(x_str), int(y_str), int(r_str)
        if radius <= 0:
            messagebox.showerror("Ошибка", "Радиус должен быть больше нуля.")
            return
            
        cv2.circle(current_image, (cx, cy), radius, (0, 0, 255), 2)
        display_image(current_image)
    except ValueError:
        messagebox.showerror("Ошибка", "Пожалуйста, введите целые числа.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось нарисовать круг:\n{str(e)}")

def reset_image():
    """Функция сбрасывает изменения до исходного состояния."""
    global original_image, current_image
    if original_image is not None:
        current_image = original_image.copy()
        display_image(current_image)
    else:
        messagebox.showinfo("Информация", "Нет загруженного изображения для сброса.")

# Инициализация GUI интерфейса
root = tk.Tk()
root.title("Image Processing App")
root.resizable(True, True)

# Верхний фрейм для панели кнопок
btn_frame = tk.Frame(root)
btn_frame.pack(pady=15, padx=15, fill=tk.X)
tk.Button(btn_frame, text="Загрузить изображение", command=load_image).pack(side=tk.LEFT, padx=4)
tk.Button(btn_frame, text="Сделать снимок с веб-камеры", command=capture_camera).pack(side=tk.LEFT, padx=4)
tk.Button(btn_frame, text="Показать канал", command=show_channel).pack(side=tk.LEFT, padx=4)
tk.Button(btn_frame, text="Обрезка изображения", command=crop_image).pack(side=tk.LEFT, padx=4)
tk.Button(btn_frame, text="Повысить яркость", command=enhance_brightness).pack(side=tk.LEFT, padx=4)
tk.Button(btn_frame, text="Нарисовать круг", command=draw_circle).pack(side=tk.LEFT, padx=4)
tk.Button(btn_frame, text="Сбросить", command=reset_image).pack(side=tk.LEFT, padx=4)

# Элемент для вывода изображения прямо внутри главного окна
img_label = tk.Label(root, text="Изображение не загружено", bg="gray", width=80, height=25)
img_label.pack(pady=10, padx=15, expand=True, fill=tk.BOTH)

root.mainloop()