import sqlite3
import re
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
# Paleta de colores ajustada
COLOR_FONDO = (0.8, 0.91, 1, 1) # Azul claro tipo selección Windows (#cce8ff)
COLOR_TARJETA = (0.12, 0.12, 0.12, 1) # Negro mate (#1e1e1e)
COLOR_TEXTO_TARJETA = (1, 1, 1, 1) # Blanco puro (#ffffff)
COLOR_TEXTO_BIBLIA = (0, 0, 0, 1) # Negro para lectura clara
# Mapeo oficial (IDs LBLA y Nombres para RV)
MAPA_LIBROS = {
	"Génesis": (1, 10), "Éxodo": (2, 20), "Levítico": (3, 30), "Números": (4, 40),
	"Deuteronomio": (5, 50), "Josué": (6, 60), "Jueces": (7, 70), "Rut": (8, 80),
	"1 Samuel": (9, 90), "2 Samuel": (10, 100), "1 Reyes": (11, 110), "2 Reyes": (12, 120),
	"1 Crónicas": (13, 130), "2 Crónicas": (14, 140), "Esdras": (15, 150), "Nehemías": (16, 160),
	"Ester": (17, 190), "Job": (18, 220), "Salmos": (19, 230), "Proverbios": (20, 240),
	"Eclesiastés": (21, 250), "Cantar de los Cantares": (22, 260), "Isaías": (23, 290),
	"Jeremías": (24, 300), "Lamentaciones": (25, 310), "Ezequiel": (26, 330), "Daniel": (27, 340),
	"Oseas": (28, 350), "Joel": (29, 360), "Amós": (30, 370), "Abdías": (31, 380),
	"Jonás": (32, 390), "Miqueas": (33, 400), "Nahúm": (34, 410), "Habacuc": (35, 420),
	"Sofonías": (36, 430), "Hageo": (37, 440), "Zacarías": (38, 450), "Malaquías": (39, 460),
	"Mateo": (40, 470), "Marcos": (41, 480), "Lucas": (42, 490), "Juan": (43, 500),
	"Hechos": (44, 510), "Romanos": (45, 520), "1 Corintios": (46, 530), "2 Corintios": (47, 540),
	"Gálatas": (48, 550), "Efesios": (49, 560), "Filipenses": (50, 570), "Colosenses": (51, 580),
	"1 Tesalonicenses": (52, 590), "2 Tesalonicenses": (53, 600), "1 Timoteo": (54, 610),
	"2 Timoteo": (55, 620), "Tito": (56, 630), "Filemón": (57, 640), "Hebreos": (58, 650),
	"Santiago": (59, 660), "1 Pedro": (60, 670), "2 Pedro": (61, 680), "1 Juan": (62, 690),
	"2 Juan": (63, 700), "3 Juan": (64, 710), "Judas": (65, 720), "Apocalipsis": (66, 730)
}
PLAN_DESARMADO = [
	('TEXTO', "Génesis", 1, 1, 11, 32, "Génesis 1 al 11 - Los Orígenes"),
	('TRANSICION', "", 0, 0, 0, 0, "--- COMENTARIO EXEGÉTICO ---\nSegún la investigación bíblica, Job vivió durante la época patriarcal (contemporáneo con la era de Abraham). Hacemos una pausa en Génesis para leer la prueba de Job en la tierra de Uz."),
	('TEXTO', "Job", 1, 1, 42, 17, "Libro de Job Completo (Capítulos 1 al 42)"),
	('TRANSICION', "", 0, 0, 0, 0, "--- COMENTARIO EXEGÉTICO ---\nConcluida la historia de Job, retomamos el hilo narrativo patriarcal en Génesis a partir del llamamiento de Abraham."),
	('TEXTO', "Génesis", 12, 1, 50, 26, "Génesis 12 al 50 - Los Patriarcas"),
	('TEXTO', "Éxodo", 1, 1, 40, 38, "Éxodo 1 al 40"),
	('TEXTO', "Levítico", 1, 1, 27, 34, "Levítico 1 al 27"),
	('TEXTO', "Números", 1, 1, 14, 45, "Números 1 al 14"),
	('TRANSICION', "", 0, 0, 0, 0, "--- COMENTARIO EXEGÉTICO ---\nDurante los 40 años de peregrinaje por el desierto registrados en Números, Moisés escribe la meditación del Salmo 90."),
	('TEXTO', "Salmos", 90, 1, 90, 17, "Salmo 90 - Oración de Moisés"),
	('TEXTO', "Números", 15, 1, 36, 13, "Números 15 al 36"),
	('TEXTO', "Deuteronomio", 1, 1, 34, 12, "Deuteronomio 1 al 34"),
	('TEXTO', "Josué", 1, 1, 24, 33, "Josué 1 al 24"),
	('TEXTO', "Jueces", 1, 1, 5, 31, "Jueces 1 al 5"),
	('TRANSICION', "", 0, 0, 0, 0, "--- COMENTARIO EXEGÉTICO ---\nLa historia de Rut ocurre 'en los días que gobernaban los jueces'. Abrimos un paréntesis para leer su relato familiar."),
	('TEXTO', "Rut", 1, 1, 4, 22, "Libro de Rut Completo"),
	('TEXTO', "Jueces", 6, 1, 21, 25, "Jueces 6 al 21")
]
class BibliaApp(App):
	def build(self):
		Window.clearcolor = COLOR_FONDO
		self.db_path = "programa_marcos.db"
		self.paso_actual = 0
		self.version = "LBLA"
		# Layout Principal Vertical
		layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
		# Encabezado
		self.lbl_paso = Label(text="Paso 1", font_size='14sp', color=(0.3, 0.3, 0.3, 1), size_hint_y=None, height=30)
		self.lbl_titulo = Label(text="Título", font_size='18sp', bold=True, color=(0, 0, 0, 1), size_hint_y=None, height=40)
		layout.add_widget(self.lbl_paso)
		layout.add_widget(self.lbl_titulo)
		# Áreas de Scroll para el Texto
		self.scroll = ScrollView(size_hint=(1, 1))
		self.lbl_contenido = Label(
			text="", font_size='16sp', color=COLOR_TEXTO_BIBLIA,
			size_hint_y=None, markup=True
		)
		self.lbl_contenido.bind(width=lambda*x: self.lbl_contenido.setter('text_size')(self.lbl_contenido, (self.lbl_contenido.width, None)))
		self.lbl_contenido.bind(texture_size=lambda*x: self.lbl_contenido.setter('height')(self.lbl_contenido, self.lbl_contenido.texture_size[1]))
		self.scroll.add_widget(self.lbl_contenido)
		layout.add_widget(self.scroll)
		# Barra de Navegación Inferior (Botones Grandes para Táctil)
		bar_nav = BoxLayout(size_hint_y=None, height=50, spacing=10)
		self.btn_ant = Button(text="? Anterior", on_press=self.retroceder)
		self.btn_sig = Button(text="Siguiente ?", on_press=self.avanzar)
		bar_nav.add_widget(self.btn_ant)
		bar_nav.add_widget(self.btn_sig)
		layout.add_widget(bar_nav)
		self.cargar_paso()
		return layout
	def cargar_paso(self):
		total = len(PLAN_DESARMADO)
		item = PLAN_DESARMADO[self.paso_actual]
		tipo = item[0]
		self.lbl_paso.text = f"PASO {self.paso_actual + 1} DE {total}"
		if tipo == 'TRANSICION':
			self.lbl_titulo.text = "PAUSA EXEGÉTICA"
			# Tarjeta Negra con Letras Blancas en formato Markup
			self.lbl_contenido.color = COLOR_TEXTO_TARJETA
			self.lbl_contenido.text = f"\n[background=1e1e1e] {item[6]} [/background]\n"
		else:
			self.lbl_contenido.color = COLOR_TEXTO_BIBLIA
			nombre_libro = item[1]
			cap_i, ver_i, cap_f, ver_f, desc = item[2], item[3], item[4], item[5], item[6]
			self.lbl_titulo.text = desc
		try:
			conn = sqlite3.connect(self.db_path)
			cursor = conn.cursor()
			lbla_id = MAPA_LIBROS[nombre_libro][1]
			query = """
				SELECT capitulo, versiculo, texto FROM texto_biblico_lbla
				WHERE libro = ? AND (
					(capitulo = ? AND versiculo >= ?) OR
					(capitulo > ? AND capitulo < ?) OR
					(capitulo = ? AND versiculo <= ?)
				) ORDER BY capitulo, versiculo
			"""
			cursor.execute(query, (lbla_id, cap_i, ver_i, cap_i, cap_f, cap_f, ver_f))
			filas = cursor.fetchall()
			conn.close()
			texto_completo = ""
			for c, v, t in filas:
				t_limpio = re.sub(r'<[^>]+>', '', str(t))
				t_limpio = re.sub(r'\s+', ' ', t_limpio).strip()
				texto_completo += f"[b][color=003366]{c}:{v}[/color][/b] {t_limpio}\n\n"
			self.lbl_contenido.text = texto_completo
		except Exception as e:
			self.lbl_contenido.text = f"Error: {e}"
		self.scroll.scroll_y = 1
	def avanzar(self, instance):
		if self.paso_actual < len(PLAN_DESARMADO) - 1:
			self.paso_actual += 1
			self.cargar_paso()
	def retroceder(self, instance):
		if self.paso_actual > 0:
			self.paso_actual -= 1
			self.cargar_paso()
if __name__ == '__main__':
	BibliaApp().run()