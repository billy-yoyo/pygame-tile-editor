import pygame, math

class TileSizer:
    def __init__(self, tile_width, tile_height):
        self.tile_width = tile_width
        self.tile_height = tile_height

#class for loading and storing images. 
class ImageManager:
    def __init__(self, tilemap = None, iconsize = None): #tilemap anything with variables tile_width and tile_height
        self.tilemap = tilemap
        self.images = {}
        self.iconsize = iconsize

        self.icons = []
        self.id_icons = {}
        self.icon_names = []

    def getIcon(self, index):
        if index < self.iconAmount() and index >= 0:
            return self.icons[index]
        return None

    def iconAmount(self):
        return len(self.icons)

    def iconIdAmount(self, name):
        if name != None:
            return len(self.id_icons[name])
        return 0

    def getIdIcon(self, name, index):
        if name != None and index >= 0 and index < self.iconIdAmount(name):
            return self.id_icons[name][index]
        return None

    def createIcon(self, name):
        if self.iconsize != None:
            image = self.images[name][0]
            image = pygame.transform.scale(image, self.iconsize)
            self.icons.append(image)
            self.icon_names.append(name)

            length = len(self.images[name])
            idicons = []
            for i in range(length):
                idicons.append(pygame.transform.scale(self.images[name][i], self.iconsize))
            self.id_icons[name] = idicons

    def loadImage(self, image, name):
        if self.tilemap != None and not self.checkScale(image):
            image = pygame.transform.scale(image, (self.tilemap.tile_width, self.tilemap.tile_height))
        self.images[name] = [image]
        self.createIcon(name)

    def loadTiles(self, image, columns, rows, name):
        tile_width = math.floor(image.get_width()/columns)
        tile_height = math.floor(image.get_height()/rows)
        need_to_scale = True
        if  self.tilemap == None or (tile_width == self.tilemap.tile_width and tile_height == self.tilemap.tile_height):
            need_to_scale = False
        images = [None] * (columns*rows)
        for y in range(rows):
            id_offset = y*columns
            for x in range(columns):
                img = pygame.Surface((tile_width, tile_height))
                img.blit(image, [0,0], [x*tile_width, y*tile_height, tile_width, tile_height])
                if need_to_scale:
                    img = pygame.transform.scale(img, (self.tilemap.tile_width, self.tilemap.tile_height))
                images[id_offset+x] = img
        self.images[name] = images
        self.createIcon(name)

    def loadResourceFile(self, name):
        f = open(fixName(name))
        line = f.readLine()
        while line != '':
            if line != "\n" and line[0] != "#":
                data = line.split(":")
                image = pygame.image.load(data[1])
                if len(data) == 2:
                    self.loadImage(image, data[0])
                elif len(data) == 4:
                    columns, rows = int(data[2]), int(data(3))
                    if columns == 1 and rows == 1:
                        self.loadImage(image, data[0])
                    else:
                        self.loadTiles(image, columns, rows, data[0])
                else:
                    print(" INVALID LINE FOUND IN " + name)
                line = f.readLine()

    def checkScale(self, image):
        if self.tilemap == None:
            return True
        elif image.get_width() != self.tilemap.tile_width or image.get_height() != self.tilemap.tile_height:
            return False
        return True

    def getImage(self, name, imgid = 0):
        if name != None and imgid != None:
            img = self.images[name][imgid]
            if self.tilemap != None and not self.checkScale(img):
                img = pygame.transform.scale(img, (self.tilemap.tile_width, self.tilemap.tile_height))
                self.images[name][imgid] = img
            return img

    def getTileImage(self, tile):
        return self.getImage(tile.info["img_name"], tile.info["img_id"])

