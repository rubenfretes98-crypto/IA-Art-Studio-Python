# -*- coding: utf-8 -*-
import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import threading
from tkinter import filedialog
import textwrap
import urllib.parse 

# --- CONFIGURACION VISUAL ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AplicacionArteIA(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("IA Art Studio V9 - Final")
        self.geometry("1200x850")
        self.imagen_generada_actual = None 

        # --- CONFIGURACION DE FORMATOS (Ancho x Alto) ---
        self.formatos_lienzo = {
            "Instagram Post (4:5)": (1080, 1350),
            "Instagram Story (9:16)": (1080, 1920),
            "PC / YouTube (16:9)": (1280, 720),
            "Poster Vertical (3:4)": (768, 1024)
        }

        # --- ESTILOS VISUALES ---
        self.estilos_visuales = {
            "Flyer Moderno": "modern flyer background, vector art, geometric shapes, minimalist, clean, copy space",
            "Cine Epico": "movie poster background, cinematic lighting, dramatic, 8k render, epic composition",
            "Cyberpunk": "cyberpunk city background, neon lights, futuristic, dark, glowing elements",
            "Lujo Dorado": "luxury background, gold textures, black marble, elegant, premium",
            "Retro 80s": "retro 80s vaporwave background, synthwave, neon grid, sunset, nostalgic",
            "3D Cartoon": "3d render background, cute style, soft lighting, pixar style, colorful"
        }

        # --- TEMA ---
        self.temas_ocasion = {
            "Sin Tema": "",
            "Fiesta / Club": "nightclub atmosphere, party confetti, dj lights, energetic",
            "Comida": "delicious food background, restaurant vibe, fresh ingredients",
            "Ventas": "shopping background, sale elements, commercial atmosphere",
            "Gaming": "gaming setup background, rgb lights, tech circuits"
        }

        self.frame_home = ctk.CTkFrame(self, corner_radius=0)
        self.frame_home.pack(fill="both", expand=True)
        self.crear_interfaz()

    def crear_interfaz(self):
        # Panel Izquierdo
        self.panel_izq = ctk.CTkScrollableFrame(self.frame_home, width=400)
        self.panel_izq.pack(side="left", fill="y", padx=10, pady=10)

        ctk.CTkLabel(self.panel_izq, text="STUDIO V9 FINAL", font=("Impact", 30), text_color="#4B8BBE").pack(pady=20)

        # 1. FORMATO
        self.crear_titulo_seccion("1. FORMATO Y TAMANO")
        self.menu_formato = ctk.CTkOptionMenu(self.panel_izq, values=list(self.formatos_lienzo.keys()))
        self.menu_formato.pack(fill="x", padx=10, pady=5)

        # 2. TEXTOS
        self.crear_titulo_seccion("2. TEXTOS (Auto-Ajustables)")
        self.entrada_titulo = ctk.CTkEntry(self.panel_izq, placeholder_text="Titulo Principal")
        self.entrada_titulo.pack(fill="x", padx=10, pady=5)
        self.entrada_sub = ctk.CTkEntry(self.panel_izq, placeholder_text="Subtitulo (Opcional)")
        self.entrada_sub.pack(fill="x", padx=10, pady=5)

        # 3. ESTILO IA
        self.crear_titulo_seccion("3. ESTILO DE FONDO")
        ctk.CTkLabel(self.panel_izq, text="Estilo:", anchor="w").pack(fill="x", padx=10)
        self.menu_estilo = ctk.CTkOptionMenu(self.panel_izq, values=list(self.estilos_visuales.keys()))
        self.menu_estilo.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(self.panel_izq, text="Tema:", anchor="w").pack(fill="x", padx=10)
        self.menu_tema = ctk.CTkOptionMenu(self.panel_izq, values=list(self.temas_ocasion.keys()))
        self.menu_tema.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(self.panel_izq, text="Detalles:", anchor="w").pack(fill="x", padx=10)
        self.entrada_detalles = ctk.CTkEntry(self.panel_izq, placeholder_text="Ej: un auto rojo...")
        self.entrada_detalles.pack(fill="x", padx=10, pady=5)

        # 4. NEGATIVO
        self.crear_titulo_seccion("4. FILTRO NEGATIVO")
        self.entrada_neg = ctk.CTkEntry(self.panel_izq, placeholder_text="Lo que NO quieres")
        self.entrada_neg.pack(fill="x", padx=10, pady=5)
        self.entrada_neg.insert(0, "text, blurry, watermark, ugly, deformed people")

        # BOTONES
        self.boton_generar = ctk.CTkButton(self.panel_izq, text="GENERAR DISENO", height=50, font=("Arial", 14, "bold"), fg_color="#007ACC", command=self.iniciar_hilo)
        self.boton_generar.pack(fill="x", padx=10, pady=30)

        self.boton_guardar = ctk.CTkButton(self.panel_izq, text="GUARDAR IMAGEN", fg_color="#28a745", state="disabled", command=self.guardar)
        self.boton_guardar.pack(fill="x", padx=10, pady=5)

        self.consola = ctk.CTkTextbox(self.panel_izq, height=120)
        self.consola.pack(fill="x", padx=10, pady=10)

        # Panel Derecho
        self.panel_der = ctk.CTkFrame(self.frame_home)
        self.panel_der.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        self.label_img = ctk.CTkLabel(self.panel_der, text="")
        self.label_img.pack(fill="both", expand=True)

    def crear_titulo_seccion(self, txt):
        ctk.CTkLabel(self.panel_izq, text=txt, anchor="w", font=("Arial", 12, "bold"), text_color="#4B8BBE").pack(fill="x", padx=10, pady=(20,0))

    def log(self, txt):
        self.consola.insert("end", f"\n{txt}")
        self.consola.see("end")

    def iniciar_hilo(self):
        threading.Thread(target=self.procesar_generacion).start()

    def procesar_generacion(self):
        titulo = self.entrada_titulo.get().upper()
        sub = self.entrada_sub.get()
        nombre_formato = self.menu_formato.get()
        ancho, alto = self.formatos_lienzo[nombre_formato]
        
        estilo = self.estilos_visuales[self.menu_estilo.get()]
        tema = self.temas_ocasion[self.menu_tema.get()]
        detalle = self.entrada_detalles.get()
        
        prompt_raw = f"{estilo}, {tema}, {detalle}, empty space in center, clean composition, no text"
        negativo_raw = self.entrada_neg.get()

        self.boton_generar.configure(state="disabled", text="TRABAJANDO...")
        self.log(f"Generando formato: {nombre_formato}...")

        try:
            # Encoding seguro
            prompt_safe = urllib.parse.quote(prompt_raw)
            negativo_safe = urllib.parse.quote(negativo_raw)

            url = f"https://image.pollinations.ai/prompt/{prompt_safe}?negative={negativo_safe}&width={ancho}&height={alto}&nologo=true"
            print(f"URL: {url}")
            
            resp = requests.get(url, timeout=60)

            if resp.status_code == 200:
                self.imagen_generada_actual = Image.open(BytesIO(resp.content))
                self.aplicar_textos_smart(titulo, sub, ancho, alto)
                
                # Preview
                ratio = min(600/ancho, 700/alto)
                new_w = int(ancho * ratio)
                new_h = int(alto * ratio)
                
                img_prev = self.imagen_generada_actual.copy().resize((new_w, new_h))
                tk_img = ctk.CTkImage(img_prev, size=(new_w, new_h))
                
                self.label_img.configure(image=tk_img)
                self.boton_guardar.configure(state="normal")
                self.log("Exito! Imagen creada.")
            else:
                self.log(f"Error API: {resp.status_code}")

        except Exception as e:
            self.log(f"Error Critico: {e}")
        finally:
            self.boton_generar.configure(state="normal", text="GENERAR DISENO")

    def aplicar_textos_smart(self, titulo, sub, W, H):
        draw = ImageDraw.Draw(self.imagen_generada_actual)
        
        def fit_text(txt, max_width, initial_font_size, is_bold=True):
            font_size = initial_font_size
            font_name = "arialbd.ttf" if is_bold else "arial.ttf"
            while font_size > 20:
                try:
                    font = ImageFont.truetype(font_name, font_size)
                except:
                    font = ImageFont.load_default()
                    return font, [txt], 20
                
                avg_char_width = font.getlength("x")
                chars_per_line = int(max_width / avg_char_width * 1.5)
                lines = textwrap.wrap(txt, width=chars_per_line)
                
                valid = True
                for line in lines:
                    if font.getlength(line) > max_width:
                        valid = False
                        break
                
                if valid:
                    total_h = sum([font.getbbox(line)[3] - font.getbbox(line)[1] for line in lines])
                    if total_h < (H * 0.4):
                        return font, lines, total_h
                font_size -= 5
            return font, [txt], 20

        if titulo:
            safe_width = W * 0.8
            font_t, lines_t, h_total_t = fit_text(titulo, safe_width, 120, True)
            y_start = (H / 2) - (h_total_t / 2) - 40
            
            padding = 30
            if lines_t:
                max_line_w = max([font_t.getlength(l) for l in lines_t])
            else:
                max_line_w = 100
            
            x1 = (W - max_line_w)/2 - padding
            y1 = y_start - padding
            x2 = (W + max_line_w)/2 + padding
            y2 = y_start + h_total_t + padding + (len(lines_t)*10)
            
            overlay = Image.new('RGBA', self.imagen_generada_actual.size, (0,0,0,0))
            d_over = ImageDraw.Draw(overlay)
            d_over.rectangle([x1, y1, x2, y2], fill=(0,0,0, 160))
            
            self.imagen_generada_actual = self.imagen_generada_actual.convert("RGBA")
            self.imagen_generada_actual = Image.alpha_composite(self.imagen_generada_actual, overlay)
            self.imagen_generada_actual = self.imagen_generada_actual.convert("RGB")
            draw = ImageDraw.Draw(self.imagen_generada_actual)
            
            current_y = y_start
            for line in lines_t:
                lw = font_t.getlength(line)
                lx = (W - lw) / 2
                # AQUI ESTABA EL ERROR: Ahora especificamos font= y fill=
                draw.text((lx, current_y), line, font=font_t, fill="white")
                current_y += font_t.getbbox(line)[3] + 10

            if sub:
                font_s, lines_s, h_total_s = fit_text(sub, safe_width, 50, False)
                y_sub = y2 + 20
                for line in lines_s:
                    lw = font_s.getlength(line)
                    lx = (W - lw) / 2
                    # CORREGIDO AQUI TAMBIEN
                    draw.text((lx+2, y_sub+2), line, font=font_s, fill="black")
                    draw.text((lx, y_sub), line, font=font_s, fill="#FFD700")
                    y_sub += font_s.getbbox(line)[3] + 10

    def guardar(self):
        if self.imagen_generada_actual:
            f = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
            if f: self.imagen_generada_actual.save(f)

if __name__ == "__main__":
    app = AplicacionArteIA()
    app.mainloop()