from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.properties import StringProperty
from kivy.core.window import Window
import sqlite3

# Clase para manejar la base de datos
class UsuarioDB:
    @staticmethod
    def init_db():
        conn = sqlite3.connect("usuarios.db")
        cursor = conn.cursor()
        cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    email TEXT NOT NULL
)
""")
        conn.commit()
        conn.close()

    @staticmethod
    def insertar(nombre, email):
        conn = sqlite3.connect("usuarios.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios(nombre, email) VALUES(?, ?)", (nombre, email))
        conn.commit()
        conn.close()

    @staticmethod
    def obtener():
        conn = sqlite3.connect("usuarios.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios")
        datos = cursor.fetchall()
        conn.close()
        return datos

    @staticmethod
    def actualizar(uid, nombre, email):
        conn = sqlite3.connect("usuarios.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE usuarios SET nombre=?, email=? WHERE id=?", (nombre, email, uid))
        conn.commit()
        conn.close()

    @staticmethod
    def eliminar(uid):
        conn = sqlite3.connect("usuarios.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id=?", (uid,))
        conn.commit()
        conn.close()

class CRUDApp(App):
    feedback = StringProperty("")
    feedback_color = [0.95, 0.23, 0.23, 1]

    def build(self):
        # Paleta de colores
        self.primary_color = [0.12, 0.47, 0.95, 1]
        self.accent_color = [0.13, 0.71, 0.38, 1]
        self.delete_color = [0.95, 0.23, 0.23, 1]
        self.bg_color = [1, 1, 1, 1]
        self.text_color = [0.10, 0.10, 0.10, 1]
        self.btn_text_color = [1, 1, 1, 1]

        Window.clearcolor = (1, 1, 1, 1)

        main_layout = BoxLayout(orientation="vertical", padding=[40, 30, 40, 30], spacing=10)
        main_layout.add_widget(Label(text="Gestión de Usuarios", font_size=30, bold=True, color=self.primary_color, size_hint_y=None, height=50, halign="center", valign="middle"))
        main_layout.add_widget(Label(text="Agrega, actualiza o elimina usuarios fácilmente", font_size=16, color=[0.3,0.3,0.3,1], size_hint_y=None, height=28, halign="center", valign="middle"))

        content_layout = BoxLayout(orientation="horizontal", spacing=40, size_hint=(1, 1))

        # Formulario
        form_layout = BoxLayout(orientation="vertical", spacing=16, size_hint=(0.45, 1))
        self.nombre_input = TextInput(hint_text="Nombre", multiline=False, background_color=self.bg_color, foreground_color=self.text_color, cursor_color=self.primary_color, font_size=18, padding=[10,10,10,10], size_hint_y=None, height=45)
        self.email_input = TextInput(hint_text="Email", multiline=False, background_color=self.bg_color, foreground_color=self.text_color, cursor_color=self.primary_color, font_size=18, padding=[10,10,10,10], size_hint_y=None, height=45)
        self.id_input = TextInput(hint_text="ID para actualizar/eliminar", multiline=False, background_color=self.bg_color, foreground_color=self.text_color, cursor_color=self.primary_color, font_size=18, padding=[10,10,10,10], size_hint_y=None, height=45)
        form_layout.add_widget(self.nombre_input)
        form_layout.add_widget(self.email_input)
        form_layout.add_widget(self.id_input)

        btn_layout = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=50)
        btn_layout.add_widget(Button(text="Agregar", on_press=self.on_agregar, background_color=self.accent_color, color=self.btn_text_color, font_size=18, size_hint=(1, 1), border=(16,16,16,16)))
        btn_layout.add_widget(Button(text="Actualizar", on_press=self.on_actualizar, background_color=self.primary_color, color=self.btn_text_color, font_size=18, size_hint=(1, 1), border=(16,16,16,16)))
        btn_layout.add_widget(Button(text="Eliminar", on_press=self.on_eliminar, background_color=self.delete_color, color=self.btn_text_color, font_size=18, size_hint=(1, 1), border=(16,16,16,16)))
        form_layout.add_widget(btn_layout)

        self.feedback_label = Label(text="", font_size=15, color=self.delete_color, size_hint_y=None, height=28)
        form_layout.add_widget(self.feedback_label)

        # Listado
        right_layout = BoxLayout(orientation="vertical", spacing=10, size_hint=(0.55, 1))
        right_layout.add_widget(Label(text="Lista de Usuarios", font_size=22, bold=True, color=self.primary_color, size_hint_y=None, height=38, halign="center", valign="middle"))
        self.scroll = ScrollView(size_hint=(1, 1))
        self.grid = GridLayout(cols=1, spacing=8, size_hint_y=None, padding=[0,10,0,10])
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        right_layout.add_widget(self.scroll)

        content_layout.add_widget(form_layout)
        content_layout.add_widget(right_layout)
        main_layout.add_widget(content_layout)

        self.refrescar_lista()
        return main_layout

    def set_feedback(self, mensaje, color):
        self.feedback_label.text = mensaje
        self.feedback_label.color = color

    def on_agregar(self, instance):
        nombre = self.nombre_input.text.strip()
        email = self.email_input.text.strip()
        if nombre and email:
            UsuarioDB.insertar(nombre, email)
            self.nombre_input.text = ""
            self.email_input.text = ""
            self.set_feedback("Usuario agregado correctamente.", self.accent_color)
            self.refrescar_lista()
        else:
            self.set_feedback("Nombre y email son obligatorios.", self.delete_color)

    def on_actualizar(self, instance):
        uid = self.id_input.text.strip()
        nombre = self.nombre_input.text.strip()
        email = self.email_input.text.strip()
        if not uid.isdigit():
            self.set_feedback("ID inválido. Debe ser un número.", self.delete_color)
            return
        if not (nombre and email):
            self.set_feedback("Nombre y email son obligatorios.", self.delete_color)
            return
        usuarios = UsuarioDB.obtener()
        if not any(str(u[0]) == uid for u in usuarios):
            self.set_feedback(f"No existe usuario con ID {uid}.", self.delete_color)
            return
        UsuarioDB.actualizar(int(uid), nombre, email)
        self.id_input.text = ""
        self.nombre_input.text = ""
        self.email_input.text = ""
        self.set_feedback("Usuario actualizado correctamente.", self.accent_color)
        self.refrescar_lista()

    def on_eliminar(self, instance):
        uid = self.id_input.text.strip()
        if not uid.isdigit():
            self.set_feedback("ID inválido. Debe ser un número.", self.delete_color)
            return
        usuarios = UsuarioDB.obtener()
        if not any(str(u[0]) == uid for u in usuarios):
            self.set_feedback(f"No existe usuario con ID {uid}.", self.delete_color)
            return
        UsuarioDB.eliminar(int(uid))
        self.id_input.text = ""
        self.set_feedback("Usuario eliminado correctamente.", self.accent_color)
        self.refrescar_lista()

    def refrescar_lista(self):
        self.grid.clear_widgets()
        usuarios = UsuarioDB.obtener()
        for uid, nombre, email in usuarios:
            label = Label(
                text=f"ID: {uid}   Nombre: {nombre}   Email: {email}",
                color=[0, 0, 0, 1],
                font_size=17,
                halign="left",
                valign="middle",
                size_hint_y=None,
                height=44
            )
            self.grid.add_widget(label)

if __name__ == "__main__":
    UsuarioDB.init_db()
    CRUDApp().run()
