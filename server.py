#!/usr/bin/env python3
"""
🌐 BOM Visualizer HTTP Server
Прост HTTP сървър за споделяне на bom_data.json в локална мрежа.

Използване:
    python server.py
    
По подразбиране стартира на: http://0.0.0.0:8080
Всички в локалната мрежа могат да достъпват: http://<твоят-IP>:8080
"""

import http.server
import socketserver
import json
import os
import sys
from datetime import datetime

# Опит за импортиране на qrcode библиотеката
try:
    import qrcode
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False

# Не използваме отделен файл за потребителски данни –
# всички данни се пазят централизирано в bom_data.json

# Настройки
PORT = 8080
BOM_FILE = "bom_data.json"
HOST = "0.0.0.0"  # Слуша на всички мрежови интерфейси

class BOMServerHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler с поддръжка за GET/POST на bom_data.json"""
    
    def do_GET(self):
        """Обработва GET заявки"""
        if self.path == "/get_bom":
            # Зареждане на bom_data.json от сървъра
            try:
                if os.path.exists(BOM_FILE):
                    with open(BOM_FILE, 'r', encoding='utf-8') as f:
                        bom_data = json.load(f)
                    
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(json.dumps(bom_data, ensure_ascii=False).encode('utf-8'))
                    print(f"📥 {datetime.now().strftime('%H:%M:%S')} - bom_data.json изпратен на клиент")
                else:
                    self.send_response(404)
                    self.send_header("Content-type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "BOM file not found"}).encode())
            except Exception as e:
                print(f"❌ Грешка при четене на BOM: {e}")
                self.send_response(500)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
                
        elif self.path == "/get_user_data":
            # Съвместимост: endpoint остава, но връща празни данни (не използваме отделен файл)
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({}).encode('utf-8'))
        else:
            # Нормални файлове (HTML, JSON, снимки)
            super().do_GET()
    
    def do_POST(self):
        """Обработва POST заявки за запазване на bom_data.json"""
        if self.path == "/save_bom_data":
            try:
                # Четем данните от заявката
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                bom_data = json.loads(post_data.decode('utf-8'))
                
                # ДИАГНОСТИКА: Проверяваме classification
                if 'classification' in bom_data:
                    print(f"🔍 Classification получена:")
                    print(f"   Workshop: {len(bom_data['classification'].get('workshop', []))} items")
                    print(f"   External: {len(bom_data['classification'].get('external', []))} items")
                    print(f"   Workshop items: {bom_data['classification'].get('workshop', [])}")
                    print(f"   External items: {bom_data['classification'].get('external', [])}")
                else:
                    print(f"⚠️ Няма classification секция в получените данни!")
                
                # Записваме директно bom_data.json (БЕЗ backup)
                with open(BOM_FILE, 'w', encoding='utf-8') as f:
                    json.dump(bom_data, f, ensure_ascii=False, indent=2)
                
                print(f"✅ {datetime.now().strftime('%H:%M:%S')} - bom_data.json записан успешно")
                
                # Връщаме успешен отговор
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success"}).encode())
                
            except Exception as e:
                print(f"❌ Грешка при запазване: {e}")
                self.send_response(500)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode())
        
        elif self.path == "/save_user_data":
            # Съвместимост: endpoint остава, но не прави запис (всичко се пише в bom_data.json)
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_OPTIONS(self):
        """Обработва OPTIONS заявки (CORS preflight)"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def log_message(self, format, *args):
        """Персонализиран лог"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {args[0]} - {args[1]}")

def get_local_ip():
    """Връща локалния IP адрес"""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"
def generate_shortcut(url):
    """Генерира пряк път (.url файл) за бърз достъп"""
    try:
        # Взимаме името на текущата директория
        folder_name = os.path.basename(os.getcwd())
        shortcut_filename = f"{folder_name}.url"
        
        shortcut_content = f"""[InternetShortcut]
URL={url}
IconIndex=0
"""
        with open(shortcut_filename, 'w', encoding='utf-8') as f:
            f.write(shortcut_content)
        
        print(f"🔗 Пряк път създаден: {shortcut_filename}")
        print(f"   Копирайте този файл на други компютри за бърз достъп!")
        
    except Exception as e:
        print(f"❌ Грешка при създаване на пряк път: {e}")

def generate_qr_code(url):
    """Генерира QR код за даден URL"""
    if not QR_AVAILABLE:
        print("⚠️  qrcode библиотеката не е инсталирана.")
        print("   За да видите QR код, инсталирайте: pip install qrcode[pil]")
        return
    
    try:
        # Генериране на QR код
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        # Запазване като PNG файл
        img = qr.make_image(fill_color="black", back_color="white")
        qr_filename = "bom_visualizer_qr.png"
        img.save(qr_filename)
        print(f"📱 QR код запазен като: {qr_filename}")
        
        # Показване в терминала като ASCII
        print("\n" + "=" * 60)
        print("📱 QR КОД ЗА МОБИЛЕН ДОСТЪП:")
        print("=" * 60)
        qr_terminal = qrcode.QRCode(border=2)
        qr_terminal.add_data(url)
        qr_terminal.make(fit=True)
        qr_terminal.print_ascii(invert=True)
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"❌ Грешка при генериране на QR код: {e}")
if __name__ == "__main__":
    # Проверка за bom_data.json
    if not os.path.exists(BOM_FILE):
        print(f"⚠️  ВНИМАНИЕ: {BOM_FILE} не съществува!")
        print(f"   Моля поставете {BOM_FILE} в същата папка като server.py")
        print()
        sys.exit(1)
    
    # Стартиране на сървъра
    with socketserver.TCPServer((HOST, PORT), BOMServerHandler) as httpd:
        local_ip = get_local_ip()
        network_url = f"http://{local_ip}:{PORT}/unified_bom_viewer.html"
        
        print("=" * 60)
        print("🌐 BOM Visualizer Server СТАРТИРАН!")
        print("=" * 60)
        print(f"📂 Споделена папка: {os.getcwd()}")
        print(f"📄 BOM файл: {BOM_FILE}")
        print()
        print("🔗 Достъп до приложението:")
        print(f"   От този компютър:  http://localhost:{PORT}/unified_bom_viewer.html")
        print(f"   От локалната мрежа: {network_url}")
        print()
        
        # Генериране на пряк път и QR код
        generate_shortcut(network_url)
        generate_qr_code(network_url)
        
        print("💡 Инструкции:")
        print("   1. Отворете горния линк в браузър")
        print("   2. Или използвайте BOM_Visualizer.url файла (копирайте го на други компютри)")
        print("   3. Или сканирайте QR кода с мобилен телефон")
        print("   4. Класифицирайте сборките в Admin режим")
        print("   5. Промените се запазват автоматично в bom_data.json")
        print("   6. Всички потребители виждат промените веднага")
        print()
        print("⏹️  За спиране натиснете Ctrl+C")
        print("=" * 60)
        print()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n🛑 Сървърът е спрян.")
            sys.exit(0)
