import math
import tkinter as tk
from tkinter import ttk, messagebox

import psycopg2




DB_HOST = "localhost"
#DB_PORT = 5433 
DB_PORT = 5432          
DB_USER = "postgres"
DB_PASSWORD = "password"
DB_NAME = "web_database"  
DB_SCHEMA = "gearcalc"     





def create_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname=DB_NAME,
        )
        return conn
    except Exception as e:
        messagebox.showerror("Ошибка БД", f"Не удалось подключиться к Postgres:\n{e}")
        return None


def get_materials(conn):
    """Список материалов для выпадающего списка."""
    try:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT DISTINCT material
                FROM {DB_SCHEMA}.mat_table
                ORDER BY material
            """)
            rows = cur.fetchall()
        return [r[0] for r in rows]
    except Exception as e:
        messagebox.showerror("Ошибка БД", f"Не удалось получить список материалов:\n{e}")
        return []


def get_modules(conn):
    """Список стандартных модулей из module_table."""
    try:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT m
                FROM {DB_SCHEMA}.module_table
                ORDER BY m
            """)
            rows = cur.fetchall()
        return [float(r[0]) for r in rows]
    except Exception as e:
        messagebox.showerror("Ошибка БД", f"Не удалось получить список модулей:\n{e}")
        return []


def get_yf1(conn, z1, x):
    """Коэффициент Yf1 по таблице 1: yf1_table(z1, x, yf1)."""
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT yf1
                FROM {DB_SCHEMA}.yf1_table
                WHERE z1 = %s AND ABS(x - %s) < 1e-6
                LIMIT 1
                """,
                (z1, x),
            )
            row = cur.fetchone()
        if row is None:
            raise ValueError(
                f"В таблице Yf1 не найдено значение для z1={z1}, x={x}. "
                "Проверь таблицу yf1_table."
            )
        return float(row[0])
    except Exception as e:
        raise RuntimeError(f"Ошибка при получении Yf1 из БД: {e}")


def get_material_data(conn, material, load_dir):
    """
    По таблице 2: mat_table(material, load_type, sigma_fp_p, nf0)
    Возвращает σ′fp (sigma_fp_p) и NF0.
    """
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT sigma_fp_p, nf0
                FROM {DB_SCHEMA}.mat_table
                WHERE material = %s AND load_type = %s
                LIMIT 1
                """,
                (material, load_dir),
            )
            row = cur.fetchone()
        if row is None:
            raise ValueError(
                f"Для материала '{material}' и вида нагрузки '{load_dir}' "
                f"нет строки в mat_table."
            )
        sigma = float(row[0])
        nf0 = float(row[1])
        if nf0 <= 0:
            raise ValueError("NF0 в таблице mat_table должно быть > 0.")
        return sigma, nf0
    except Exception as e:
        raise RuntimeError(f"Ошибка при получении данных материала: {e}")


def nearest_module(modules, m_val):
    """Возвращает ближайший стандартный модуль из списка modules."""
    if not modules:
        return m_val
    best = modules[0]
    for m in modules[1:]:
        if abs(m - m_val) < abs(best - m_val):
            best = m
    return best



def parse_float(entry: ttk.Entry, label: str):
    text = entry.get().strip().replace(",", ".")
    if not text:
        raise ValueError(f"Поле «{label}» не заполнено")
    try:
        return float(text)
    except ValueError:
        raise ValueError(f"Поле «{label}» содержит неверное число")


def parse_int(entry: ttk.Entry, label: str):
    text = entry.get().strip()
    if not text:
        raise ValueError(f"Поле «{label}» не заполнено")
    try:
        return int(text)
    except ValueError:
        raise ValueError(f"Поле «{label}» содержит неверное целое число")




