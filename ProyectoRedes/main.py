"""
Main - Menú principal
"""
import tkinter as tk

class Menu:
    def __init__(self):
        self.ventana = tk.Tk()
        self.ventana.title("Chat - Menú")
        self.ventana.geometry("500x250")
        
        tk.Label(self.ventana, text="Chat TCP/UDP", 
                font=("Arial", 20, "bold")).pack(pady=20)
        
        #Botones de servidor
        frame_server = tk.Frame(self.ventana)
        frame_server.pack(pady=10)
        
        tk.Label(frame_server, text="Servidor:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_server, text="TCP", command=lambda: self.config_servidor('tcp'),
                 font=("Arial", 11), width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_server, text="UDP", command=lambda: self.config_servidor('udp'),
                 font=("Arial", 11), width=10).pack(side=tk.LEFT, padx=5)
        
        #Botones de cliente
        frame_client = tk.Frame(self.ventana)
        frame_client.pack(pady=10)
        
        tk.Label(frame_client, text="Cliente:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_client, text="TCP", command=lambda: self.config_cliente('tcp'),
                 font=("Arial", 11), width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_client, text="UDP", command=lambda: self.config_cliente('udp'),
                 font=("Arial", 11), width=10).pack(side=tk.LEFT, padx=5)
        
        self.ventana.mainloop()
    
    #Configuración de servidor
    def config_servidor(self, protocolo):
        config = tk.Toplevel()
        config.title(f"Configurar Servidor {protocolo.upper()}")
        config.geometry("350x200")
        
        tk.Label(config, text=f"Servidor {protocolo.upper()}", 
                font=("Arial", 14, "bold")).pack(pady=10)
        
        frame_ip = tk.Frame(config)
        frame_ip.pack(pady=5)
        tk.Label(frame_ip, text="IP:", width=8).pack(side=tk.LEFT)
        entrada_ip = tk.Entry(frame_ip, width=20)
        entrada_ip.insert(0, "0.0.0.0")
        entrada_ip.pack(side=tk.LEFT)
        
        frame_puerto = tk.Frame(config)
        frame_puerto.pack(pady=5)
        tk.Label(frame_puerto, text="Puerto:", width=8).pack(side=tk.LEFT)
        entrada_puerto = tk.Entry(frame_puerto, width=20)
        entrada_puerto.insert(0, "5555" if protocolo == 'tcp' else "5556")
        entrada_puerto.pack(side=tk.LEFT)
        
        def iniciar():
            ip = entrada_ip.get().strip()
            puerto = entrada_puerto.get().strip()
            
            if not puerto.isdigit():
                tk.messagebox.showerror("Error", "Puerto debe ser un número")
                return
            
            try:
                config.destroy()
                self.ventana.withdraw()
            except:
                pass
            
            if protocolo == 'tcp':
                from tcp_server import ServidorTCP
                ServidorTCP(ip, int(puerto))
            else:
                from udp_server import ServidorUDP
                ServidorUDP(ip, int(puerto))
        
        tk.Button(config, text="Iniciar Servidor", command=iniciar,
                 font=("Arial", 12)).pack(pady=20)
    
    #Configuración de cliente
    def config_cliente(self, protocolo):
        config = tk.Toplevel()
        config.title(f"Conectar {protocolo.upper()}")
        config.geometry("350x250")
        
        tk.Label(config, text=f"Cliente {protocolo.upper()}", 
                font=("Arial", 14, "bold")).pack(pady=10)
        
        frame_user = tk.Frame(config)
        frame_user.pack(pady=5)
        tk.Label(frame_user, text="Usuario:", width=10).pack(side=tk.LEFT)
        entrada_user = tk.Entry(frame_user, width=20)
        entrada_user.pack(side=tk.LEFT)
        entrada_user.focus()
        
        frame_ip = tk.Frame(config)
        frame_ip.pack(pady=5)
        tk.Label(frame_ip, text="IP:", width=10).pack(side=tk.LEFT)
        entrada_ip = tk.Entry(frame_ip, width=20)
        entrada_ip.insert(0, "127.0.0.1")
        entrada_ip.pack(side=tk.LEFT)
        
        frame_puerto = tk.Frame(config)
        frame_puerto.pack(pady=5)
        tk.Label(frame_puerto, text="Puerto:", width=10).pack(side=tk.LEFT)
        entrada_puerto = tk.Entry(frame_puerto, width=20)
        entrada_puerto.insert(0, "5555" if protocolo == 'tcp' else "5556")
        entrada_puerto.pack(side=tk.LEFT)
        
        def conectar():
            username = entrada_user.get().strip()
            ip = entrada_ip.get().strip()
            puerto = entrada_puerto.get().strip()
            
            if not username:
                tk.messagebox.showerror("Error", "Ingresa un usuario")
                return
            
            if not puerto.isdigit():
                tk.messagebox.showerror("Error", "Puerto debe ser un número")
                return
            
            try:
                config.destroy()
                self.ventana.withdraw()
            except:
                pass
            
            if protocolo == 'tcp':
                from tcp_client import ClienteTCP
                ClienteTCP(username, ip, int(puerto))
            else:
                from udp_client import ClienteUDP
                ClienteUDP(username, ip, int(puerto))
        
        tk.Button(config, text="Conectar", command=conectar,
                 font=("Arial", 12)).pack(pady=20)
        entrada_user.bind("<Return>", lambda e: conectar())

if __name__ == "__main__":
    Menu()
