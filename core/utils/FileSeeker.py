from pathlib import Path
import os
import threading
import time
from .paintext import *
from sys import exit
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from random import choice

class FileSeeker() :
    def __init__(self, path: Path, is_thread: bool = True, title = '', multipath: bool = False):        
        if not os.path.exists(path) :
            print(f"[{BOLD}{RED}!{RESET}] Path does NOT exists")
            exit()
        self.is_thread = is_thread
        self.result = None if not multipath else list()
        self.lock = threading.RLock()
        self.should_stop = False
        self.feedback_thread = threading.Thread(target=self.update_render)
        self.path = path
        self.__listdir = sorted(os.listdir(self.path))
        self.esc_quote = ""
        self.start = 0
        self.limit = self.start + 10
        self.selection = -1
        self.feedback = ""
        self.__title = title
        self.positive_list = [
    f"{YELLOW}You {GREEN}matter{RESET} today", 
    f"{YELLOW}Sun{RESET} will rise soon",
    f"{CYAN}Coffee{RESET} is {MAGENTA}magic{RESET}",
    f"Dogs {RED}love{RESET} you",
    f"{CYAN}Water {GREEN}heals{RESET} stress",
    f"You are {YELLOW}enough{RESET}",
    f"{GREEN}Kindness{RESET} spreads",
    f"{YELLOW}Stars{RESET} still shine",
    f"{CYAN}Breathe{RESET} in {BLUE}peace{RESET}",
    f"Laughing is {YELLOW}free{RESET}",
    f"{RED}Music{RESET} lifts {MAGENTA}souls{RESET}",
    f"{GREEN}Hugs{RESET} feels {YELLOW}warm{RESET}",
    f"{BLUE}Sleep{RESET} fixes {GREEN}mood{RESET}",
    f"Growth takes {CYAN}time{RESET}",
    f"Smile is {RED}power{RESET}",
    f"{GREEN}You're still here{RESET}",
    f"{BLUE}Birds{RESET} still {YELLOW}sing{RESET}"]

    def update_render(self):
        while True:
            if self.should_stop:
                break;
            self.feedback = choice(self.positive_list)
            self.folder_render()
            time.sleep(10)

    def folder_render(self) :
        self.lock.acquire()
        try:

            os.system("cls" if os.name == "nt" else "clear")
            try :
                print(f"{GREEN}[SEL]{RESET} {self.listdir[self.selection]}")
                print(f"{YELLOW}INDEX :{RESET} {self.selection}")
            except IndexError :
                print(f"{GREEN}[SEL]{RESET} ")
            self.listdir = sorted(os.listdir(self.path))

            if self.selection < 0 : self.selection = 0
            elif self.selection > len(self.listdir) : self.selection = len(self.listdir)
            name = ""
            print(f"{RED}[TITLE] :{RESET} {self.__title}")
            print(f"{YELLOW}[DIR]{RESET} : {str(self.path)}\n{'='*28}")
            if len(self.listdir) <= 10 :
                for i in range(0, len(self.listdir)) :
                    if i == self.selection : 
                        name += "▶"
                    else : name += "  |"
                    name += self.listdir[i]
                    if os.path.isdir(self.path / self.listdir[i]) :
                        name += "/"
                    print(name)
                    name = ""
            else : 

                if self.selection > self.limit : 
                    self.start += self.selection - self.limit
                elif self.selection < self.start : self.start = self.selection
                if self.start < 0 : 
                    self.start = 0
                    self.selection = 0
                self.limit = self.start + 10

                for i in range(self.start, self.limit) :
                    try :
                        if i == self.selection : name += "▶"
                        else : name += "  |"
                        name += self.listdir[i]
                        if os.path.isdir(self.path / self.listdir[i]) : name += "/"
                        print(name)
                        name = ""
                    except IndexError :
                        break
            print(f"{'='*28}\nfeedback : {self.feedback}\n{'='*28}")
        finally:
            self.lock.release()            
    
    def main(self) -> Path|list[Path]|None :
        kb = KeyBindings()
        @kb.add("up")
        def upinput(event) :
            self.selection -= 1
            self.folder_render()


        @kb.add("down")
        def downinput(event) :
            self.selection += 1
            self.folder_render()

        @kb.add("left")
        def leftarr(event) :
            try :
                old_path = self.path
                self.path = self.path.parent
                self.folder_render()
            except PermissionError :
                os.system("cls" if os.name == "nt" else "clear")
                self.path = old_path
                self.feedback = "Permission Denied"
                self.folder_render()

        @kb.add("right")
        def rightarr(event) :
            path = self.path / self.listdir[self.selection]
            if os.path.isdir(path) :
                if os.access(path, os.X_OK) and os.access(path, os.R_OK) :
                    self.path = path
                else :
                    self.feedback = "Permission denied :("
            else :
                self.feedback = "Can't change dir to a file !"
            self.folder_render()
        
        @kb.add("q")
        def exit(event) :
            self.esc_quote = "Exiting... (this might take a while)"
            event.app.exit()

        if not isinstance(self.result, list):
            @kb.add("enter")
            def choose_file(event) :
                path = self.path / self.listdir[self.selection]
                if self.listdir :
                    if os.path.isfile(path) :
                        if os.access(path, os.W_OK) :
                            if os.access(path, os.R_OK) :
                                self.result = path
                                self.esc_quote = "Operation successful quiting"
                                event.app.exit()
                            else :
                                self.feedback = "File is not readable !"
                        else :
                            self.feedback = "File was not movable"
                    else :
                        self.feedback = "Can't select a folder !"
                else: 
                    self.feedback = "Folder is empty"
                self.folder_render()
        else :
            @kb.add("space")
            def choose_file(event) :
                path = self.path / self.listdir[self.selection]
                if self.listdir :
                    if os.path.isfile(path) :
                        if os.access(path, os.W_OK) :
                            if os.access(path, os.R_OK) :
                                if path not in self.result :
                                    self.result.append(path)
                                    self.feedback = f"File {path.name} was added"
                                else :
                                    self.feedback = "file is already picked !"
                            else :
                                self.feedback = "File is not readable !"
                        else :
                            self.feedback = "File was not movable"
                    else :
                        self.feedback = "Can't select a folder !"
                else: 
                    self.feedback = "Folder is empty"
                self.folder_render()
        if self.is_thread :
            self.feedback_thread.start()
        else :
            self.folder_render()
        try:
            app = PromptSession(key_bindings=kb)
            text = app.prompt("> ")
        finally:
            self.should_stop = True
            print(self.esc_quote)
            for i in range(11) :
                print(f"Exiting in {11-i} seconds")
                time.sleep(1)
            return self.result

