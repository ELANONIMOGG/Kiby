from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
import sqlite3


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

def insertar_usuario(nombre, email):
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO usuarios(nombre, email) VALUES(?, ?)", (nombre, email))
    conn.commit()
    conn.close()

def obtener_usuarios():
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios")
    datos = cursor.fetchall()
    conn.close()
    return datos

def actualizar_usuario(uid, nombre, email):
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE usuarios SET nombre=?, email=? WHERE id=?", (nombre, email, uid))
    conn.commit()
    conn.close()

def eliminar_usuario(uid):
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id=?", (uid,))
    conn.commit()
    conn.close()


class CRUDApp(App):
    def build(self):
        # Nueva paleta vibrante y mejor contraste
        primary_color = [0.12, 0.47, 0.95, 1]   # Azul vibrante
        accent_color = [0.13, 0.71, 0.38, 1]    # Verde vibrante
        delete_color = [0.95, 0.23, 0.23, 1]    # Rojo
        bg_color = [1, 1, 1, 1]                 # Blanco
        text_color = [0.10, 0.10, 0.10, 1]      # Gris oscuro casi negro
        btn_text_color = [1, 1, 1, 1]           # Blanco
        btn_text_dark = [0.10, 0.10, 0.10, 1]   # Gris oscuro para botones claros

        # Cambiar fondo de la ventana a blanco
        from kivy.core.window import Window
        Window.clearcolor = (1, 1, 1, 1)

        # Layout principal vertical centrado
        main_layout = BoxLayout(orientation="vertical", padding=[40, 30, 40, 30], spacing=10)

        # Título principal
        main_layout.add_widget(Label(text="Gestión de Usuarios", font_size=30, bold=True, color=primary_color, size_hint_y=None, height=50, halign="center", valign="middle"))
        main_layout.add_widget(Label(text="Agrega, actualiza o elimina usuarios fácilmente", font_size=16, color=[0.3,0.3,0.3,1], size_hint_y=None, height=28, halign="center", valign="middle"))

        # Layout horizontal para centrar el contenido
        content_layout = BoxLayout(orientation="horizontal", spacing=40, size_hint=(1, 1), padding=[0,0,0,0])

        # Columna izquierda: formulario
        form_layout = BoxLayout(orientation="vertical", spacing=16, size_hint=(0.45, 1), padding=[0,0,0,0])

        self.nombre_input = TextInput(
            hint_text="Nombre",
            multiline=False,
            background_color=bg_color,
            foreground_color=text_color,
            cursor_color=primary_color,
            font_size=18,
            padding=[10,10,10,10],
            size_hint_y=None,
            height=45
        )
        self.email_input = TextInput(
            hint_text="Email",
            multiline=False,
            background_color=bg_color,
            foreground_color=text_color,
            cursor_color=primary_color,
            font_size=18,
            padding=[10,10,10,10],
            size_hint_y=None,
            height=45
        )
        self.id_input = TextInput(
            hint_text="ID para actualizar/eliminar",
            multiline=False,
            background_color=bg_color,
            foreground_color=text_color,
            cursor_color=primary_color,
            font_size=18,
            padding=[10,10,10,10],
            size_hint_y=None,
            height=45
        )

        form_layout.add_widget(self.nombre_input)
        form_layout.add_widget(self.email_input)
        form_layout.add_widget(self.id_input)

        # Botones con iconos Unicode y mejor contraste
        btn_layout = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=50)
        btn_add = Button(
            text="Agregar",
            on_press=self.agregar_usuario,
            background_color=accent_color,
            color=btn_text_color,
            font_size=18,
            size_hint=(1, 1),
            border=(16,16,16,16)
        )
        btn_update = Button(
            text="Actualizar",
            on_press=self.actualizar_usuario,
            background_color=primary_color,
            color=btn_text_color,
            font_size=18,
            size_hint=(1, 1),
            border=(16,16,16,16)
        )
        btn_delete = Button(
            text="Eliminar",
            on_press=self.eliminar_usuario,
            background_color=delete_color,
            color=btn_text_color,
            font_size=18,
            size_hint=(1, 1),
            border=(16,16,16,16)
        )
        btn_layout.add_widget(btn_add)
        btn_layout.add_widget(btn_update)
        btn_layout.add_widget(btn_delete)
        form_layout.add_widget(btn_layout)
        # Label para mensajes de feedback
        self.feedback_label = Label(text="", font_size=15, color=[0.95, 0.23, 0.23, 1], size_hint_y=None, height=28)
        form_layout.add_widget(self.feedback_label)

        # Columna derecha: listado
        right_layout = BoxLayout(orientation="vertical", spacing=10, size_hint=(0.55, 1), padding=[0,0,0,0])
        right_layout.add_widget(Label(text="Lista de Usuarios", font_size=22, bold=True, color=primary_color, size_hint_y=None, height=38, halign="center", valign="middle"))

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

    def agregar_usuario(self, instance):
        nombre = self.nombre_input.text.strip()
        email = self.email_input.text.strip()
        if nombre and email:
            insertar_usuario(nombre, email)
            self.nombre_input.text = ""
            self.email_input.text = ""
            self.feedback_label.text = "Usuario agregado correctamente."
            self.feedback_label.color = [0.13, 0.71, 0.38, 1]  # Verde
            self.refrescar_lista()
        else:
            self.feedback_label.text = "Nombre y email son obligatorios."
            self.feedback_label.color = [0.95, 0.23, 0.23, 1]  # Rojo

    def actualizar_usuario(self, instance):
        uid = self.id_input.text.strip()
        nombre = self.nombre_input.text.strip()
        email = self.email_input.text.strip()
        if not uid.isdigit():
            self.feedback_label.text = "ID inválido. Debe ser un número."
            self.feedback_label.color = [0.95, 0.23, 0.23, 1]
            return
        if not (nombre and email):
            self.feedback_label.text = "Nombre y email son obligatorios."
            self.feedback_label.color = [0.95, 0.23, 0.23, 1]
            return
        # Verificar si el usuario existe
        usuarios = obtener_usuarios()
        if not any(str(u[0]) == uid for u in usuarios):
            self.feedback_label.text = f"No existe usuario con ID {uid}."
            self.feedback_label.color = [0.95, 0.23, 0.23, 1]
            return
        actualizar_usuario(int(uid), nombre, email)
        self.id_input.text = ""
        self.nombre_input.text = ""
        self.email_input.text = ""
        self.feedback_label.text = "Usuario actualizado correctamente."
        self.feedback_label.color = [0.13, 0.71, 0.38, 1]
        self.refrescar_lista()

    def eliminar_usuario(self, instance):
        uid = self.id_input.text.strip()
        if not uid.isdigit():
            self.feedback_label.text = "ID inválido. Debe ser un número."
            self.feedback_label.color = [0.95, 0.23, 0.23, 1]
            return
        usuarios = obtener_usuarios()
        if not any(str(u[0]) == uid for u in usuarios):
            self.feedback_label.text = f"No existe usuario con ID {uid}."
            self.feedback_label.color = [0.95, 0.23, 0.23, 1]
            return
        eliminar_usuario(int(uid))
        self.id_input.text = ""
        self.feedback_label.text = "Usuario eliminado correctamente."
        self.feedback_label.color = [0.13, 0.71, 0.38, 1]
        self.refrescar_lista()

    def refrescar_lista(self):
        self.grid.clear_widgets()
        usuarios = obtener_usuarios()
        for idx, (uid, nombre, email) in enumerate(usuarios):
            color = [0, 0, 0, 1]  # Negro puro para máximo contraste
            label = Label(
                text=f"ID: {uid}   Nombre: {nombre}   Email: {email}",
                color=color,
                font_size=17,
                halign="left",
                valign="middle",
                size_hint_y=None,
                height=44
            )
            self.grid.add_widget(label)


if __name__ == "__main__":
    init_db()
    CRUDApp().run()
