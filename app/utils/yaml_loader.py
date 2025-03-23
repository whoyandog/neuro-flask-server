import os
import yaml
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class PromptLoader:
    def __init__(self, prompts_dir='prompts'):
        self.prompts_dir = prompts_dir
        self.prompts = {}
        self.last_loaded = {}
        self.load_all_prompts()
        self._setup_file_watcher()
    
    def load_all_prompts(self):
        """Загружает все промпты из директорий"""
        for model_name in os.listdir(self.prompts_dir):
            model_dir = os.path.join(self.prompts_dir, model_name)
            if os.path.isdir(model_dir):
                self.prompts[model_name] = {}
                for prompt_file in os.listdir(model_dir):
                    if prompt_file.endswith('.yaml') or prompt_file.endswith('.yml'):
                        prompt_path = os.path.join(model_dir, prompt_file)
                        prompt_name = os.path.splitext(prompt_file)[0]
                        self.load_prompt(model_name, prompt_name, prompt_path)
    
    def load_prompt(self, model_name, prompt_name, file_path):
        """Загружает отдельный промпт из YAML-файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                prompt_data = yaml.safe_load(f)
                self.prompts.setdefault(model_name, {})[prompt_name] = prompt_data
                self.last_loaded[file_path] = os.path.getmtime(file_path)
                print(f"Загружен промпт: {model_name}/{prompt_name}")
                print(prompt_data)
                return prompt_data
        except Exception as e:
            print(f"Ошибка при загрузке промпта {file_path}: {str(e)}")
            return None
    
    def get_prompt(self, model_name, prompt_name):
        """Получает промпт по имени модели и промпта"""
        if model_name in self.prompts and prompt_name in self.prompts[model_name]:
            return self.prompts[model_name][prompt_name]
        return None
    
    def _setup_file_watcher(self):
        """Настраивает отслеживание изменений в файлах промптов"""
        event_handler = PromptFileHandler(self)
        self.observer = Observer()
        self.observer.schedule(event_handler, self.prompts_dir, recursive=True)
        self.observer.start()
    
    def stop_watching(self):
        """Останавливает отслеживание файлов"""
        if hasattr(self, 'observer'):
            self.observer.stop()
            self.observer.join()

class PromptFileHandler(FileSystemEventHandler):
    def __init__(self, prompt_loader):
        self.prompt_loader = prompt_loader
        self.loading = False  
        super().__init__()
    
    def on_modified(self, event):
        if not event.is_directory and (event.src_path.endswith('.yaml') or event.src_path.endswith('.yml')):
            if self.loading:    
                return
            
            self.loading = True 
            try:
                rel_path = os.path.relpath(event.src_path, self.prompt_loader.prompts_dir)
                parts = os.path.normpath(rel_path).split(os.sep)
                
                if len(parts) >= 2:
                    model_name = parts[0]
                    prompt_name = os.path.splitext(parts[1])[0]
                    
                    current_mtime = os.path.getmtime(event.src_path)
                    if event.src_path not in self.prompt_loader.last_loaded or current_mtime > self.prompt_loader.last_loaded[event.src_path]:
                        print(f"Обновление промпта: {model_name}/{prompt_name}")
                        self.prompt_loader.load_prompt(model_name, prompt_name, event.src_path)
            finally:
                self.loading = False  

prompt_loader = None

def init_prompt_loader(prompts_dir='prompts'):
    """Инициализирует глобальный загрузчик промптов"""
    global prompt_loader
    prompt_loader = PromptLoader(prompts_dir)
    return prompt_loader

def get_prompt_loader():
    """Возвращает глобальный загрузчик промптов"""
    global prompt_loader
    if prompt_loader is None:
        prompt_loader = init_prompt_loader()
    return prompt_loader 