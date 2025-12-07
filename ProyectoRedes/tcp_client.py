"""Cliente TCP"""
import socket, threading
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

class ClienteTCP:
    def __init__(self, username, host="127.0.0.1", puerto=5555):
        self.username = username
        self.usuarios = []
        self.usuario_seleccionado = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            self.socket.connect((host, puerto))
            self.socket.send(username.encode())
            
            if self.socket.recv(1024).decode() != "OK":
                return
            
            #Crea la ventana
            self.ventana = tk.Tk()
            self.ventana.title(f"Cliente TCP - {username}")
            self.ventana.geometry("600x500")
            self.ventana.protocol("WM_DELETE_WINDOW", self.cerrar)
            
            tk.Label(self.ventana, text=f"Chat TCP - {username}", 
                    font=("Arial", 14, "bold")).pack(pady=10)
            
            self.label_dest = tk.Label(self.ventana, text="Enviando a: Todos")
            self.label_dest.pack()
            
            #Area de chat
            self.chat = ScrolledText(self.ventana, width=70, height=18)
            self.chat.pack(padx=10, pady=10)
            
            #Entrada de mensajes
            entrada_f = tk.Frame(self.ventana)
            entrada_f.pack(pady=5)
            
            self.entrada = tk.Entry(entrada_f, width=50)
            self.entrada.pack(side=tk.LEFT, padx=5)
            self.entrada.bind("<Return>", lambda e: self.enviar())
            
            tk.Button(entrada_f, text="Enviar", command=self.enviar, width=10).pack(side=tk.LEFT)
            
            #Lista de usuarios
            tk.Label(self.ventana, text="Usuarios Conectados:", font=("Arial", 10, "bold")).pack()
            
            usuarios_f = tk.Frame(self.ventana)
            usuarios_f.pack(pady=5)
            
            self.frame_usuarios = tk.Frame(usuarios_f)
            self.frame_usuarios.pack()
            
            threading.Thread(target=self.recibir, daemon=True).start()
            self.socket.send("LISTA|".encode())
            
            self.ventana.mainloop()
        except Exception as e:
            print(f"Error: {e}")
    
    #Envia mensaje al servidor
    def enviar(self):
        txt = self.entrada.get().strip()
        if not txt: 
            return
        self.entrada.delete(0, tk.END)
        
        msg_texto = ""
        if self.usuario_seleccionado:
            msg_texto = f"PRIVADO|{txt}|{self.usuario_seleccionado}"
        else:
            msg_texto = f"BROADCAST|{txt}|"
        
        try: 
            self.socket.send(msg_texto.encode())
        except: 
            pass
    
    #Recibe mensajes del servidor
    def recibir(self):
        while True:
            try:
                data = self.socket.recv(1024).decode()
                if not data: 
                    break
                
                if data.startswith("USUARIOS:"):
                    usuarios_str = data.replace("USUARIOS:", "")
                    self.usuarios = usuarios_str.split(",") if usuarios_str else []
                    self.ventana.after(0, self.actualizar_usuarios)
                elif data.startswith("PRIVADO:"):
                    partes_msg = data.split(":", 2)
                    self.chat.insert(tk.END, f"[PRIVADO] {partes_msg[1]}: {partes_msg[2]}\n")
                    self.chat.see(tk.END)
                else:
                    self.chat.insert(tk.END, f"[GRUPAL] {data}\n")
                    self.chat.see(tk.END)
            except: 
                break
    
    #Actualiza la lista de usuarios
    def actualizar_usuarios(self):
        for w in self.frame_usuarios.winfo_children(): 
            w.destroy()
        
        for u in self.usuarios:
            if u == self.username:
                lbl = tk.Label(self.frame_usuarios, text=f"• {u} (tu)", fg="blue")
            else:
                color_txt = "green" if self.usuario_seleccionado == u else "black"
                lbl = tk.Label(self.frame_usuarios, text=f"• {u}", 
                              fg=color_txt, cursor="hand2")
                lbl.bind("<Button-1>", lambda e, usuario=u: self.seleccionar(usuario))
            lbl.pack(side=tk.LEFT, padx=10)
    
    #Selecciona/deselecciona usuario para mensaje privado
    def seleccionar(self, u):
        if self.usuario_seleccionado == u:
            self.usuario_seleccionado = None
            self.label_dest.config(text="Enviando a: Todos")
        else:
            self.usuario_seleccionado = u
            self.label_dest.config(text=f"Enviando a: {u}")
        self.actualizar_usuarios()
    
    def cerrar(self):
        try: 
            self.socket.close()
        except: 
            pass
        self.ventana.destroy()

if __name__ == "__main__":
    import sys
    ClienteTCP(sys.argv[1] if len(sys.argv) > 1 else "User1")
