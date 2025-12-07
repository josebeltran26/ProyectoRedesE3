"""Servidor UDP"""
import socket
import threading
import tkinter as tk
import time
import sys
from tkinter.scrolledtext import ScrolledText
from datetime import datetime

MAX_CLIENTES = 6

class ServidorUDP:
    def __init__(self, ip='0.0.0.0', puerto=5556):
        self.clientes = {}
        self.running = True
        self.socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_servidor.bind((ip, puerto))
        
        #Crea la ventana
        self.ventana = tk.Tk()
        self.ventana.title("Servidor UDP")
        self.ventana.geometry("600x450")
        self.ventana.protocol("WM_DELETE_WINDOW", self.apagar)
        
        tk.Label(self.ventana, text=f"Servidor UDP en {ip}:{puerto}", 
                font=("Arial", 14, "bold")).pack(pady=10)
        
        self.label_info = tk.Label(self.ventana, text="Clientes: 0/6")
        self.label_info.pack()
        
        self.log = ScrolledText(self.ventana, width=70, height=18)
        self.log.pack(padx=10, pady=10)
        
        tk.Button(self.ventana, text="Apagar Servidor", command=self.apagar,
                 bg="red", fg="white", font=("Arial", 11, "bold")).pack(pady=10)
        
        threading.Thread(target=self.recibir, daemon=True).start()
        threading.Thread(target=self.limpiar_inactivos, daemon=True).start()
        self.escribir_log("Servidor iniciado")
        self.ventana.mainloop()
    
    def escribir_log(self, texto):
        hora = datetime.now().strftime('%H:%M:%S')
        self.log.insert(tk.END, f"[{hora}] {texto}\n")
        self.log.see(tk.END)
        num_clientes = len(self.clientes)
        self.label_info.config(text=f"Clientes: {num_clientes}/6")
    
    #Recibe datagramas de los clientes
    def recibir(self):
        while self.running:
            try:
                self.socket_servidor.settimeout(1)
                data, addr = self.socket_servidor.recvfrom(1024)
                msg = data.decode()
                
                #Procesa el mensaje segun su tipo
                partes = msg.split("|")
                tipo = partes[0]
                
                if tipo == 'CONECTAR':
                    username = partes[1] if len(partes) > 1 else ""
                    if len(self.clientes) >= MAX_CLIENTES:
                        self.socket_servidor.sendto("ERROR:Servidor lleno".encode(), addr)
                    else:
                        self.clientes[username] = (addr, time.time())
                        self.escribir_log(f"{username} se conecto")
                        self.socket_servidor.sendto("OK".encode(), addr)
                        self.enviar_lista_usuarios()
                
                elif tipo == 'KEEPALIVE':
                    username = partes[1] if len(partes) > 1 else ""
                    if username in self.clientes:
                        self.clientes[username] = (addr, time.time())
                
                elif tipo == 'BROADCAST':
                    username = partes[1] if len(partes) > 1 else ""
                    contenido = partes[2] if len(partes) > 2 else ""
                    if username in self.clientes:
                        self.clientes[username] = (addr, time.time())
                        self.escribir_log(f"{username}: {contenido}")
                        self.broadcast(f"{username}:{contenido}", username)
                
                elif tipo == 'PRIVADO':
                    username = partes[1] if len(partes) > 1 else ""
                    contenido = partes[2] if len(partes) > 2 else ""
                    dest = partes[3] if len(partes) > 3 else ""
                    if username in self.clientes:
                        self.clientes[username] = (addr, time.time())
                        self.escribir_log(f"{username} -> {dest}: {contenido}")
                        self.enviar_privado(username, dest, contenido)
                
                elif tipo == 'LISTA':
                    self.enviar_lista_usuarios(addr)
            except socket.timeout:
                continue
            except:
                pass
    
    #Envia mensaje a todos menos al que lo envio
    def broadcast(self, mensaje, excluir=None):
        for username, (addr, _) in self.clientes.items():
            if username != excluir:
                try:
                    self.socket_servidor.sendto(mensaje.encode(), addr)
                except:
                    pass
    
    #Envia mensaje privado
    def enviar_privado(self, remitente, destinatario, mensaje):
        if destinatario in self.clientes:
            addr_dest = self.clientes[destinatario][0]
            self.socket_servidor.sendto(f"PRIVADO:{remitente}:{mensaje}".encode(), addr_dest)
        if remitente in self.clientes:
            addr_rem = self.clientes[remitente][0]
            self.socket_servidor.sendto(f"PRIVADO:{remitente}:{mensaje}".encode(), addr_rem)
    
    #Envia la lista de usuarios conectados
    def enviar_lista_usuarios(self, addr=None):
        lista_temp = list(self.clientes.keys())
        usuarios = ",".join(lista_temp)
        data = f"USUARIOS:{usuarios}"
        
        if addr:
            try:
                self.socket_servidor.sendto(data.encode(), addr)
            except:
                pass
        else:
            for _, (a, _) in self.clientes.items():
                try:
                    self.socket_servidor.sendto(data.encode(), a)
                except:
                    pass
    
    #Elimina clientes que no responden
    def limpiar_inactivos(self):
        while self.running:
            time.sleep(5)
            ahora = time.time()
            inactivos = []
            
            for u, (_, t) in self.clientes.items():
                if ahora - t > 15:
                    inactivos.append(u)
            
            for username in inactivos:
                del self.clientes[username]
                self.escribir_log(f"{username} desconectado (timeout)")
                self.enviar_lista_usuarios()
    
    def apagar(self):
        self.running = False
        try:
            self.socket_servidor.close()
        except:
            pass
        self.ventana.destroy()
        sys.exit(0)

if __name__ == "__main__":
    ServidorUDP()
