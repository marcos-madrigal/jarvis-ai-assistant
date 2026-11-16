import os
import base64
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send'
]

class GestorGmail:
    def __init__(self):
        self.ultimos_ids = []

    def autenticar(self):
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        return creds

    def obtener_correos(self, solo_no_leidos=False, incluir_todo=False, busqueda_libre=""):
        try:
            creds = self.autenticar()
            servicio = build('gmail', 'v1', credentials=creds)
            
            filtros = []
            if busqueda_libre:
                filtros.append(busqueda_libre)
            else:
                if solo_no_leidos:
                    filtros.append('is:unread')
                if not incluir_todo:
                    filtros.append('category:primary')
                
            query = ' '.join(filtros)
            resultados = servicio.users().messages().list(userId='me', maxResults=3, q=query).execute()
            mensajes = resultados.get('messages', [])

            if not mensajes:
                return "No he encontrado correos bajo esos criterios."

            self.ultimos_ids = [m['id'] for m in mensajes]
            texto_correos = ""
            for i, mensaje in enumerate(mensajes):
                msg = servicio.users().messages().get(userId='me', id=mensaje['id'], format='metadata').execute()
                cabeceras = msg['payload']['headers']
                asunto = next((header['value'] for header in cabeceras if header['name'] == 'Subject'), "Sin asunto")
                remitente = next((header['value'] for header in cabeceras if header['name'] == 'From'), "Desconocido")
                
                remitente_limpio = remitente.split('<')[0].strip()
                texto_correos += f"\n[{i+1}] De: {remitente_limpio} | Asunto: {asunto}"
            
            return texto_correos
        except Exception as e:
            return f"Error accediendo a la red de Gmail: {str(e)}"

    def obtener_cuerpo_correo(self, id_correo):
        try:
            creds = self.autenticar()
            servicio = build('gmail', 'v1', credentials=creds)
            msg = servicio.users().messages().get(userId='me', id=id_correo, format='full').execute()
            
            def extraer_texto(payload):
                if 'data' in payload.get('body', {}):
                    return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
                if 'parts' in payload:
                    for part in payload['parts']:
                        if part['mimeType'] == 'text/plain':
                            if 'data' in part['body']:
                                return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        elif 'parts' in part:
                            return extraer_texto(part)
                return ""

            texto = extraer_texto(msg['payload'])
            return texto if texto else "No se pudo extraer texto legible."
        except Exception as e:
            return f"Error leyendo el correo: {str(e)}"

    def enviar_correo(self, destinatario, asunto, cuerpo):
        try:
            creds = self.autenticar()
            servicio = build('gmail', 'v1', credentials=creds)
            
            mensaje = EmailMessage()
            mensaje.set_content(cuerpo)
            mensaje['To'] = destinatario
            mensaje['From'] = 'me'
            mensaje['Subject'] = asunto
            
            encoded_message = base64.urlsafe_b64encode(mensaje.as_bytes()).decode()
            crear_mensaje = {'raw': encoded_message}
            
            servicio.users().messages().send(userId='me', body=crear_mensaje).execute()
            return f"He enviado el correo exitosamente a {destinatario}."
        except Exception as e:
            return f"He encontrado un error al intentar enviar el correo: {str(e)}"