#helpful cooldowns class;
# note that after inputing the cooldown name you can not pass a name argument for the functions as long as you want to interact with the same cooldown
class Cooldowns:
    def __init__(self):
        self.cooldowns = {}
        self.last_used = ""

    def create(self, name, length):
        self.last_used = name
        self.cooldowns[name] = [length, -1]
        return self

    def start(self, name = None):
        if name == None:
            name = self.last_used
        else:
            self.last_used = name
        
        self.cooldowns[name][1] = pygame.time.get_ticks()
        return self

    def stop(self, name = None):
        if name == None:
            name = self.last_used
        else:
            self.last_used = name
        
        self.cooldowns[name][1] = -1
        return self

    def check(self, name = None):
        if name == None:
            name = self.last_used
        else:
            self.last_used = name
            
        cd = self.cooldowns[name]
        if cd[1] > 0 and pygame.time.get_ticks() - cd[1] >= cd[0]:
            return True
        return False

    def elapsed(self, name = None):
        if name == None:
            name = self.last_used
        else:
            self.last_used = name

        return pygame.time.get_ticks() - self.cooldowns[name][1]

#does nothing as a base class, inherit this class and override the functions to interact with a button.
class ButtonEvent:
    
    def left_click(self, button, event, down):
        return

    def right_click(self, button, event, down):
        return

    def mouse_move(self, button, event):
        return

    def scroll_up(self, button, event, down):
        return

    def scroll_down(self, button, event, down):
        return

    def scroll_click(self, button, event, down):
        return

    def key_press(self, button, event, down):
        return

    def update(self, button):
        return

    def draw(self, button, screen):
        return

#main button class, don't need to override, calls buttonevent every time something happens.
class Button:
    def __init__(self, dims, buttonevent, name, desc = ""):
        self.x = dims[0]
        self.y = dims[1]
        self.width = dims[2]
        self.height = dims[3]
        self.buttonevent = buttonevent
        self.name = name
        self.desc = desc

        self.popup_timer = -1
        self.popup = False

    def dims(self):
        return [self.x, self.y, self.width, self.height]

    def pos(self):
        return [self.x, self.y]

    def size(self):
        return [self.width, self.height]

    def check_mouse(self, mx, my):
        if mx >= self.x and my >= self.y and mx < self.x+self.width and my < self.y+self.height:
            return True
        return False

    def get_rel(self, pos):
        return [ pos[0] - self.x, pos[1] - self.y ]

    def mouse_button_down(self, event):
        event.x = event.pos[0]
        event.y = event.pos[1]
        if self.check_mouse(event.x, event.y):
            
            if event.button == 1:
                self.buttonevent.left_click(self, event, True)
                event.interface.focus = self
            elif event.button == 2:
                self.buttonevent.scroll_click(self, event, True)
            elif event.button == 3:
                self.buttonevent.right_click(self, event, True)
                #event.interface.focus = self
            elif event.button == 4:
                self.buttonevent.scroll_up(self, event, True)
            elif event.button == 5:
                self.buttonevent.scroll_down(self, event, True)

    def mouse_button_up(self, event):
        event.x = event.pos[0]
        event.y = event.pos[1]
        if self.check_mouse(event.x, event.y):
            if event.button == 1:
                self.buttonevent.left_click(self, event, False)
            elif event.button == 2:
                self.buttonevent.scroll_click(self, event, False)
            elif event.button == 3:
                self.buttonevent.right_click(self, event, False)
            elif event.button == 4:
                self.buttonevent.scroll_up(self, event, False)
            elif event.button == 5:
                self.buttonevent.scroll_down(self, event, False)

    def mouse_move(self, event):
        event.x = event.pos[0]
        event.y = event.pos[1]
        if self.check_mouse(event.x, event.y):
            self.buttonevent.mouse_move(self, event)

    def key_down(self, event):
        self.buttonevent.key_press(self, event, True)

    def key_up(self, event):
        self.buttonevent.key_press(self, event, False)

    def draw(self, screen):
        self.buttonevent.draw(self, screen)

    def update(self, interface):
        if self.check_mouse(*pygame.mouse.get_pos()):
            if self.popup_timer < 0:
                self.popup_timer = pygame.time.get_ticks()
            elif pygame.time.get_ticks() - self.popup_timer >= 500 and not self.popup:
                self.popup = True
                interface.addPopup(self)
        elif self.popup:
            self.popup = False
            self.popup_timer = -1
            interface.destroyPopup()
        elif self.popup_timer > 0:
            self.popup_timer = -1
            
        self.buttonevent.update(self)


