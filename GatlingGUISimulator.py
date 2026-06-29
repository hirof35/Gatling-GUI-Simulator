import tkinter as tk
from tkinter import ttk

class GatlingGUISimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Gatling Gun Spec & Recoil Simulator")
        self.root.geometry("650x700")
        self.root.resizable(False, False)

        # 各機関砲のスペック定義
        self.guns_data = {
            "GAU-8 Avenger (30mm)": {
                "desc": "A-10サンダーボルトIIの主砲。戦車を切り裂く怪物ガトリング。",
                "rpm": 3900, "velocity": 1010, "ammo_w": 0.69, "max_ammo": 1174, "sound": "BRRRRRRRT!!"
            },
            "M61 Vulcan (20mm)": {
                "desc": "F-15やF-16等に搭載される傑作20mm。圧倒的な連射速度が武器。",
                "rpm": 6000, "velocity": 1050, "ammo_w": 0.25, "max_ammo": 511, "sound": "VVRVRVRVRVT!!"
            },
            "GAU-22/A Equalizer (25mm)": {
                "desc": "F-35に搭載される最新鋭。高威力だが、機内装弾数は極めてシビア。",
                "rpm": 3300, "velocity": 1040, "ammo_w": 0.50, "max_ammo": 180, "sound": "BZZZZZZZZT!!"
            }
        }

        # 状態管理変数
        self.selected_gun = tk.StringVar(value="GAU-8 Avenger (30mm)")
        self.current_ammo = 0
        self.max_ammo = 0
        self.is_firing = False

        # GUIコンポーネントの構築
        self.create_widgets()
        self.update_gun_specs()

    def create_widgets(self):
        # 1. 機関砲の選択エリア
        selector_frame = ttk.LabelFrame(self.root, text=" 兵装選択 (Select Weapon) ", padding=10)
        selector_frame.pack(fill="x", padx=15, pady=(15, 5))

        ttk.Label(selector_frame, text="搭載機関砲:", font=("MS Gothic", 10, "bold")).grid(row=0, column=0, sticky="w")
        gun_combo = ttk.Combobox(selector_frame, textvariable=self.selected_gun, values=list(self.guns_data.keys()), state="readonly", width=30)
        gun_combo.grid(row=0, column=1, padx=10, sticky="w")
        gun_combo.bind("<<ComboboxSelected>>", lambda e: self.update_gun_specs())

        self.lbl_desc = ttk.Label(selector_frame, text="", wraplength=580, foreground="gray")
        self.lbl_desc.grid(row=1, column=0, columnspan=2, pady=(10, 0), sticky="w")

        # 2. スペック表示エリア
        spec_frame = ttk.LabelFrame(self.root, text=" カタログスペック (Specifications) ", padding=10)
        spec_frame.pack(fill="x", padx=15, pady=5)

        self.spec_labels = {}
        specs = [("口径・弾薬重量", "ammo"), ("砲口初速", "vel"), ("発射速度", "rpm")]
        for i, (label_text, key) in enumerate(specs):
            ttk.Label(spec_frame, text=label_text + ":").grid(row=i, column=0, sticky="e", pady=3)
            lbl_val = ttk.Label(spec_frame, text="", font=("Segoe UI", 10, "bold"))
            lbl_val.grid(row=i, column=1, sticky="w", padx=10, pady=3)
            self.spec_labels[key] = lbl_val

        # 3. コントロール & 射撃シミュレートエリア
        sim_frame = ttk.LabelFrame(self.root, text=" 射撃シミュレーター (Fire Control) ", padding=10)
        sim_frame.pack(fill="both", expand=True, padx=15, pady=5)

        # 弾薬カウンターとゲージ
        ttk.Label(sim_frame, text="マガジン残弾数:", font=("MS Gothic", 11)).pack(anchor="w")
        self.lbl_ammo_count = ttk.Label(sim_frame, text="0 / 0", font=("Segoe UI", 16, "bold"))
        self.lbl_ammo_count.pack(anchor="w", pady=2)

        self.ammo_bar = ttk.Progressbar(sim_frame, orient="horizontal", mode="determinate")
        self.ammo_bar.pack(fill="x", pady=5)

        # 投射重量と反動の可視化
        recoil_container = ttk.Frame(sim_frame)
        recoil_container.pack(fill="x", pady=10)

        ttk.Label(recoil_container, text="射撃時の平均反動（後座力）:", font=("MS Gothic", 10)).grid(row=0, column=0, sticky="w")
        self.lbl_recoil = ttk.Label(recoil_container, text="0 kgf", font=("Segoe UI", 14, "bold"), foreground="red")
        self.lbl_recoil.grid(row=0, column=1, sticky="w", padx=10)

        ttk.Label(recoil_container, text="1秒あたりの投射重量:", font=("MS Gothic", 10)).grid(row=1, column=0, sticky="w", pady=5)
        self.lbl_weight_per_sec = ttk.Label(recoil_container, text="0 kg/s", font=("Segoe UI", 12, "bold"), foreground="blue")
        self.lbl_weight_per_sec.grid(row=1, column=1, sticky="w", padx=10, pady=5)

        # 射撃中の効果音テキスト演出
        self.lbl_sound = ttk.Label(sim_frame, text="", font=("Arial Black", 24, "italic"), foreground="orange")
        self.lbl_sound.pack(pady=15)

        # 操作ボタン
        btn_container = ttk.Frame(sim_frame)
        btn_container.pack(side="bottom", fill="x", pady=10)

        # 「押している間連射」をシミュレートするため、マウスの長押し（ButtonPress/ButtonRelease）をバインド
        self.btn_fire = tk.Button(btn_container, text="トリガーを引く (長押し)", bg="#d9534f", fg="white", font=("MS Gothic", 12, "bold"), height=2)
        self.btn_fire.pack(side="left", fill="x", expand=True, padx=5)
        self.btn_fire.bind("<ButtonPress-1>", self.start_firing)
        self.btn_fire.bind("<ButtonRelease-1>", self.stop_firing)

        btn_reload = tk.Button(btn_container, text="リロード (Reload)", bg="#5cb85c", fg="white", font=("MS Gothic", 12, "bold"), height=2, command=self.reload_ammo)
        btn_reload.pack(side="right", fill="x", expand=True, padx=5)

    def update_gun_specs(self):
        """選択された機関砲に応じてスペックとマガジンを更新"""
        self.stop_firing()
        data = self.guns_data[self.selected_gun.get()]

        self.lbl_desc.config(text=data["desc"])
        self.spec_labels["ammo"].config(text=f"{data['ammo_w']} kg")
        self.spec_labels["vel"].config(text=f"{data['velocity']} m/s")
        self.spec_labels["rpm"].config(text=f"{data['rpm']} 発/分 (秒間 {int(data['rpm']/60)} 発)")

        # マガジン初期化
        self.max_ammo = data["max_ammo"]
        self.current_ammo = self.max_ammo
        self.update_ammo_display()
        self.lbl_sound.config(text="")

    def update_ammo_display(self):
        """残弾数テキストとプログレスバーを更新"""
        self.lbl_ammo_count.config(text=f"{self.current_ammo} / {self.max_ammo} 発")
        # 割合計算
        percentage = (self.current_ammo / self.max_ammo) * 100 if self.max_ammo > 0 else 0
        self.ammo_bar["value"] = percentage

    def start_firing(self, event=None):
        if self.current_ammo <= 0:
            self.lbl_sound.config(text="CLICK! (弾切れ)", foreground="red")
            return
        
        self.is_firing = True
        self.fire_loop()

    def stop_firing(self, event=None):
        self.is_firing = False
        self.lbl_sound.config(text="")
        self.lbl_recoil.config(text="0 kgf")
        self.lbl_weight_per_sec.config(text="0 kg/s")

    def fire_loop(self):
        """100ミリ秒（0.1秒）おきに射撃処理を行うループ。ボタンを離すまで続く"""
        if not self.is_firing or self.current_ammo <= 0:
            if self.current_ammo <= 0:
                self.stop_firing()
                self.lbl_sound.config(text="OUT OF AMMO!", foreground="red")
            return

        data = self.guns_data[self.selected_gun.get()]
        rps = data["rpm"] / 60
        
        # 0.1秒間に消費する弾数（最低1発）
        rounds_in_01s = max(1, int(rps * 0.1))
        self.current_ammo = max(0, self.current_ammo - rounds_in_01s)
        
        # 反動と投射重量の計算
        # F = m * v * rps (ニュートン) -> kgf変換
        recoil_force_kgf = ((data["ammo_w"] * rps) * data["velocity"]) / 9.80665
        weight_per_second = data["ammo_w"] * rps

        # GUIの表示更新
        self.update_ammo_display()
        self.lbl_sound.config(text=data["sound"], foreground="orange")
        self.lbl_recoil.config(text=f"{recoil_force_kgf:.1f} kgf")
        self.lbl_weight_per_sec.config(text=f"{weight_per_second:.1f} kg/s")

        # 100ms後に再帰呼び出し
        self.root.after(100, self.fire_loop)

    def reload_ammo(self):
        self.stop_firing()
        self.current_ammo = self.max_ammo
        self.update_ammo_display()
        self.lbl_sound.config(text="RELOADED", foreground="green")


if __name__ == "__main__":
    root = tk.Tk()
    app = GatlingGUISimulator(root)
    root.mainloop()
