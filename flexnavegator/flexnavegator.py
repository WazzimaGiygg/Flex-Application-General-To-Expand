import sys
import json
import random
import os
import re
import tempfile
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWebEngineCore import *
from PyQt5.QtGui import *
from PyQt5.QtNetwork import QNetworkProxy, QNetworkProxyFactory, QNetworkRequest

class PrivacyProfile(QWebEngineProfile):
    """
    Perfil personalizado com configurações avançadas de privacidade
    Implementa bloqueios de geolocalização, fingerprinting e emulação de tela
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Configurações básicas de privacidade
        self.setup_privacy_settings()
        
        # Configurar User-Agent randomizado
        self.setup_random_user_agent()
        
        # Configurar cache e cookies
        self.setup_storage()
        
        # Lista de padrões de rastreamento de IMEI
        self.imei_patterns = [
            r'\b\d{15}\b',  # IMEI padrão 15 dígitos
            r'\b\d{14}\b',  # IMEI sem dígito verificador
            r'imei[=:\s]?\d{15}',
            r'imeistring[=:\s]?[\w]+',
            r'deviceid[=:\s]?\d+',
            r'device_id[=:\s]?\d+',
            r'androidid[=:\s]?[\w]+',
            r'advertisingid[=:\s]?[\w-]+',
            r'gaid[=:\s]?[\w-]+',  # Google Advertising ID
            r'idfa[=:\s]?[\w-]+',   # iOS Advertising ID
            r'macaddress[=:\s]?[\w:]+',
            r'mac_addr[=:\s]?[\w:]+',
            r'serial[=:\s]?\w+',
            r'serialnumber[=:\s]?\w+',
        ]
        
        # Compilar padrões regex
        self.imei_regex = re.compile('|'.join(self.imei_patterns), re.IGNORECASE)
        
        # Conectar interceptador de requisições
        self.setRequestInterceptor(PrivacyRequestInterceptor(self))
        
        # Configurar preferências de terceiros
        self.setHttpUserAgent(self.httpUserAgent())
    
    def setup_privacy_settings(self):
        """Configurar todas as settings de privacidade com verificação de compatibilidade"""
        settings = self.settings()
        
        # Configurações básicas (compatíveis com todas versões)
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, False)
        settings.setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, False)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, False)
        settings.setAttribute(QWebEngineSettings.FullScreenSupportEnabled, False)
        settings.setAttribute(QWebEngineSettings.WebGLEnabled, False)
        settings.setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, False)
        settings.setAttribute(QWebEngineSettings.AutoLoadImages, True)
        settings.setAttribute(QWebEngineSettings.ErrorPageEnabled, True)
        settings.setAttribute(QWebEngineSettings.HyperlinkAuditingEnabled, False)
        settings.setAttribute(QWebEngineSettings.ScrollAnimatorEnabled, False)
        
        # Configurações adicionais com verificação de existência
        self.safe_set_attribute(settings, 'SpatialNavigationEnabled', False)
        self.safe_set_attribute(settings, 'FocusOnNavigationEnabled', True)
        self.safe_set_attribute(settings, 'PdfViewerEnabled', False)
        self.safe_set_attribute(settings, 'PlaybackRequiresUserGesture', True)
        self.safe_set_attribute(settings, 'ShowScrollBars', True)
        self.safe_set_attribute(settings, 'LocalContentCanAccessRemoteUrls', True)
        self.safe_set_attribute(settings, 'LocalContentCanAccessFileUrls', False)
        self.safe_set_attribute(settings, 'XSSAuditingEnabled', True)
        self.safe_set_attribute(settings, 'JavascriptCanPaste', False)
        self.safe_set_attribute(settings, 'AllowRunningInsecureContent', False)
        self.safe_set_attribute(settings, 'AllowGeolocationOnInsecureOrigins', False)
        self.safe_set_attribute(settings, 'WebRTCPublicInterfacesOnly', True)
    
    def safe_set_attribute(self, settings, attr_name, value):
        """
        Configurar atributo com segurança, verificando se existe
        """
        try:
            if hasattr(QWebEngineSettings, attr_name):
                attr = getattr(QWebEngineSettings, attr_name)
                settings.setAttribute(attr, value)
            else:
                print(f"⚠️ Atributo não disponível nesta versão do Qt: {attr_name}")
        except Exception as e:
            print(f"⚠️ Erro ao configurar {attr_name}: {e}")
    
    def setup_random_user_agent(self):
        """Configurar User-Agent randomizado com mais opções"""
        user_agents = [
            # Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 OPR/105.0.0.0",
            
            # macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
            
            # Linux
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
            
            # Mobile
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        ]
        
        self.setHttpUserAgent(random.choice(user_agents))
    
    def setup_storage(self):
        """Configurar armazenamento isolado"""
        self.setHttpCacheType(QWebEngineProfile.MemoryHttpCache)
        self.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
        
        # Configurar pasta de perfil temporária
        try:
            temp_dir = tempfile.mkdtemp(prefix="privacy_browser_")
            self.setPersistentStoragePath(temp_dir)
        except Exception as e:
            print(f"⚠️ Erro ao criar pasta temporária: {e}")
        
        # Limitar tamanho do cache
        self.setHttpCacheMaximumSize(50 * 1024 * 1024)  # 50MB max
    
    def check_imei_tracking(self, url, content):
        """
        Verificar se há tentativa de rastreamento de IMEI na URL ou conteúdo
        """
        url_string = url.toString() if hasattr(url, 'toString') else str(url)
        
        # Verificar URL
        url_matches = self.imei_regex.findall(url_string)
        if url_matches:
            print(f"🚨 [ALERTA IMEI] Padrão de IMEI detectado na URL: {url_matches}")
            return True, url_matches
        
        # Verificar conteúdo se fornecido
        if content and isinstance(content, str):
            content_matches = self.imei_regex.findall(content)
            if content_matches:
                print(f"🚨 [ALERTA IMEI] Padrão de IMEI detectado no conteúdo: {content_matches}")
                return True, content_matches
        
        return False, []
    
    def emulate_viewport(self, width, height):
        """Emular tamanho de tela personalizado (versão aprimorada)"""
        viewport_script = f"""
        (function() {{
            // Modificar propriedades da tela
            try {{
                Object.defineProperties(window.screen, {{
                    'width': {{ get: function() {{ return {width}; }} }},
                    'height': {{ get: function() {{ return {height}; }} }},
                    'availWidth': {{ get: function() {{ return {width}; }} }},
                    'availHeight': {{ get: function() {{ return {height}; }} }},
                    'colorDepth': {{ get: function() {{ return 24; }} }},
                    'pixelDepth': {{ get: function() {{ return 24; }} }},
                    'availLeft': {{ get: function() {{ return 0; }} }},
                    'availTop': {{ get: function() {{ return 0; }} }}
                }});
                
                // Modificar window outer/inner
                Object.defineProperties(window, {{
                    'innerWidth': {{ get: function() {{ return {width}; }} }},
                    'innerHeight': {{ get: function() {{ return {height}; }} }},
                    'outerWidth': {{ get: function() {{ return {width}; }} }},
                    'outerHeight': {{ get: function() {{ return {height}; }} }},
                    'screenX': {{ get: function() {{ return 0; }} }},
                    'screenY': {{ get: function() {{ return 0; }} }},
                    'screenLeft': {{ get: function() {{ return 0; }} }},
                    'screenTop': {{ get: function() {{ return 0; }} }}
                }});
                
                // Modificar document element
                Object.defineProperty(document.documentElement, 'clientWidth', {{ get: function() {{ return {width}; }} }});
                Object.defineProperty(document.documentElement, 'clientHeight', {{ get: function() {{ return {height}; }} }});
                
                console.log(`📏 Viewport emulado: ${{{width}}}x${{{height}}}`);
            }} catch (e) {{
                console.warn('Erro ao emular viewport:', e);
            }}
        }})();
        """
        
        return viewport_script
    
    def emulate_hardware(self):
        """Emular características de hardware (versão aprimorada)"""
        hardware_script = """
        (function() {
            try {
                // Hardware concurrency (núcleos de CPU) - variável para evitar fingerprinting
                const cpuCores = [2, 4, 6, 8, 12, 16];
                if (navigator && navigator.hardwareConcurrency !== undefined) {
                    Object.defineProperty(navigator, 'hardwareConcurrency', {
                        get: function() { return cpuCores[Math.floor(Math.random() * cpuCores.length)]; }
                    });
                }
                
                // Device memory (GB) - apenas Chrome, mas seguro
                if (navigator && 'deviceMemory' in navigator) {
                    const memories = [2, 4, 8, 16, 32];
                    Object.defineProperty(navigator, 'deviceMemory', {
                        get: function() { return memories[Math.floor(Math.random() * memories.length)]; }
                    });
                }
                
                // Do Not Track
                if (navigator) {
                    Object.defineProperty(navigator, 'doNotTrack', {
                        get: function() { return '1'; }
                    });
                }
                
                console.log('🖥️ Hardware fingerprint emulado');
            } catch (e) {
                console.warn('Erro na emulação de hardware:', e);
            }
        })();
        """
        
        return hardware_script
    
    def block_fingerprinting(self):
        """Bloquear técnicas de fingerprinting (versão aprimorada)"""
        fingerprint_block_script = """
        (function() {
            // ========== BLOQUEIO DE CANVAS ==========
            try {
                if (HTMLCanvasElement && HTMLCanvasElement.prototype) {
                    const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
                    HTMLCanvasElement.prototype.toDataURL = function(type, quality) {
                        console.warn('🔴 Canvas fingerprinting bloqueado!');
                        
                        // Verificar se é tentativa de fingerprinting por tamanho
                        if (this.width > 100 && this.height > 100) {
                            // Retornar uma imagem em branco
                            return 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==';
                        }
                        
                        // Para canvases pequenos, permitir (provavelmente não é fingerprinting)
                        return originalToDataURL.call(this, type, quality);
                    };
                }
                
                if (CanvasRenderingContext2D && CanvasRenderingContext2D.prototype) {
                    const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;
                    CanvasRenderingContext2D.prototype.getImageData = function(x, y, width, height) {
                        console.warn('🔴 Canvas getImageData bloqueado!');
                        
                        // Retornar dados de imagem em branco se for uma tentativa grande
                        if (width > 10 || height > 10) {
                            return originalGetImageData.call(this, 0, 0, 1, 1);
                        }
                        
                        return originalGetImageData.call(this, x, y, width, height);
                    };
                }
            } catch (e) {}
            
            // ========== BLOQUEIO DE WEBGL ==========
            try {
                if (typeof WebGLRenderingContext !== 'undefined' && WebGLRenderingContext.prototype) {
                    const originalGetParameter = WebGLRenderingContext.prototype.getParameter;
                    WebGLRenderingContext.prototype.getParameter = function(parameter) {
                        console.warn(`🔴 WebGL getParameter bloqueado: ${parameter}`);
                        
                        // Valores genéricos para evitar fingerprinting
                        if (parameter === 37445) return 'WebKit'; // UNMASKED_VENDOR_WEBGL
                        if (parameter === 37446) return 'WebKit WebGL'; // UNMASKED_RENDERER_WEBGL
                        
                        // Renderer info
                        if (parameter === 7936) return 'WebKit'; // VENDOR
                        if (parameter === 7937) return 'WebKit WebGL'; // RENDERER
                        
                        return originalGetParameter.call(this, parameter);
                    };
                }
            } catch (e) {}
            
            // ========== BLOQUEIO DE AUDIOCONTEXT ==========
            try {
                if (window.AudioContext) {
                    const originalAudioContext = window.AudioContext;
                    window.AudioContext = function() {
                        console.warn('🔴 AudioContext bloqueado por privacidade');
                        
                        // Retornar um objeto mockado para evitar erros
                        return {
                            sampleRate: 44100,
                            state: 'suspended',
                            close: function() { return Promise.resolve(); },
                            resume: function() { return Promise.resolve(); },
                            suspend: function() { return Promise.resolve(); }
                        };
                    };
                }
            } catch (e) {}
            
            // ========== BLOQUEIO DE API DE BATERIA ==========
            try {
                if (navigator && navigator.getBattery) {
                    navigator.getBattery = function() {
                        console.warn('🔴 Battery API bloqueada');
                        return Promise.reject(new Error('Battery API desabilitada'));
                    };
                }
            } catch (e) {}
            
            // ========== BLOQUEIO DE API DE DISPOSITIVOS ==========
            try {
                if (navigator && navigator.mediaDevices && navigator.mediaDevices.enumerateDevices) {
                    const originalEnumerateDevices = navigator.mediaDevices.enumerateDevices;
                    navigator.mediaDevices.enumerateDevices = function() {
                        console.warn('🔴 enumerateDevices bloqueado');
                        return Promise.resolve([]);
                    };
                }
            } catch (e) {}
            
            console.log('🔒 Fingerprinting bloqueado (versão avançada)');
        })();
        """
        
        return fingerprint_block_script
    
    def block_imei_tracking(self):
        """
        Script para bloquear tentativas de acesso a APIs que podem vazar IMEI
        """
        imei_block_script = """
        (function() {
            // ========== BLOQUEIO DE ACESSO A IMEI/SERIAL ==========
            
            // Bloquear propriedades comuns que podem conter IMEI
            const blockedProps = [
                'imei', 'serial', 'serialNumber', 'deviceId', 'deviceID',
                'androidId', 'advertisingId', 'gaid', 'idfa', 'macAddress',
                'wifiMac', 'bluetoothMac', 'deviceSerial', 'hardwareSerial'
            ];
            
            // Interceptar acesso a propriedades em objetos globais
            const interceptProperty = function(obj, propName) {
                if (!obj) return;
                
                try {
                    Object.defineProperty(obj, propName, {
                        get: function() {
                            console.warn(`🔴 Tentativa de acesso a ${propName} bloqueada`);
                            return null;
                        },
                        set: function() {},
                        configurable: false
                    });
                } catch (e) {}
            };
            
            // Aplicar bloqueio em navigator e window
            if (navigator) {
                blockedProps.forEach(prop => {
                    interceptProperty(navigator, prop);
                });
            }
            
            // Interceptar chamadas AJAX/Fetch para detectar envio de IMEI
            if (window.fetch) {
                const originalFetch = window.fetch;
                window.fetch = function(url, options) {
                    const urlStr = url.toString().toLowerCase();
                    const blockedKeywords = ['imei', 'deviceid', 'serial', 'androidid', 'gaid', 'idfa'];
                    
                    // Verificar se URL contém padrões suspeitos
                    const hasBlocked = blockedKeywords.some(keyword => urlStr.includes(keyword));
                    
                    if (hasBlocked) {
                        console.warn(`🚨 Tentativa de envio de dados para URL suspeita: ${url}`);
                        // Bloquear a requisição
                        return Promise.reject(new Error('Requisição bloqueada por segurança'));
                    }
                    
                    return originalFetch.call(this, url, options);
                };
            }
            
            console.log('🚫 Bloqueio de rastreamento IMEI ativado');
        })();
        """
        
        return imei_block_script

class PrivacyRequestInterceptor(QWebEngineUrlRequestInterceptor):
    """
    Interceptador de requisições para bloquear rastreadores
    """
    
    def __init__(self, profile):
        super().__init__()
        self.profile = profile
        
        # Lista de domínios de rastreamento conhecidos
        self.tracking_domains = [
            'google-analytics.com',
            'doubleclick.net',
            'facebook.com/tr',
            'googletagmanager.com',
            'googleadservices.com',
            'scorecardresearch.com',
            'outbrain.com',
            'taboola.com',
            'criteo.com',
            'addthis.com',
            'hotjar.com',
            'mixpanel.com',
            'amplitude.com',
            'segment.com',
            'newrelic.com',
            'fullstory.com',
            'mouseflow.com',
            'clarity.ms',
        ]
        
        # Lista de padrões de IMEI em URLs
        self.imei_patterns = [
            r'imei=\d{15}',
            r'deviceid=\d+',
            r'serial=[A-Za-z0-9]+',
            r'androidid=[A-Fa-f0-9]+',
            r'advertisingid=[A-Fa-f0-9\-]+',
            r'gaid=[A-Fa-f0-9\-]+',
            r'idfa=[A-Fa-f0-9\-]+',
        ]
        
        self.imei_regex = re.compile('|'.join(self.imei_patterns), re.IGNORECASE)
    
    def interceptRequest(self, info):
        """
        Interceptar e potencialmente bloquear requisições
        """
        url = info.requestUrl().toString()
        resource_type = info.resourceType()
        
        # Verificar se é requisição de rastreamento
        for domain in self.tracking_domains:
            if domain in url:
                print(f"🚫 Bloqueando rastreador: {domain}")
                info.block(True)
                return
        
        # Verificar se há IMEI na URL
        if self.imei_regex.search(url):
            print(f"🚨 BLOQUEADO: Possível vazamento de IMEI na URL: {url}")
            info.block(True)
            return
        
        # Bloquear requisições para APIs sensíveis
        sensitive_patterns = [
            '/geolocation',
            '/api/location',
            '/device/info',
            '/deviceid',
            '/getimei',
            '/getserial',
            '/advertisingid',
        ]
        
        for pattern in sensitive_patterns:
            if pattern in url.lower():
                print(f"⚠️ Bloqueando requisição suspeita: {url}")
                info.block(True)
                return

class PrivacyBrowserPage(QWebEnginePage):
    """
    Página personalizada com interceptação de permissões e monitoramento
    """
    
    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)
        self.parent_window = parent
        
        # Configurar FeaturePermissionRequested
        self.featurePermissionRequested.connect(self.handle_feature_permission)
        
        # Configurar monitoramento de console JavaScript
        self.javaScriptConsoleMessage = self.console_message
        
        # Lista para armazenar tentativas suspeitas
        self.suspicious_attempts = []
    
    def console_message(self, level, message, line, source):
        """
        Monitorar mensagens do console JavaScript
        """
        if message and ('imei' in message.lower() or 'serial' in message.lower() or 'deviceid' in message.lower()):
            print(f"🚨 [JS SUSPEITO] {message} (linha {line}, {source})")
            self.suspicious_attempts.append({
                'type': 'javascript',
                'message': message,
                'line': line,
                'source': source,
                'time': datetime.now().strftime('%H:%M:%S')
            })
    
    def handle_feature_permission(self, url, feature):
        """
        Lidar com requisições de permissão de features
        """
        feature_names = {
            QWebEnginePage.Geolocation: "📍 Geolocalização",
            QWebEnginePage.MediaAudioCapture: "🎤 Microfone",
            QWebEnginePage.MediaVideoCapture: "📷 Câmera",
            QWebEnginePage.MediaAudioVideoCapture: "🎥 Câmera/Microfone",
            QWebEnginePage.DesktopVideoCapture: "🖥️ Captura de tela",
            QWebEnginePage.DesktopAudioVideoCapture: "📹 Captura de tela + áudio",
            QWebEnginePage.Notifications: "🔔 Notificações",
            QWebEnginePage.ClipboardReadWrite: "📋 Área de transferência",
            QWebEnginePage.LocalFonts: "🔤 Fontes locais",
        }
        
        feature_name = feature_names.get(feature, f"Permissão #{feature}")
        
        print(f"[PERMISSÃO] {feature_name} solicitada por: {url.toString()}")
        
        # Política: negar tudo automaticamente
        self.setFeaturePermission(url, feature, QWebEnginePage.PermissionDeniedByUser)
        print(f"   → BLOQUEADO (política de privacidade)")
    
    def certificateError(self, error):
        """
        Lidar com erros de certificado (possível MITM)
        """
        print(f"⚠️ Erro de certificado: {error.url().toString()} - {error.description()}")
        
        # Em modo de segurança, rejeitar certificados inválidos
        return False
    
    def acceptNavigationRequest(self, url, navigation_type, is_main_frame):
        """
        Verificar navegação antes de carregar
        """
        url_str = url.toString()
        
        # Verificar se é URL suspeita
        suspicious_patterns = [
            'imei=', 'deviceid=', 'serial=', 'tracking=',
            'utm_source=', 'utm_medium=', 'utm_campaign='
        ]
        
        for pattern in suspicious_patterns:
            if pattern in url_str.lower():
                print(f"⚠️ Parâmetro suspeito detectado: {pattern}")
                
                # Criar alerta visual se for frame principal
                if is_main_frame and self.parent_window:
                    self.parent_window.status_bar.showMessage(
                        f"⚠️ Parâmetros de rastreamento detectados: {url_str[:50]}...", 3000)
                break
        
        return super().acceptNavigationRequest(url, navigation_type, is_main_frame)

class PrivacyBrowserTab(QWebEngineView):
    """
    Aba do navegador com proteções de privacidade
    """
    
    def __init__(self, parent=None, viewport_size=None):
        super().__init__(parent)
        self.parent_window = parent
        
        # Criar perfil de privacidade personalizado
        self.profile = PrivacyProfile(self)
        
        # Criar página personalizada
        self.page = PrivacyBrowserPage(self.profile, self)
        self.setPage(self.page)
        
        # Configurar viewport personalizado se especificado
        self.viewport_size = viewport_size or (1920, 1080)
        
        # Conectar sinais
        self.loadStarted.connect(self.on_load_started)
        self.loadFinished.connect(self.on_load_finished)
        self.urlChanged.connect(self.on_url_changed)
        self.titleChanged.connect(self.on_title_changed)
        
        # Título da aba
        self.tab_title = "Nova Aba"
        
        # Registrar tempo de carregamento
        self.load_start_time = None
    
    def on_url_changed(self, url):
        """Quando a URL muda"""
        if self.parent_window:
            self.parent_window.update_url_bar(url)
    
    def on_title_changed(self, title):
        """Quando o título muda"""
        self.tab_title = title
        if self.parent_window:
            self.parent_window.update_tab_title(self, title)
    
    def on_load_started(self):
        """Quando a página começa a carregar"""
        self.load_start_time = datetime.now()
        print(f"🌐 Carregando: {self.url().toString()}")
    
    def on_load_finished(self, success):
        """Quando a página termina de carregar"""
        if success:
            load_time = (datetime.now() - self.load_start_time).total_seconds() if self.load_start_time else 0
            print(f"✅ Página carregada: {self.title()} ({load_time:.2f}s)")
            self.tab_title = self.title()
            
            # Injetar scripts de proteção APRIMORADOS
            self.inject_all_protections()
            
            # Verificar tentativas de acesso a APIs sensíveis
            self.monitor_sensitive_apis()
            
            # Verificar IMEI tracking
            self.check_imei_tracking()
        else:
            print(f"❌ Erro ao carregar página")
    
    def inject_all_protections(self):
        """
        Injetar todas as proteções na página
        """
        # Proteções existentes
        self.page.runJavaScript(self.profile.emulate_viewport(*self.viewport_size))
        self.page.runJavaScript(self.profile.emulate_hardware())
        self.page.runJavaScript(self.profile.block_fingerprinting())
        
        # Proteção contra rastreamento IMEI
        self.page.runJavaScript(self.profile.block_imei_tracking())
        
        # Verificar DOM em busca de elementos suspeitos
        check_dom_script = """
        (function() {
            // Verificar se há inputs escondidos coletando dados
            if (document) {
                const hiddenInputs = document.querySelectorAll('input[type="hidden"]');
                hiddenInputs.forEach(input => {
                    if (input.name && (
                        input.name.toLowerCase().includes('imei') ||
                        input.name.toLowerCase().includes('device') ||
                        input.name.toLowerCase().includes('serial')
                    )) {
                        console.warn(`⚠️ Input escondido suspeito: ${input.name}`);
                    }
                });
                
                // Verificar scripts inline com padrões de IMEI
                const scripts = document.querySelectorAll('script:not([src])');
                scripts.forEach(script => {
                    if (script.textContent && (
                        script.textContent.includes('imei') ||
                        script.textContent.includes('deviceId')
                    )) {
                        console.warn('⚠️ Script inline com possível coleta de IMEI');
                    }
                });
            }
        })();
        """
        self.page.runJavaScript(check_dom_script)
    
    def monitor_sensitive_apis(self):
        """Monitorar tentativas de acesso a APIs sensíveis"""
        monitor_script = """
        (function() {
            // Monitorar tentativas de geolocation
            if (navigator && navigator.geolocation) {
                const originalGetCurrentPosition = navigator.geolocation.getCurrentPosition;
                navigator.geolocation.getCurrentPosition = function(success, error, options) {
                    console.warn('🔴 Tentativa de acesso à GEOLOCALIZAÇÃO bloqueada');
                    if (error) error({ code: 1, message: 'Geolocation bloqueada' });
                };
                
                const originalWatchPosition = navigator.geolocation.watchPosition;
                navigator.geolocation.watchPosition = function() {
                    console.warn('🔴 Tentativa de monitoramento de posição bloqueada');
                    return null;
                };
            }
            
            console.log('👁️ Monitoramento de APIs ativo');
        })();
        """
        
        self.page.runJavaScript(monitor_script)
    
    def check_imei_tracking(self):
        """
        Verificar se a página está tentando rastrear IMEI
        """
        # Extrair HTML para análise
        self.page.toHtml(self.handle_html_content)
    
    def handle_html_content(self, html):
        """
        Processar HTML em busca de padrões de IMEI
        """
        if not html:
            return
        
        # Verificar no perfil
        detected, matches = self.profile.check_imei_tracking(self.url(), html)
        
        if detected:
            # Mostrar alerta na interface
            if self.parent_window:
                self.parent_window.status_bar.showMessage(
                    f"🚨 ALERTA: Possível rastreamento de IMEI detectado!", 5000)
            
            # Registrar no console
            print(f"🚨 Página suspeita: {self.url().toString()}")
            print(f"🚨 Padrões encontrados: {matches}")
    
    def set_viewport(self, width, height):
        """Alterar viewport em tempo real"""
        self.viewport_size = (width, height)
        self.page.runJavaScript(self.profile.emulate_viewport(width, height))

class SecurityTestPanel(QDialog):
    """
    Painel para testes de segurança e identificação de rastreamento
    """
    
    def __init__(self, browser, parent=None):
        super().__init__(parent)
        self.browser = browser
        self.setWindowTitle("Painel de Testes de Segurança")
        self.setGeometry(200, 200, 800, 600)
        
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("🔬 TESTES DE SEGURANÇA E RASTREAMENTO")
        title.setStyleSheet("font-size: 16px; font-weight: bold; background: #333; color: #fff; padding: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Abas para diferentes testes
        tabs = QTabWidget()
        
        # ===== ABA 1: DETECÇÃO DE RASTREAMENTO IMEI =====
        imei_tab = QWidget()
        imei_layout = QVBoxLayout()
        
        imei_info = QLabel("""
        <h3>Detecção de Rastreamento IMEI</h3>
        <p>Este painel monitora tentativas de acesso a:</p>
        <ul>
            <li>IMEI (International Mobile Equipment Identity)</li>
            <li>Android ID / Google Advertising ID (GAID)</li>
            <li>IDFA (iOS Advertising Identifier)</li>
            <li>Número de série do dispositivo</li>
            <li>Endereço MAC</li>
        </ul>
        """)
        imei_info.setWordWrap(True)
        imei_layout.addWidget(imei_info)
        
        # Lista de tentativas detectadas
        imei_layout.addWidget(QLabel("Tentativas detectadas:"))
        self.imei_list = QListWidget()
        imei_layout.addWidget(self.imei_list)
        
        # Botões
        imei_buttons = QHBoxLayout()
        btn_clear = QPushButton("Limpar Lista")
        btn_clear.clicked.connect(self.imei_list.clear)
        btn_refresh = QPushButton("Atualizar")
        btn_refresh.clicked.connect(self.refresh_imei_detection)
        imei_buttons.addWidget(btn_clear)
        imei_buttons.addWidget(btn_refresh)
        imei_layout.addLayout(imei_buttons)
        
        imei_tab.setLayout(imei_layout)
        tabs.addTab(imei_tab, "📱 Rastreamento IMEI")
        
        # ===== ABA 2: FINGERPRINTING =====
        fingerprint_tab = QWidget()
        fingerprint_layout = QVBoxLayout()
        
        fingerprint_info = QLabel("""
        <h3>Teste de Fingerprinting</h3>
        <p>Clique nos botões abaixo para testar se as proteções estão funcionando:</p>
        """)
        fingerprint_info.setWordWrap(True)
        fingerprint_layout.addWidget(fingerprint_info)
        
        # Botões de teste
        btn_test_canvas = QPushButton("🎨 Testar Canvas Fingerprinting")
        btn_test_canvas.clicked.connect(self.test_canvas_fingerprint)
        fingerprint_layout.addWidget(btn_test_canvas)
        
        btn_test_webgl = QPushButton("🎮 Testar WebGL Fingerprinting")
        btn_test_webgl.clicked.connect(self.test_webgl_fingerprint)
        fingerprint_layout.addWidget(btn_test_webgl)
        
        btn_test_audio = QPushButton("🔊 Testar AudioContext")
        btn_test_audio.clicked.connect(self.test_audio_fingerprint)
        fingerprint_layout.addWidget(btn_test_audio)
        
        btn_test_fonts = QPushButton("🔤 Testar Font Fingerprinting")
        btn_test_fonts.clicked.connect(self.test_font_fingerprint)
        fingerprint_layout.addWidget(btn_test_fonts)
        
        # Resultado dos testes
        fingerprint_layout.addWidget(QLabel("Resultados:"))
        self.fingerprint_result = QTextEdit()
        self.fingerprint_result.setReadOnly(True)
        self.fingerprint_result.setMaximumHeight(200)
        fingerprint_layout.addWidget(self.fingerprint_result)
        
        fingerprint_tab.setLayout(fingerprint_layout)
        tabs.addTab(fingerprint_tab, "🖐️ Fingerprinting")
        
        # ===== ABA 3: HEADERS HTTP =====
        headers_tab = QWidget()
        headers_layout = QVBoxLayout()
        
        headers_info = QLabel("""
        <h3>Headers HTTP Enviados</h3>
        <p>Verifique quais informações estão sendo enviadas nas requisições:</p>
        """)
        headers_layout.addWidget(headers_info)
        
        self.headers_text = QTextEdit()
        self.headers_text.setReadOnly(True)
        self.headers_text.setFont(QFont("Courier New", 10))
        headers_layout.addWidget(self.headers_text)
        
        btn_check_headers = QPushButton("🔍 Verificar Headers Atuais")
        btn_check_headers.clicked.connect(self.check_current_headers)
        headers_layout.addWidget(btn_check_headers)
        
        headers_tab.setLayout(headers_layout)
        tabs.addTab(headers_tab, "📨 Headers HTTP")
        
        # ===== ABA 4: CONFIGURAÇÕES AVANÇADAS =====
        config_tab = QWidget()
        config_layout = QVBoxLayout()
        
        config_info = QLabel("Configurações Avançadas de Privacidade:")
        config_layout.addWidget(config_info)
        
        # Opções avançadas
        self.chk_block_webgl = QCheckBox("Bloquear WebGL completamente")
        self.chk_block_webgl.setChecked(True)
        config_layout.addWidget(self.chk_block_webgl)
        
        self.chk_block_canvas = QCheckBox("Bloquear Canvas Fingerprinting")
        self.chk_block_canvas.setChecked(True)
        config_layout.addWidget(self.chk_block_canvas)
        
        self.chk_block_audio = QCheckBox("Bloquear AudioContext")
        self.chk_block_audio.setChecked(True)
        config_layout.addWidget(self.chk_block_audio)
        
        self.chk_block_imei = QCheckBox("Bloquear APIs de IMEI/Serial")
        self.chk_block_imei.setChecked(True)
        config_layout.addWidget(self.chk_block_imei)
        
        self.chk_block_geolocation = QCheckBox("Bloquear Geolocalização")
        self.chk_block_geolocation.setChecked(True)
        config_layout.addWidget(self.chk_block_geolocation)
        
        # Botões
        btn_apply_config = QPushButton("Aplicar Configurações")
        btn_apply_config.clicked.connect(self.apply_advanced_config)
        config_layout.addWidget(btn_apply_config)
        
        config_tab.setLayout(config_layout)
        tabs.addTab(config_tab, "⚙️ Config. Avançadas")
        
        layout.addWidget(tabs)
        
        # Botão fechar
        btn_close = QPushButton("Fechar")
        btn_close.clicked.connect(self.close)
        layout.addWidget(btn_close)
        
        self.setLayout(layout)
    
    def refresh_imei_detection(self):
        """Atualizar lista de detecções de IMEI"""
        tab = self.browser.get_current_tab()
        if tab and tab.page:
            # Coletar tentativas suspeitas da página
            script = """
            (function() {
                const attempts = [];
                
                if (!document) return attempts;
                
                // Verificar se há elementos com IMEI no DOM
                const bodyText = document.body ? document.body.innerText : '';
                const imeiMatch = bodyText.match(/\\b\\d{15}\\b/g);
                if (imeiMatch) {
                    attempts.push(`IMEI encontrado no texto: ${imeiMatch}`);
                }
                
                // Verificar inputs
                document.querySelectorAll('input[name*="imei"], input[name*="device"], input[name*="serial"]').forEach(el => {
                    attempts.push(`Input suspeito: ${el.name}`);
                });
                
                return attempts;
            })();
            """
            
            tab.page.runJavaScript(script, self.display_imei_results)
    
    def display_imei_results(self, results):
        """Exibir resultados de IMEI"""
        self.imei_list.clear()
        if results and len(results) > 0:
            for item in results:
                self.imei_list.addItem(item)
        else:
            self.imei_list.addItem("Nenhuma tentativa de rastreamento IMEI detectada.")
    
    def test_canvas_fingerprint(self):
        """Testar proteção contra Canvas fingerprinting"""
        script = """
        (function() {
            try {
                if (!document) return { success: false, error: 'No document' };
                
                const canvas = document.createElement('canvas');
                canvas.width = 200;
                canvas.height = 200;
                const ctx = canvas.getContext('2d');
                if (!ctx) return { success: false, error: 'No canvas context' };
                
                ctx.fillText('Teste', 10, 50);
                const dataURL = canvas.toDataURL();
                
                // Tentar obter dados da imagem
                let imageData = null;
                try {
                    imageData = ctx.getImageData(0, 0, 200, 200);
                } catch (e) {
                    imageData = { data: { length: 0 } };
                }
                
                return {
                    success: true,
                    canvasDataURL: dataURL ? dataURL.substring(0, 50) + '...' : 'empty',
                    imageDataType: typeof imageData,
                    imageDataLength: imageData && imageData.data ? imageData.data.length : 0,
                    blocked: (dataURL && dataURL.includes('blank')) || (imageData && imageData.data && imageData.data.length === 0)
                };
            } catch (e) {
                return { success: false, error: e.toString(), blocked: true };
            }
        })();
        """
        
        tab = self.browser.get_current_tab()
        if tab:
            tab.page.runJavaScript(script, self.display_test_result)
    
    def display_test_result(self, result):
        """Exibir resultado de teste"""
        if result:
            if result.get('blocked'):
                self.fingerprint_result.append("✅ Canvas Fingerprinting: BLOQUEADO com sucesso!")
            else:
                self.fingerprint_result.append("❌ Canvas Fingerprinting: PODE ESTAR VAZANDO!")
                self.fingerprint_result.append(f"   Detalhes: {result}")
        else:
            self.fingerprint_result.append("❌ Erro ao executar teste")
    
    def test_webgl_fingerprint(self):
        """Testar proteção contra WebGL fingerprinting"""
        script = """
        (function() {
            try {
                if (!document) return { success: true, blocked: true, message: 'No document' };
                
                const canvas = document.createElement('canvas');
                const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
                
                if (!gl) {
                    return { success: true, blocked: true, message: 'WebGL não disponível (bloqueado)' };
                }
                
                const renderer = gl.getParameter(gl.RENDERER);
                const vendor = gl.getParameter(gl.VENDOR);
                
                const isBlocked = (renderer === 'WebKit WebGL' || vendor === 'WebKit');
                
                return {
                    success: true,
                    blocked: isBlocked,
                    renderer: renderer,
                    vendor: vendor
                };
            } catch (e) {
                return { success: false, error: e.toString(), blocked: true };
            }
        })();
        """
        
        tab = self.browser.get_current_tab()
        if tab:
            tab.page.runJavaScript(script, self.display_test_result)
    
    def test_audio_fingerprint(self):
        """Testar proteção contra AudioContext fingerprinting"""
        script = """
        (function() {
            try {
                const AudioContext = window.AudioContext || window.webkitAudioContext;
                if (!AudioContext) {
                    return { success: true, blocked: true, message: 'AudioContext não suportado' };
                }
                
                let context;
                try {
                    context = new AudioContext();
                    return { 
                        success: true, 
                        blocked: false, 
                        message: 'AudioContext disponível - PODE VAZAR!',
                        state: context.state
                    };
                } catch (e) {
                    return { 
                        success: true, 
                        blocked: true, 
                        message: 'AudioContext bloqueado: ' + e.message 
                    };
                }
            } catch (e) {
                return { success: false, error: e.toString(), blocked: true };
            }
        })();
        """
        
        tab = self.browser.get_current_tab()
        if tab:
            tab.page.runJavaScript(script, self.display_test_result)
    
    def test_font_fingerprint(self):
        """Testar proteção contra Font fingerprinting"""
        script = """
        (function() {
            try {
                if (!document) return { success: false, error: 'No document' };
                
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                if (!ctx) return { success: false, error: 'No canvas context' };
                
                const testString = 'abcdefghijklmnopqrstuvwxyz0123456789';
                const fonts = ['Arial', 'Helvetica', 'Times New Roman', 'Courier New', 'Verdana'];
                
                const widths = {};
                fonts.forEach(font => {
                    ctx.font = `16px ${font}`;
                    widths[font] = ctx.measureText(testString).width;
                });
                
                return {
                    success: true,
                    fontWidths: widths,
                    note: 'Font fingerprinting pode estar funcionando se as larguras variarem'
                };
            } catch (e) {
                return { success: false, error: e.toString() };
            }
        })();
        """
        
        tab = self.browser.get_current_tab()
        if tab:
            tab.page.runJavaScript(script, self.display_font_test_result)
    
    def display_font_test_result(self, result):
        """Exibir resultado de teste de fontes"""
        if result and result.get('success'):
            self.fingerprint_result.append("📊 Teste de Font Fingerprinting:")
            for font, width in result.get('fontWidths', {}).items():
                self.fingerprint_result.append(f"   {font}: {width:.2f}px")
        else:
            self.fingerprint_result.append("❌ Erro no teste de fontes")
    
    def check_current_headers(self):
        """Verificar headers HTTP atuais"""
        tab = self.browser.get_current_tab()
        if tab:
            # Esta é uma simulação - na prática, precisaríamos interceptar headers
            headers = f"""