def calculate(conn, modules, widgets):
    """
    Выполняет все вычисления и показывает результат.
    widgets – словарь с элементами интерфейса.
    """
    try:
        aw = parse_float(widgets["aw"], "aw (межосевое расстояние)")
        if aw <= 0:
            raise ValueError("aw должно быть > 0")

        beta_deg = parse_float(widgets["beta"], "β (угол)")
        T1 = parse_float(widgets["T1"], "T1 (крутящий момент)")
        if T1 <= 0:
            raise ValueError("T1 должно быть > 0")

        z1n = parse_int(widgets["z1n"], "z1n (предварительное число зубьев)")
        if z1n <= 0:
            raise ValueError("z1n должно быть > 0")

        x = parse_float(widgets["x"], "x (коэффициент смещения)")
        u = parse_float(widgets["u"], "u (передаточное число)")
        if u <= 0:
            raise ValueError("u должно быть > 0")

        bw = parse_float(widgets["bw"], "bw (ширина венца)")
        if bw <= 0:
            raise ValueError("bw должно быть > 0")

        mf = parse_float(widgets["mf"], "mf (параметр mf)")
        if mf <= 0:
            raise ValueError("mf должно быть > 0")

        gear_type = widgets["gear_type"].get().strip()
        axial_mode = widgets["axial_overlap"].get().strip()
        material = widgets["material"].get().strip()
        load_dir = widgets["load_dir"].get().strip()
        load_type = widgets["load_type"].get().strip()

        if not gear_type:
            raise ValueError("Не выбран тип передачи")
        if gear_type == "Косозубая" and not axial_mode:
            raise ValueError("Для косозубой передачи нужно указать коэффициент осевого перекрытия")
        if not material:
            raise ValueError("Не выбран материал")
        if not load_dir:
            raise ValueError("Не выбран вид нагрузки")
        if not load_type:
            raise ValueError("Не выбран тип нагружения")


        if gear_type == "Прямозубая":
            Kma = 1400.0
        elif gear_type == "Шевронная":
            Kma = 850.0
        elif gear_type == "Косозубая":
            if axial_mode == "εβ ≤ 1":
                Kma = 1100.0
            else:
                Kma = 850.0
        else:
            raise ValueError("Неизвестный тип передачи")


        Yf1 = get_yf1(conn, z1n, x)


        sigma_fp_p, NF0 = get_material_data(conn, material, load_dir)

        if load_type == "Постоянная":
            t_hours = parse_float(widgets["thours"], "tч (часы работы)")
            n_rpm = parse_float(widgets["n"], "n (об/мин)")
            if t_hours <= 0 or n_rpm <= 0:
                raise ValueError("tч и n должны быть > 0")
            NFE = 60.0 * t_hours * n_rpm
        else:
            Nsum = parse_float(widgets["Nsum"], "Nсумм (суммарное число циклов)")
            if Nsum <= 0:
                raise ValueError("Nсумм должно быть > 0")

            NFE = 0.0
            sum_nci = 0.0
            for i in range(1, 6):
                eT = widgets[f"T1_{i}"]
                eN = widgets[f"nci_{i}"]
                t_str = eT.get().strip().replace(",", ".")
                n_str = eN.get().strip().replace(",", ".")
                if not t_str and not n_str:
                    continue 

                try:
                    T1i = float(t_str)
                    nci = float(n_str)
                except ValueError:
                    raise ValueError(f"Неверные данные ступени {i} (T1i или nci)")

                if T1i <= 0 or nci <= 0:
                    raise ValueError(f"T1i и nci на ступени {i} должны быть > 0")

                sum_nci += nci
                NFE += (T1i / T1) ** mf * nci


            if NFE <= 0:
                raise ValueError("Эквивалентное число циклов NFE получилось ≤ 0")

            if abs(sum_nci - Nsum) > 0.01 * max(1.0, abs(Nsum)):
                messagebox.showwarning(
                    "Предупреждение",
                    f"Сумма nci ({sum_nci:.3e}) заметно отличается от Nсумм ({Nsum:.3e})",
                )


        if NFE >= NF0:
            KFL = 1.0
        else:
            KFL = (NF0 / NFE) ** (1.0 / mf)

        if abs(mf - 3.0) < 1e-6 and KFL > 1.63:
            KFL = 1.63
        if abs(mf - 6.0) < 1e-6 and KFL > 2.08:
            KFL = 2.08

        sigma_fp = sigma_fp_p * KFL


        m_raw = Kma * T1 * (u + 1.0) * Yf1 / (aw * bw * sigma_fp)
        m_std = nearest_module(modules, m_raw)

        beta_rad = math.radians(beta_deg)
        z1k = 2.0 * aw * math.cos(beta_rad) / (m_std * (u + 1.0))
        z1_final = int(round(z1k))
        if z1_final <= 0:
            raise ValueError("Получилось некорректное z1 (≤ 0)")

        z2 = int(round(z1_final * u))

        result_text = (
            "Результаты расчёта:\n"
            f"  Kma = {Kma:.0f}\n"
            f"  Yf1 = {Yf1:.3f}\n"
            f"  σ′fp = {sigma_fp_p:.2f} МПа, NF0 = {NF0:.3e}\n"
            f"  NFE = {NFE:.3e}, KFL = {KFL:.3f}, σfp = {sigma_fp:.2f} МПа\n"
            f"  Расчётный модуль m = {m_raw:.3f}, стандартный m = {m_std:.3f}\n\n"
            f"  Число зубьев шестерни z1 = {z1_final}\n"
            f"  Число зубьев колеса   z2 = {z2}"
        )

        messagebox.showinfo("Результат", result_text)

    except Exception as e:
        messagebox.showerror("Ошибка", str(e))




