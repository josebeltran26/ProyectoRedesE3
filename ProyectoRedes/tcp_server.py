"""Servidor TCP"""
import socket
import threading
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from datetime import datetime
import sys

MAX_CLIENTES = 6

class ServidorTCP:
    def __init__(self, ip='0.0.0.0', puerto=5555):
        self.clientes = {}
        self.running = True
        self.socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_servidor.bind((ip, puerto))
        self.socket_servidor.listen(MAX_CLIENTES)
        
        #Crea la ventana
        self.ventana = tk.Tk()
        self.ventana.title("Servidor TCP")
        self.ventana.geometry("600x450")
        self.ventana.protocol("WM_DELETE_WINDOW", self.apagar)
        
        tk.Label(self.ventana, text=f"Servidor TCP en {ip}:{puerto}", 
                font=("Arial", 14, "bold")).pack(pady=10)
        
        self.label_info = tk.Label(self.ventana, text="Clientes: 0/6")
        self.label_info.pack()
        
        self.log = ScrolledText(self.ventana, width=70, height=18)
        self.log.pack(padx=10, pady=10)
        
        tk.Button(self.ventana, text="Apagar Servidor", command=self.apagar,
                 bg="red", fg="white", font=("Arial", 11, "bold")).pack(pady=10)
        
        threading.Thread(target=self.aceptar_clientes, daemon=True).start()
        self.escribir_log("Servidor iniciado")
        self.ventana.mainloop()
    
    def escribir_log(self, texto):
        hora = datetime.now().strftime('%H:%M:%S')
        self.log.insert(tk.END, f"[{hora}] {texto}\n")
        self.log.see(tk.END)
        self.label_info.config(text=f"Clientes: {len(self.clientes)}/6")
    
    #Acepta nuevas conexiones
    def aceptar_clientes(self):
        while self.running:
            try:
                self.socket_servidor.settimeout(1)
                cliente, addr = self.socket_servidor.accept()
                threading.Thread(target=self.manejar_cliente, args=(cliente,), daemon=True).start()
            except socket.timeout:
                continue
            except:
                break
    
    #Maneja cada cliente en su propio hilo
    def manejar_cliente(self, cliente):
        try:
            username = cliente.recv(1024).decode()
            
            if len(self.clientes) >= MAX_CLIENTES:
                cliente.send("ERROR:Servidor lleno".encode())
                cliente.close()
                return
            
            self.clientes[cliente] = username
            self.escribir_log(f"{username} se conecto")
            cliente.send("OK".encode())
            self.enviar_lista_usuarios()
            
            while self.running:
                data = cliente.recv(1024).decode()
                if not data:
                    break
                
                #Procesa el mensaje segun su tipo
                partes = data.split("|")
                tipo = partes[0]
                
                if tipo == 'BROADCAST':
                    contenido = partes[1] if len(partes) > 1 else ""
                    self.escribir_log(f"{username}: {contenido}")
                    self.broadcast(f"{username}:{contenido}", cliente)
                
                elif tipo == 'PRIVADO':
                    contenido = partes[1] if len(partes) > 1 else ""
                    dest = partes[2] if len(partes) > 2 else ""
                    self.escribir_log(f"{username} -> {dest}: {contenido}")
                    self.enviar_privado(username, dest, contenido)
                
                elif tipo == 'LISTA':
                    self.enviar_lista_usuarios(cliente)
        except:
            pass
        finally:
            if cliente in self.clientes:
                user = self.clientes[cliente]
                del self.clientes[cliente]
                self.escribir_log(f"{user} se desconecto")
                self.enviar_lista_usuarios()
            try:
                cliente.close()
            except:
                pass
    
    #Envia mensaje a todos menos al que lo envio
    def broadcast(self, mensaje, excluir=None):
        lista_clientes = list(self.clientes.keys())
        for c in lista_clientes:
            if c != excluir:
                try:
                    c.send(mensaje.encode())
                except:
                    pass
    
    #Envia mensaje privado
    def enviar_privado(self, remitente, destinatario, mensaje):
        for c, u in self.clientes.items():
            if u == destinatario or u == remitente:
                try:
                    c.send(f"PRIVADO:{remitente}:{mensaje}".encode())
                except:
                    pass
    
    #Envia la lista de usuarios conectados
    def enviar_lista_usuarios(self, cliente=None):
        lista_usuarios = list(self.clientes.values())
        usuarios = ",".join(lista_usuarios)
        data = f"USUARIOS:{usuarios}"
        if cliente:
            try:
                cliente.send(data.encode())
            except:
                pass
        else:
            for c in list(self.clientes.keys()):
                try:
                    c.send(data.encode())
                except:
                    pass
    
    def apagar(self):
        self.running = False
        try:
            self.socket_servidor.close()
        except:
            pass
        self.ventana.destroy()
        sys.exit(0)

if __name__ == "__main__":
    ServidorTCP()
