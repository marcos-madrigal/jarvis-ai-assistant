import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Pedimos permiso de lectura SOLO para Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def autenticar():
    creds = None
    # Si ya existe el token, lo carga directamente
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # Si no hay token o está caducado, pide permiso en el navegador
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Guarda el token mágico para no volver a pedir login
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

if __name__ == '__main__':
    print("Iniciando conexión con Gmail...")
    credenciales = autenticar()
    
    try:
        # Probamos conectando a la API de Gmail
        servicio = build('gmail', 'v1', credentials=credenciales)
        print("\n¡Conexión exitosa! Buscando tus últimos 3 correos...")
        
        # Pedimos la lista de los últimos 3 mensajes
        resultados = servicio.users().messages().list(userId='me', maxResults=3).execute()
        mensajes = resultados.get('messages', [])

        if not mensajes:
            print('No tienes correos en tu bandeja.')
        else:
            for mensaje in mensajes:
                # Obtenemos los detalles (metadatos) de cada correo
                msg = servicio.users().messages().get(userId='me', id=mensaje['id'], format='metadata').execute()
                
                # Extraemos el asunto y el remitente de las cabeceras
                cabeceras = msg['payload']['headers']
                asunto = next((header['value'] for header in cabeceras if header['name'] == 'Subject'), "Sin asunto")
                remitente = next((header['value'] for header in cabeceras if header['name'] == 'From'), "Desconocido")
                
                print(f"- De: {remitente} \n  Asunto: {asunto}\n")
                
    except Exception as e:
        print(f"\nError de conexión: {e}")