class Group:
    def __init__(self, x, y, buttons = []):
        self.x = x
        self.y = y
        self.buttons = []
        self.addButtons(buttons)

    def setX(self, x):
        diffx = x - self.x
        for button in buttons:
            button.x+=diffx
        self.x = x

    def setY(self, y):
        diffy = y - self.y
        for button in buttons:
            button.y+=diffy
        self.y = y

    def setPos(self, pos):
        diff = [ pos[0] - self.x, pos[1] - self.y]
        for button in buttons:
            button.x+=diff[0]
            button.y+=diff[1]
        self.x = pos[0]
        self.y = pos[1]

    def addButton(self, button):
        button.x+=self.x
        button.y+=self.y
        self.buttons.append(button)

    def addButtons(self, buttons):
        for button in buttons:
            self.addButton(button)

    def mouse_button_down(self, event):
        for button in self.buttons:
            button.mouse_button_down(event)

    def mouse_button_up(self, event):
        for button in self.buttons:
            button.mouse_button_up(event)

    def mouse_move(self, event):
        for button in self.buttons:
            button.mouse_move(event)

    def key_down(self, event):
        for button in self.buttons:
            button.key_down(event)

    def key_up(self, event):
        for button in self.buttons:
            button.key_up(event)

    def draw(self, screen):
        for button in self.buttons:
            button.draw(screen)

    def update(self, interface):
        for button in self.buttons:
            button.update(interface)

#contains the loop for an interface. everything should be controllable via the use of buttons.
class Interface:
    def __init__(self, width, height, buttons = [], background = None):
        self.buttons = buttons
        self.screen = pygame.display.set_mode((width, height))
        self.background = background
        if background == None:
            self.background = pygame.Surface((width, height))
            self.background.fill([0,0,0])
        self.popup = []
        self.focus = None

    def addPopup(self, button):
        if button.desc != "":
            self.popup.append(popup_font.render(button.desc, 2, [255, 255, 255], [0, 0, 0]))

    def destroyPopup(self):
        self.popup = []

    def addButton(self, button):
        self.buttons.append(button)

    def addButtons(self, buttons):
        for button in buttons:
            self.buttons.append(button)

    def start(self):
        while True:
            for event in pygame.event.get():
                event.interface = self
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for button in self.buttons:
                        button.mouse_button_down(event)
                elif event.type == pygame.MOUSEBUTTONUP:
                    for button in self.buttons:
                        button.mouse_button_up(event)
                elif event.type == pygame.MOUSEMOTION:
                    for button in self.buttons:
                        button.mouse_move(event)
                elif event.type == pygame.KEYDOWN:
                    for button in self.buttons:
                        button.key_down(event)
                elif event.type == pygame.KEYUP:
                    for button in self.buttons:
                        button.key_up(event)
            self.screen.blit(self.background, [0,0])
            for button in self.buttons:
                button.update(self)
                button.draw(self.screen)
            
            for i in range(len(self.popup)):
                mpos = pygame.mouse.get_pos()
                self.screen.blit(self.popup[i], [mpos[0], mpos[1] + 17 + (i*20)])
            pygame.display.flip()


#
# USEFUL BUTTONEVENTS:
#

