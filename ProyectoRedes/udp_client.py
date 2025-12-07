"""Cliente UDP"""
import socket
import threading, tkinter as tk
import time
from tkinter.scrolledtext import ScrolledText

class ClienteUDP:
    def __init__(self, username, host="127.0.0.1", puerto=5556):
        self.username = username
        self.running = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server = (host, puerto)
        self.usuarios = []
        self.usuario_seleccionado = None
        
        try:
            self.socket.sendto(f"CONECTAR|{username}".encode(), self.server)
            self.socket.settimeout(5)
            
            respuesta = self.socket.recvfrom(1024)[0].decode()
            if respuesta != "OK":
                return
            
            #Crea la ventana
            self.ventana = tk.Tk()
            self.ventana.title(f"Cliente UDP - {username}")
            self.ventana.geometry("600x500")
            self.ventana.protocol("WM_DELETE_WINDOW", self.cerrar)
            
            tk.Label(self.ventana, text=f"Chat UDP - {username}", 
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
            threading.Thread(target=self.keepalive, daemon=True).start()
            self.socket.sendto(f"LISTA|{username}".encode(), self.server)
            
            self.ventana.mainloop()
        except Exception as e:
            print(f"Error: {e}")
    
    #Envia mensaje al servidor
    def enviar(self):
        txt = self.entrada.get().strip()
        if not txt: 
            return
        self.entrada.delete(0, tk.END)
        
        mensaje_final = ""
        if self.usuario_seleccionado:
            mensaje_final = f"PRIVADO|{self.username}|{txt}|{self.usuario_seleccionado}"
        else:
            mensaje_final = f"BROADCAST|{self.username}|{txt}|"
        
        try: 
            self.socket.sendto(mensaje_final.encode(), self.server)
        except: 
            pass
    
    #Recibe mensajes del servidor
    def recibir(self):
        while self.running:
            try:
                self.socket.settimeout(1)
                data = self.socket.recvfrom(1024)[0].decode()
                
                if data.startswith("USUARIOS:"):
                    usuarios_str = data.replace("USUARIOS:", "")
                    self.usuarios = usuarios_str.split(",") if usuarios_str else []
                    self.ventana.after(0, self.actualizar_usuarios)
                elif data.startswith("PRIVADO:"):
                    aux = data.split(":", 2)
                    self.chat.insert(tk.END, f"[PRIVADO] {aux[1]}: {aux[2]}\n")
                    self.chat.see(tk.END)
                else:
                    self.chat.insert(tk.END, f"[GRUPAL] {data}\n")
                    self.chat.see(tk.END)
            except socket.timeout: 
                continue
            except: 
                break
    
    #Envia keepalive cada 3 segundos
    def keepalive(self):
        while self.running:
            try:
                time.sleep(3)
                self.socket.sendto(f"KEEPALIVE|{self.username}".encode(), self.server)
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
                color_fg = "green" if self.usuario_seleccionado == u else "black"
                lbl = tk.Label(self.frame_usuarios, text=f"• {u}", 
                              fg=color_fg, cursor="hand2")
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
        self.running = False
        try: 
            self.socket.close()
        except: 
            pass
        self.ventana.destroy()

if __name__ == "__main__":
    import sys
    ClienteUDP(sys.argv[1] if len(sys.argv) > 1 else "User1")
