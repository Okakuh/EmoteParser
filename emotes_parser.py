from os import getcwd, listdir, path, walk, renames
from shutil import rmtree, make_archive, copytree
from json import load
from zipfile import ZipFile, is_zipfile
from PIL import Image
import json
import os
from typing import Any, Dict, Optional
from pathlib import Path
from time import sleep



this_folder = getcwd()
exe_config_folder_name = "EmotesParserConfig"
exe_config_name = "config.json"

config_dir = f"{this_folder}/{exe_config_folder_name}"
config_file = f"{config_dir}/{exe_config_name}"

unziped_part = "_unziped"
modified_part = "modified_"

class Config:
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self._default_config: Dict[str, Any] = {
            "get_emotes_data_from": "default.json",
            "emotes_dir": "assets/myemotes/textures/font/emotes",
            "how_to_define_if_emote": "myemotes",
            "tab_width": 10,
            "wide_width_to_height": 1.6,
            "group_prefixes": ["pwgood", "peepo", "pepe", "forsen", "feels"],
            "non_grouped_emotes_group_name": "other",
            "wide_emotes_group_name": "wide",
            "symbol_chat_exemple_dir": "symbol-chat.exemple",
            "where_to_save_symbol_chat_exemple": "assets",
            "result_name": "peepo",
            "archive_if_was_not?": False
            }

    
    def load_config(self) -> bool:
        """
        Загрузить конфигурацию из файла.
        Возвращает True если файл существует и загружен, False в противном случае.
        """
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
                return True
            return False
        except (json.JSONDecodeError, IOError) as e:
            print(f"Ошибка загрузки конфигурации: {e}")
            return False
    
    def save_config(self) -> bool:
        """
        Сохранить текущую конфигурацию в файл.
        Возвращает True при успешном сохранении.
        """
        try:
            # Создаем директорию если не существует
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=4, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Ошибка сохранения конфигурации: {e}")
            return False
    
    def create_default_config(self) -> bool:
        """Создать конфигурационный файл с настройками по умолчанию"""
        if self._default_config:
            self._config = self._default_config.copy()
            return self.save_config()
        return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Получить значение по ключу"""
        return self._config.get(key, default)
        """Установить значение по ключу"""
        self._config[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """Получить всю конфигурацию"""
        return self._config.copy()
    
    def reset_to_default(self) -> None:
        """Сбросить конфигурацию к значениям по умолчанию"""
        self._config = self._default_config.copy()
    
    def exists(self) -> bool:
        """Проверить существует ли конфигурационный файл"""
        return self.config_path.exists()
    

class Emote():
    def __init__(self, emote_name: str, emote_char: str, path_to_image: str):
        self.name = emote_name
        self.char = emote_char
        self.path_to_image = path_to_image
        self.width, self.height = Image.open(self.path_to_image).size
        

def get_emotes(emotes):
    result = {}
    for emote in emotes["providers"]:
        if "myemotes" in emote["file"]:
            emote_name = emote["file"].split("/")[-1].split(".")[0]
            emote_char = emote["chars"][0]
            result[emote_name] = emote_char

    return result


def get_pack(folder: str) -> Path:
    for file in listdir(folder):
        if file != Path(__file__).name and \
            file != exe_config_folder_name:
                if path.isdir(f"{folder}/{file}") or is_zipfile(f"{folder}/{file}"):
                    return f"{folder}/{file}"
    return None


def get_path_to_char_data_file(folder: str, file_to_get_from: str) -> Optional[Path]:
    for root, _, files in walk(folder):
        for file in files:
            if file == file_to_get_from:
                return path.join(root, file)
    return None


def get_emotes_from(folder: str, file_to_get_from: str, how_to_define_if_emote: str, emotes_dir: str) -> Optional[list[Emote]]:
    emotes = []
    char_data_file = get_path_to_char_data_file(folder, file_to_get_from)
    if not char_data_file:
        return None
    
    with open(char_data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for char_dict in data.get("providers"):
        file = char_dict.get("file")
        if how_to_define_if_emote in file:
            char = char_dict.get("chars")[0]
            emote_image_file = file.split("/")[-1]
            emote_name = emote_image_file.split(".")[0]
            emotes.append(Emote(emote_name, char, f"{folder}/{emotes_dir}/{emote_image_file}"))
    return emotes

def main():
    if not path.exists(config_dir):
        print("Config directory not found.")
        return

    path_to_original_pack = get_pack(this_folder)
    path_to_unziped_pack = None
    path_to_use_pack = path_to_original_pack
    
    if path_to_original_pack is None:
        print("No resource pack found in the current directory.")
        return

    if_zip = is_zipfile(path_to_original_pack)
    if if_zip:
        path_to_unziped_pack = f"{this_folder}/{Path(path_to_original_pack).stem}{unziped_part}"
        ZipFile(path_to_original_pack).extractall(path_to_unziped_pack)
        path_to_use_pack = path_to_unziped_pack
    
    config = Config(config_file)
    if not config.exists():
        config.create_default_config()
        print("Default config created")

    if not config.load_config():
        print("Failed to load config.")
        return
    
    get_emotes_data_from = config.get("get_emotes_data_from")
    how_to_define_if_emote = config.get("how_to_define_if_emote")
    emotes_dir = config.get("emotes_dir")
    tab_width = config.get("tab_width")
    wide_width_to_height = config.get("wide_width_to_height")
    group_prefixes = config.get("group_prefixes")
    non_grouped_emotes_group_name = config.get("non_grouped_emotes_group_name")
    wide_emotes_group_name = config.get("wide_emotes_group_name")
    where_to_save_symbol_chat_exemple = config.get("where_to_save_symbol_chat_exemple")
    result_name = config.get("result_name")
    archive_if_was_not = config.get("archive_if_was_not?")
    symbol_chat_exemple = config.get("symbol_chat_exemple_dir")
    
    result = ''
    
    print("Parsing emotes...")
    
    found_emotes = get_emotes_from(path_to_use_pack, get_emotes_data_from, how_to_define_if_emote, emotes_dir)
    if not found_emotes:
        print("No emotes found in the pack.")
        return

    wide_emotes = []
    
    print("Looking for wide emotes...")

    for emote in list(found_emotes):
        emote: Emote = emote
        if emote.width >= emote.height * wide_width_to_height:
            wide_emotes.append(emote)
            found_emotes.remove(emote)
    
    print(f"Found {len(wide_emotes)} wide emotes.")
    print()
    print("Grouping emotes...")
    grouped_emotes = {}

    for group_prefix in group_prefixes:
        for emote in list(found_emotes):
            emote: Emote = emote
            if emote.name.startswith(group_prefix):
                if group_prefix not in grouped_emotes:
                    grouped_emotes[group_prefix] = []
                grouped_emotes[group_prefix].append(emote)
                found_emotes.remove(emote)
    print("Done.")
    print()
    print("Adding emotes to result...")
    print("Adding grouped emotes...")

    for group in grouped_emotes:
        result += group
        if len(result) % tab_width != 0:
            result += " " * (tab_width - len(group))
        
        for emote in grouped_emotes[group]:
            result += emote.char
        if len(result) % tab_width != 0:
            result += " " * (tab_width - (len(result) % tab_width))
    print("Done.")
    print("Adding non-grouped emotes...")
    
    result += non_grouped_emotes_group_name
    if len(non_grouped_emotes_group_name) % tab_width != 0:
        result += " " * (tab_width - len(non_grouped_emotes_group_name))
    
    for emote in found_emotes:
        result += emote.char
    
    if len(result) % tab_width != 0:
        result += " " * (tab_width - (len(result) % tab_width))
    print("Done.")
    print("Adding wide emotes...")

    result += wide_emotes_group_name
    if len(wide_emotes_group_name) % tab_width != 0:
        result += " " * (tab_width - len(wide_emotes_group_name))
    
    for emote in wide_emotes:
        if len(result) % tab_width != 0:
            if (tab_width - (len(result) % tab_width)) < 3:
                result += " " * (tab_width - (len(result) % tab_width))
        result += f" {emote.char} "

    print("Done.")
    print("Copying exemple symbol chat...")

    where_to_save_symbol_chat_exemple_modify = f"{path_to_use_pack}/{where_to_save_symbol_chat_exemple}/{symbol_chat_exemple.replace('.exemple', '')}"
    
    copytree(f"{config_dir}/{symbol_chat_exemple}", where_to_save_symbol_chat_exemple_modify, dirs_exist_ok=True)
    
    print("Done.")
    print("Looking for result.txt...")

    result_txt = ""
    for root, _, files in walk(where_to_save_symbol_chat_exemple_modify):
        for file in files:
            if file == "result.txt":
                result_txt = path.join(root, file)

    if result_txt == "":
        print("result.txt not found.")
        return
    
    print("Writing result to result.txt...")

    with open(result_txt, 'w', encoding='utf-8') as f:
        f.write(result)
    
    print("Done.")
    print("Finalizing...")

    result_rename_to = f"{Path(result_txt).parent}/{result_name}.txt"
    if path.exists(result_rename_to):
        os.remove(result_rename_to)
    
    renames(result_txt, result_rename_to)

    modified_path = rf"{Path(path_to_use_pack).parent}/{modified_part}{Path(path_to_use_pack).name.replace(unziped_part, '')}"
    
    renames(path_to_use_pack, modified_path)
    
    print("Modified pack created.")
    print("Was arcived:", if_zip)
    print("If was not arcived convert to archive?:", archive_if_was_not)
    
    if if_zip or archive_if_was_not:
        print("Creating archive...")
        make_archive(modified_path, 'zip', modified_path)
        print("Archive created.")
        print("Cleaning up...")
        rmtree(modified_path)
        print("Done.")
    
    print("Emotes parsing completed successfully.")

if __name__ == "__main__":
    main()
    sleep(15)
    print("WIndow will close in 15 seconds...")