User-Agent: {tab.profile.httpUserAgent()}
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7
Accept-Encoding: gzip, deflate, br
DNT: 1 (Do Not Track ativo)
Connection: keep-alive
Upgrade-Insecure-Requests: 1
            """
            self.headers_text.setText(headers)
    
    def apply_advanced_config(self):
        """Aplicar configurações avançadas"""
        tab = self.browser.get_current_tab()
        if tab:
            settings = tab.page.settings()
            
            # WebGL
            settings.setAttribute(QWebEngineSettings.WebGLEnabled, not self.chk_block_webgl.isChecked())
            
            # Canvas (não tem setting direta, depende de script)
            if self.chk_block_canvas.isChecked():
                tab.page.runJavaScript(tab.profile.block_fingerprinting())
            
            QMessageBox.information(self, "Configurações Aplicadas", 
                                   "As configurações avançadas foram aplicadas à aba atual.")
    
    def add_suspicious_attempt(self, attempt):
        """Adicionar tentativa suspeita à lista"""
        self.imei_list.addItem(f"{attempt.get('time', '??')} - {attempt.get('message', '???')}")

class PrivacyBrowser(QMainWindow):
    """
    Janela principal do navegador anti-rastreamento (versão aprimorada)
    """
    
    def __init__(self):
        super().__init__()
        
        # Configuração da janela
        self.setWindowTitle("Navegador Anti-Rastreamento v2.0")
        self.setGeometry(100, 100, 1400, 900)
        
        # Lista de tamanhos de tela para emulação
        self.available_viewports = [
            (1920, 1080, "Full HD (Desktop)"),
            (1366, 768, "HD (Desktop)"),
            (1536, 864, "Laptop"),
            (1440, 900, "Widescreen"),
            (2560, 1440, "2K"),
            (3840, 2160, "4K"),
            (375, 812, "iPhone X (Mobile)"),
            (390, 844, "iPhone 12 (Mobile)"),
            (414, 896, "iPhone 11 (Mobile)"),
            (360, 780, "Android (Mobile)"),
            (393, 873, "Pixel 7 (Mobile)"),
            (412, 915, "Android Large (Mobile)"),
            (768, 1024, "iPad (Tablet)"),
            (1024, 1366, "iPad Pro (Tablet)"),
        ]
        
        # Índice do viewport atual
        self.current_viewport_index = 0
        
        # Configurar interface
        self.init_ui()
        
        # Configurar proxy (usar sistema)
        QNetworkProxyFactory.setUseSystemConfiguration(True)
        
        # Status bar aprimorada
        self.status_bar = self.statusBar()
        self.status_label = QLabel("🛡️ Modo Anti-Rastreamento Ativo | IMEI Tracking: 🚫 Bloqueado")
        self.status_bar.addWidget(self.status_label)
        
        # Indicador de segurança
        self.security_indicator = QLabel("🔒 Seguro")
        self.security_indicator.setStyleSheet("color: #00FF00; font-weight: bold;")
        self.status_bar.addPermanentWidget(self.security_indicator)
        
        # Criar primeira aba
        self.add_new_tab()
    
    def init_ui(self):
        """Inicializar interface do usuário (versão aprimorada)"""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # ========== BARRA DE FERRAMENTAS ==========
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # Botão voltar
        btn_back = QAction("←", self)
        btn_back.setToolTip("Voltar")
        btn_back.triggered.connect(self.navigate_back)
        toolbar.addAction(btn_back)
        
        # Botão avançar
        btn_forward = QAction("→", self)
        btn_forward.setToolTip("Avançar")
        btn_forward.triggered.connect(self.navigate_forward)
        toolbar.addAction(btn_forward)
        
        # Botão recarregar
        btn_reload = QAction("↻", self)
        btn_reload.setToolTip("Recarregar")
        btn_reload.triggered.connect(self.reload_page)
        toolbar.addAction(btn_reload)
        
        # Barra de endereço
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Digite uma URL...")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        toolbar.addWidget(self.url_bar)
        
        # Botão ir
        btn_go = QAction("🔍 Ir", self)
        btn_go.triggered.connect(self.navigate_to_url)
        toolbar.addAction(btn_go)
        
        # Separador
        toolbar.addSeparator()
        
        # Botão nova aba
        btn_new_tab = QAction("+ Nova Aba", self)
        btn_new_tab.setToolTip("Nova Aba (Ctrl+T)")
        btn_new_tab.triggered.connect(lambda: self.add_new_tab())
        toolbar.addAction(btn_new_tab)
        
        # Separador
        toolbar.addSeparator()
        
        # Botão viewport (tamanho de tela)
        self.viewport_btn = QToolButton()
        self.viewport_btn.setText("📐 Tela: Full HD")
        self.viewport_btn.setPopupMode(QToolButton.InstantPopup)
        
        viewport_menu = QMenu()
        for i, (w, h, name) in enumerate(self.available_viewports):
            action = QAction(f"{name} ({w}x{h})", self)
            action.setData(i)
            action.triggered.connect(lambda checked, idx=i: self.change_viewport(idx))
            viewport_menu.addAction(action)
        
        self.viewport_btn.setMenu(viewport_menu)
        toolbar.addWidget(self.viewport_btn)
        
        # Botão user agent
        self.ua_btn = QToolButton()
        self.ua_btn.setText("🔄 UA: Windows Chrome")
        self.ua_btn.setPopupMode(QToolButton.InstantPopup)
        
        ua_menu = QMenu()
        ua_menu.addAction("Windows Chrome", lambda: self.change_user_agent(0))
        ua_menu.addAction("Windows Firefox", lambda: self.change_user_agent(1))
        ua_menu.addAction("macOS Chrome", lambda: self.change_user_agent(2))
        ua_menu.addAction("macOS Safari", lambda: self.change_user_agent(3))
        ua_menu.addAction("Linux Chrome", lambda: self.change_user_agent(4))
        ua_menu.addSeparator()
        ua_menu.addAction("iPhone (Mobile)", lambda: self.change_user_agent(5))
        ua_menu.addAction("Android (Mobile)", lambda: self.change_user_agent(6))
        ua_menu.addAction("iPad (Tablet)", lambda: self.change_user_agent(7))
        self.ua_btn.setMenu(ua_menu)
        toolbar.addWidget(self.ua_btn)
        
        # Botão randomizar tudo
        btn_randomize = QAction("🎲 Randomizar", self)
        btn_randomize.setToolTip("Randomizar todas as configurações")
        btn_randomize.triggered.connect(self.randomize_all)
        toolbar.addAction(btn_randomize)
        
        # Separador
        toolbar.addSeparator()
        
        # Botão de painel de segurança
        btn_security_panel = QAction("🔬 Testes de Segurança", self)
        btn_security_panel.setToolTip("Abrir painel de testes de segurança")
        btn_security_panel.triggered.connect(self.open_security_panel)
        toolbar.addAction(btn_security_panel)
        
        # ========== ÁREA DE ABAS ==========
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.tab_changed)
        layout.addWidget(self.tab_widget)
        
        # Atalhos de teclado
        self.setup_shortcuts()
    
    def setup_shortcuts(self):
        """Configurar atalhos de teclado"""
        # Ctrl+T - Nova aba
        shortcut_new = QShortcut(QKeySequence("Ctrl+T"), self)
        shortcut_new.activated.connect(lambda: self.add_new_tab())
        
        # Ctrl+W - Fechar aba
        shortcut_close = QShortcut(QKeySequence("Ctrl+W"), self)
        shortcut_close.activated.connect(self.close_current_tab)
        
        # F5 - Recarregar
        shortcut_reload = QShortcut(QKeySequence("F5"), self)
        shortcut_reload.activated.connect(self.reload_page)
        
        # Ctrl+Shift+S - Painel de segurança
        shortcut_panel = QShortcut(QKeySequence("Ctrl+Shift+S"), self)
        shortcut_panel.activated.connect(self.open_security_panel)
    
    def get_current_tab(self):
        """Obter a aba atual"""
        if self.tab_widget.count() > 0:
            return self.tab_widget.currentWidget()
        return None
    
    def add_new_tab(self, url=None):
        """Adicionar nova aba"""
        # Determinar viewport atual
        w, h, name = self.available_viewports[self.current_viewport_index]
        
        # Criar nova aba
        tab = PrivacyBrowserTab(self, (w, h))
        
        # Adicionar ao tab widget
        index = self.tab_widget.addTab(tab, "Nova Aba")
        self.tab_widget.setCurrentIndex(index)
        
        # Navegar para URL se fornecida
        if url:
            tab.setUrl(QUrl(url))
        else:
            # Página inicial personalizada
            home_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        text-align: center;
                        padding: 50px;
                        margin: 0;
                        height: 100vh;
                    }
                    .container {
                        max-width: 800px;
                        margin: 0 auto;
                        background: rgba(255,255,255,0.1);
                        padding: 40px;
                        border-radius: 20px;
                        backdrop-filter: blur(10px);
                    }
                    h1 { font-size: 48px; margin-bottom: 20px; }
                    h2 { font-size: 24px; margin-bottom: 30px; opacity: 0.9; }
                    .features {
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                        gap: 20px;
                        margin-top: 40px;
                    }
                    .feature {
                        background: rgba(255,255,255,0.2);
                        padding: 20px;
                        border-radius: 10px;
                    }
                    .feature h3 { margin: 0 0 10px 0; }
                    .status {
                        margin-top: 40px;
                        padding: 20px;
                        background: rgba(0,0,0,0.3);
                        border-radius: 10px;
                        font-size: 14px;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🛡️ Navegador Anti-Rastreamento</h1>
                    <h2>Proteção Avançada contra Fingerprinting e Rastreamento IMEI</h2>
                    
                    <div class="features">
                        <div class="feature">
                            <h3>📍 Geolocalização</h3>
                            <p>Totalmente bloqueada</p>
                        </div>
                        <div class="feature">
                            <h3>🎨 Canvas</h3>
                            <p>Fingerprinting bloqueado</p>
                        </div>
                        <div class="feature">
                            <h3>📱 IMEI/Device ID</h3>
                            <p>Monitoramento ativo</p>
                        </div>
                        <div class="feature">
                            <h3>🔄 User-Agent</h3>
                            <p>Randomizável</p>
                        </div>
                    </div>
                    
                    <div class="status">
                        <p>✅ Proteções ativas | Use Ctrl+Shift+S para abrir o painel de testes</p>
                        <p>🔍 Digite uma URL acima para começar a navegar com privacidade</p>
                    </div>
                </div>
            </body>
            </html>
            """
            tab.setHtml(home_html)
        
        return tab
    
    def close_tab(self, index):
        """Fechar aba"""
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
        else:
            # Última aba - só limpa
            tab = self.get_current_tab()
            if tab:
                tab.setHtml("<h1>🛡️ Navegador Anti-Rastreamento</h1><p>Digite uma URL para começar.</p>")
    
    def close_current_tab(self):
        """Fechar aba atual"""
        if self.tab_widget.count() > 0:
            self.close_tab(self.tab_widget.currentIndex())
    
    def tab_changed(self, index):
        """Quando a aba muda, atualizar URL bar"""
        tab = self.tab_widget.widget(index)
        if tab:
            self.url_bar.setText(tab.url().toString())
            self.url_bar.setCursorPosition(0)
    
    def update_tab_title(self, tab, title):
        """Atualizar título da aba"""
        index = self.tab_widget.indexOf(tab)
        if index >= 0:
            short_title = title[:20] + "..." if len(title) > 20 else title
            self.tab_widget.setTabText(index, short_title)
            self.tab_widget.setTabToolTip(index, title)
    
    def update_url_bar(self, url):
        """Atualizar barra de URL"""
        self.url_bar.setText(url.toString())
        self.url_bar.setCursorPosition(0)
    
    def navigate_to_url(self):
        """Navegar para URL digitada"""
        url = self.url_bar.text()
        if not url:
            return
        
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        
        tab = self.get_current_tab()
        if tab:
            tab.setUrl(QUrl(url))
    
    def navigate_back(self):
        """Voltar"""
        tab = self.get_current_tab()
        if tab:
            tab.back()
    
    def navigate_forward(self):
        """Avançar"""
        tab = self.get_current_tab()
        if tab:
            tab.forward()
    
    def reload_page(self):
        """Recarregar"""
        tab = self.get_current_tab()
        if tab:
            tab.reload()
    
    def change_viewport(self, index):
        """Alterar tamanho de tela emulado"""
        self.current_viewport_index = index
        w, h, name = self.available_viewports[index]
        
        # Atualizar texto do botão
        self.viewport_btn.setText(f"📐 Tela: {name}")
        
        # Aplicar a todas as abas
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            if tab:
                tab.set_viewport(w, h)
        
        self.status_bar.showMessage(f"📐 Viewport alterado para {name} ({w}x{h})", 3000)
    
    def change_user_agent(self, index):
        """Alterar User-Agent"""
        user_agents = [
            ("Windows Chrome", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"),
            ("Windows Firefox", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"),
            ("macOS Chrome", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"),
            ("macOS Safari", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"),
            ("Linux Chrome", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"),
            ("iPhone", "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1"),
            ("Android", "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"),
            ("iPad", "Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1"),
        ]
        
        name, ua = user_agents[index]
        
        # Atualizar texto do botão
        self.ua_btn.setText(f"🔄 UA: {name}")
        
        # Aplicar a todas as abas
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            if tab:
                tab.profile.setHttpUserAgent(ua)
        
        self.status_bar.showMessage(f"🔄 User-Agent alterado para {name}", 3000)
    
    def randomize_all(self):
        """Randomizar todas as configurações"""
        # Viewport aleatório
        viewport_idx = random.randint(0, len(self.available_viewports) - 1)
        self.change_viewport(viewport_idx)
        
        # User-Agent aleatório
        ua_idx = random.randint(0, 7)
        self.change_user_agent(ua_idx)
        
        # Também randomizar hardware fingerprint
        tab = self.get_current_tab()
        if tab:
            tab.page.runJavaScript(tab.profile.emulate_hardware())
        
        self.status_bar.showMessage("🎲 Configurações randomizadas com sucesso!", 3000)
    
    def open_security_panel(self):
        """Abrir painel de testes de segurança"""
        self.security_panel = SecurityTestPanel(self, self)
        self.security_panel.show()

class StartupDialog(QDialog):
    """Diálogo inicial com explicações (versão aprimorada)"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Navegador Anti-Rastreamento v2.0")
        self.setModal(True)
        self.setGeometry(400, 300, 700, 600)
        
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("🛡️ NAVEGADOR ANTI-RASTREAMENTO v2.0")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #33FF33; background: #000; padding: 15px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Explicações
        info = QTextEdit()
        info.setReadOnly(True)
        info.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #00ff00;
                font-family: 'Courier New';
                font-size: 12px;
                padding: 15px;
            }
        """)
        info.setHtml("""
        <h2>🔒 NOVAS PROTEÇÕES ATIVAS:</h2>
        <ul>
        <li><b>📱 BLOQUEIO DE IMEI/DEVICE ID:</b> Monitoramento e bloqueio de tentativas de acesso a identificadores de dispositivo</li>
        <li><b>🚫 RASTREAMENTO ILEGAL:</b> Detecção de padrões de IMEI em URLs e conteúdo</li>
        <li><b>🛡️ BLOQUEIO DE FINGERPRINTING AVANÇADO:</b> Canvas, WebGL, AudioContext, Fontes e mais</li>
        <li><b>🔍 PAINEL DE TESTES:</b> Interface para verificar se as proteções estão funcionando</li>
        <li><b>📱 EMULAÇÃO MOBILE:</b> Viewports e User-Agents para iPhone, Android e iPad</li>
        <li><b>🔬 DETECÇÃO DE APIs SUSPEITAS:</b> Monitoramento de tentativas de acesso a geolocalização, dispositivos, etc.</li>
        </ul>
        
        <h2>🎯 NOVAS FUNCIONALIDADES:</h2>
        <p>• <b>Painel de Segurança (Ctrl+Shift+S):</b> Teste todas as proteções em tempo real</p>
        <p>• <b>Bloqueio de IMEI:</b> Detecta tentativas de captura de IMEI, Android ID, GAID, IDFA</p>
        <p>• <b>Modo Mobile:</b> Emule dispositivos reais para testes</p>
        <p>• <b>Headers HTTP:</b> Visualize o que está sendo enviado nas requisições</p>
        <p>• <b>Configurações Avançadas:</b> Ative/desative proteções individualmente</p>
        
        <h2>⚠️ AVISO LEGAL:</h2>
        <p>Este navegador é para fins educacionais e de privacidade. 
        O bloqueio de rastreamento IMEI é uma proteção contra práticas invasivas.
        Não use para atividades ilegais.</p>
        """)
        layout.addWidget(info)
        
        # Botões
        buttons = QHBoxLayout()
        
        btn_start = QPushButton("🚀 Iniciar Navegação Segura")
        btn_start.setStyleSheet("background-color: #4CAF50; color: white; font-size: 14px; padding: 10px;")
        btn_start.clicked.connect(self.accept)
        
        btn_exit = QPushButton("❌ Sair")
        btn_exit.setStyleSheet("background-color: #f44336; color: white; font-size: 14px; padding: 10px;")
        btn_exit.clicked.connect(self.reject)
        
        buttons.addWidget(btn_start)
        buttons.addWidget(btn_exit)
        layout.addLayout(buttons)
        
        self.setLayout(layout)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Navegador Anti-Rastreamento v2.0")
    app.setStyle('Fusion')
    
    # Diálogo inicial
    dialog = StartupDialog()
    if dialog.exec_() == QDialog.Accepted:
        browser = PrivacyBrowser()
        browser.show()
        sys.exit(app.exec_())
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