# Textbox class, for entering a single line of text
# supports any size of button.
class TextBox(ButtonEvent):
    def __init__(self, font_name, height, colour, bold = False, italic = False):
        self.text = ""
        self.cursor = 0
        self.height = height
        self.colour = colour

        req_h = (2 * height) / 3
        size = 5
        self.font = pygame.font.SysFont(font_name, size, bold, italic)
        while self.font.get_height() < req_h:
            size = size + 1
            self.font = pygame.font.SysFont(font_name, size, bold, italic)
        self.font = pygame.font.SysFont(font_name, size - 1, bold, italic)
        self.changed = True
        self.img = None
        self.offset = 0

        self.ldown = False
        self.rdown = False
        self.bdown = False
        self.cds = Cooldowns()
        self.cds.create("left_start", 500)
        self.cds.create("right_start", 500)
        self.cds.create("back_start", 500)
        self.cds.create("left", 30)
        self.cds.create("right", 30)
        self.cds.create("back", 30)

    def move_cursor(self, left):
        if left:
            if self.cursor > 0:
                self.cursor = self.cursor - 1
                size = self.font.size(self.text[:self.cursor])
                if size[0] < self.offset:
                    self.offset = size[0]
                self.changed = True
        else:
            if self.cursor < len(self.text):
                self.cursor = min(len(self.text), self.cursor + 1)
                size = self.font.size(self.text[:self.cursor])
                if size[0] > button.width + self.offset:
                    self.offset = self.offset + (size[0] - ( self.offset + button.width))
                self.changed = True

    def backspace(self):
        if len(self.text) > 0:
                    self.text = self.text[:-1]
                    self.move_cursor(True)
                    self.changed = True
        
    def key_press(self, button, event, down):
        if down and event.interface.focus == button:
            if event.key == pygame.K_BACKSPACE:
                self.backspace()
                self.cds.start("back_start")
                self.bdown = True
            elif event.key == pygame.K_LEFT:
                self.move_cursor(True)
                self.cds.start("left_start")
                self.ldown = True
            elif event.key == pygame.K_RIGHT:
                self.move_cursor(False)
                self.cds.start("right_start")
                self.rdown = True
            else:
                char = event.unicode
                if char != None:
                    self.text = self.text[:self.cursor] + char + self.text[self.cursor:]
                    self.move_cursor(False)
                    self.changed = True
        elif not down and event.interface.focus == button:
            if event.key == pygame.K_LEFT:
                self.ldown = False
                self.cds.stop("left_start")
                self.cds.stop("left")
            elif event.key == pygame.K_RIGHT:
                self.rdown = False
                self.cds.stop("right_start")
                self.cds.stop("right")
            elif event.key == pygame.K_BACKSPACE:
                self.bdown = False
                self.cds.stop("back_start")
                self.cds.stop("back")
        #print("test")

    def update(self, button):
        if self.ldown and self.cds.check("left_start"):
            self.cds.stop()
            self.cds.start("left")
        elif self.ldown and self.cds.check("left"):
            self.move_cursor(True)
            self.cds.start()

        if self.rdown and self.cds.check("right_start"):
            self.cds.stop()
            self.cds.start("right")
        elif self.rdown and self.cds.check("right"):
            self.move_cursor(False)
            self.cds.start()

        if self.bdown and self.cds.check("back_start"):
            self.cds.stop()
            self.cds.start("back")
        elif self.bdown and self.cds.check("back"):
            self.backspace()
            self.cds.start()

    def draw(self, button, screen):
        if self.changed:
            self.img = self.font.render(self.text, 2, self.colour)
            size = self.font.size(self.text[:self.cursor])
            cx = size[0]
            if self.cursor > 0:
                cx = cx - 2
            pygame.draw.rect(self.img, self.colour, [cx, 0, 2, self.height])
            self.changed = False
        screen.blit(self.img, [button.x + 2, button.y + (button.height - self.img.get_height() - 2)], [self.offset,0,button.width, button.height])
        if event.interface.focus == button:
            pygame.draw.rect(screen, [200, 200, 200], [button.x, button.y, button.width, button.height], 2)

class Label:
    def __init__(self, width, height, text, fontname, bold = False, italic = False):
        self.width = width
        self.height = height
        self.text = text
        self.bold = bold
        self.italic = italic
        self.fontname = fontname
        self.updateFont()

    def setText(self, text):
        self.text = text
        self.updateFont()

    def updateFont(self):
        size = 5
        self.font = pygame.font.SysFont(self.fontname, size, self.bold, self.italic)
        fontsize = self.font.size(self.text)
        while fontsize[1] < self.height and fontsize[0] < self.width:
            size = size + 1
            self.font = pygame.font.SysFont(self.fontname, size, self.bold, self.italic)
            fontsize = self.font.size(self.text)
        self.font = pygame.font.SysFont(self.fontname, size, self.bold, self.italic)

    def render(self, antialias = 2, colour = [0, 0, 0], background = None):
        return self.font.render(self.text, antialias, colour, background)

    def centre(self):
        size = self.font.size(self.text)
        return [ math.floor( (self.width - size[0]) / 2 ), math.floor( (self.height - size[1]) / 2 ) ]