def main():
    conn = create_connection()
    if conn is None:
        return

    mats = get_materials(conn)
    modules = get_modules(conn)

    root = tk.Tk()
    root.title("Расчёт числа зубьев передачи")

    widgets = {}

    frm_main = ttk.LabelFrame(root, text="Основные параметры")
    frm_main.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

    def add_row(frame, row, label):
        ttk.Label(frame, text=label).grid(row=row, column=0, sticky="w", pady=2)
        entry = ttk.Entry(frame, width=15)
        entry.grid(row=row, column=1, sticky="w", pady=2, padx=5)
        return entry

    widgets["aw"] = add_row(frm_main, 0, "aw, мм (межосевое расстояние):")
    widgets["beta"] = add_row(frm_main, 1, "β, град:")
    widgets["T1"] = add_row(frm_main, 2, "T1, Н·мм (крутящий момент):")
    widgets["z1n"] = add_row(frm_main, 3, "z1n (предварительное число зубьев):")
    widgets["x"] = add_row(frm_main, 4, "x (коэффициент смещения):")
    widgets["u"] = add_row(frm_main, 5, "u (передаточное число):")
    widgets["bw"] = add_row(frm_main, 6, "bw, мм (ширина венца):")
    widgets["mf"] = add_row(frm_main, 7, "mf (параметр):")

    
    ttk.Label(frm_main, text="Тип передачи:").grid(row=8, column=0, sticky="w", pady=2)
    cb_gear = ttk.Combobox(
        frm_main,
        values=["Прямозубая", "Косозубая", "Шевронная"],
        state="readonly",
        width=17,
    )
    cb_gear.grid(row=8, column=1, sticky="w", pady=2, padx=5)
    widgets["gear_type"] = cb_gear

    
    ttk.Label(frm_main, text="Коэфф. осевого перекрытия (для косозубой):").grid(
        row=9, column=0, sticky="w", pady=2
    )
    cb_axial = ttk.Combobox(
        frm_main,
        values=["εβ ≤ 1", "εβ > 1"],
        state="readonly",
        width=17,
    )
    cb_axial.grid(row=9, column=1, sticky="w", pady=2, padx=5)
    widgets["axial_overlap"] = cb_axial

    def on_gear_change(event):
        if cb_gear.get() == "Косозубая":
            cb_axial.configure(state="readonly")
        else:
            cb_axial.set("")
            cb_axial.configure(state="disabled")

    cb_gear.bind("<<ComboboxSelected>>", on_gear_change)
    cb_axial.configure(state="disabled")

    frm_mat = ttk.LabelFrame(root, text="Материал и нагрузка")
    frm_mat.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

    ttk.Label(frm_mat, text="Материал:").grid(row=0, column=0, sticky="w", pady=2)
    cb_mat = ttk.Combobox(frm_mat, values=mats, state="readonly", width=35)
    cb_mat.grid(row=0, column=1, sticky="w", pady=2, padx=5)
    widgets["material"] = cb_mat

    ttk.Label(frm_mat, text="Вид нагрузки:").grid(row=1, column=0, sticky="w", pady=2)
    cb_ldir = ttk.Combobox(
        frm_mat, values=["Нереверсивная", "Реверсивная"], state="readonly", width=20
    )
    cb_ldir.grid(row=1, column=1, sticky="w", pady=2, padx=5)
    widgets["load_dir"] = cb_ldir

    ttk.Label(frm_mat, text="Тип нагружения:").grid(row=2, column=0, sticky="w", pady=2)
    cb_ltype = ttk.Combobox(
        frm_mat,
        values=["Постоянная", "Ступенчатая циклограмма"],
        state="readonly",
        width=25,
    )
    cb_ltype.grid(row=2, column=1, sticky="w", pady=2, padx=5)
    widgets["load_type"] = cb_ltype

    frm_const = ttk.LabelFrame(root, text="Постоянная нагрузка")
    frm_const.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")

    widgets["thours"] = add_row(frm_const, 0, "tч, ч (часы работы):")
    widgets["n"] = add_row(frm_const, 1, "n, об/мин:")

    frm_step = ttk.LabelFrame(root, text="Ступенчатая циклограмма нагружения")
    frm_step.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")

    widgets["Nsum"] = add_row(frm_step, 0, "Nсумм (суммарное число циклов):")

    ttk.Label(frm_step, text="Ступень").grid(row=1, column=0, padx=5)
    ttk.Label(frm_step, text="T1i, Н·мм").grid(row=1, column=1, padx=5)
    ttk.Label(frm_step, text="nci, циклы").grid(row=1, column=2, padx=5)

    for i in range(1, 6):
        ttk.Label(frm_step, text=str(i)).grid(row=i + 1, column=0)
        eT = ttk.Entry(frm_step, width=12)
        eN = ttk.Entry(frm_step, width=12)
        eT.grid(row=i + 1, column=1, padx=3, pady=2)
        eN.grid(row=i + 1, column=2, padx=3, pady=2)
        widgets[f"T1_{i}"] = eT
        widgets[f"nci_{i}"] = eN

    def on_load_type_change(event):
        lt = cb_ltype.get()
        if lt == "Постоянная":
            for child in frm_const.winfo_children():
                child.configure(state="normal")
            for child in frm_step.winfo_children():
                child.configure(state="disabled")
        elif lt == "Ступенчатая циклограмма":
            for child in frm_const.winfo_children():
                child.configure(state="disabled")
            for child in frm_step.winfo_children():
                child.configure(state="normal")
        else:
            for child in frm_const.winfo_children():
                child.configure(state="normal")
            for child in frm_step.winfo_children():
                child.configure(state="normal")

    cb_ltype.bind("<<ComboboxSelected>>", on_load_type_change)

    on_load_type_change(None)

    btn_calc = ttk.Button(
        root,
        text="Рассчитать",
        command=lambda: calculate(conn, modules, widgets),
    )
    btn_calc.grid(row=4, column=0, padx=10, pady=10, sticky="e")

    root.mainloop()
    conn.close()


if __name__ == "__main__":
    main()
DB_PORT = 5432 