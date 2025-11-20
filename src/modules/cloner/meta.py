from bs4 import BeautifulSoup
import os

def inject_viewport(output_dir, print_success_func, print_error_func):
    for root, _, files in os.walk(output_dir):
        for file in files:
            if file.lower().endswith(('.html', '.htm')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r+', encoding='utf-8') as f:
                        content = f.read()
                        soup = BeautifulSoup(content, 'html.parser')
                        
                        viewport = soup.find('meta', attrs={'name': 'viewport'})
                        
                        if not viewport:
                            viewport = soup.new_tag('meta')
                            viewport.attrs['name'] = 'viewport'
                            viewport.attrs['content'] = 'width=device-width, initial-scale=1.0'
                            
                            head = soup.head
                            if not head:
                                head = soup.new_tag('head')
                                if soup.html:
                                    soup.html.insert(0, head)
                                else:
                                    soup.insert(0, head)
                        
                            head.insert(0, viewport)
                            
                            f.seek(0)
                            f.write(str(soup))
                            f.truncate()
                            
                            print_success_func(f"Added viewport meta to: {file_path}")
                except Exception as e:
                    print_error_func(f"Failed to inject viewport in {file_path}: {str(e)}")
