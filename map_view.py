import pygame, math, sys, random, json


pygame.init()
screen = pygame.display.set_mode((1080, 720))

#TODO:
# use text box to implement saving/loading file names
# possibly use tkinter (askopenfilename) for a file browser for loading file/images.
# create a way of loading images (add a button)
# think of something interesting to do with the remaining space on the UI.

class ImageManager:
    def __init__(self, tilemap, iconsize):
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
        if not self.checkScale(image):
            image = pygame.transform.scale(image, (self.tilemap.tile_width, self.tilemap.tile_height))
        self.images[name] = [image]
        self.createIcon(name)

    def loadTiles(self, image, columns, rows, name):
        tile_width = math.floor(image.get_width()/columns)
        tile_height = math.floor(image.get_height()/rows)
        need_to_scale = True
        if tile_width == self.tilemap.tile_width and tile_height == self.tilemap.tile_height:
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
        if image.get_width() != self.tilemap.tile_width or image.get_height() != self.tilemap.tile_height:
            return False
        return True

    def getImage(self, name, imgid = 0):
        if name != None and imgid != None:
            img = self.images[name][imgid]
            if not self.checkScale(img):
                img = pygame.transform.scale(img, (self.tilemap.tile_width, self.tilemap.tile_height))
                self.images[name][imgid] = img
            return img

    def getTileImage(self, tile):
        return self.getImage(tile.info["img_name"], tile.info["img_id"])

class Tile:
    def __init__(self, x, y, z, image_manager):
        self.x = x
        self.y = y
        self.z = z

        self.im = image_manager

        self.rx = x * self.im.tilemap.tile_width
        self.ry = y * self.im.tilemap.tile_height

        self.info = {}
        self.info["img_name"] = None
        self.info["img_id"] = 0
        self.colour = [ random.randint(0, 255), random.randint(0, 255), random.randint(0, 255) ]

    def updateTileSize(self):
        self.rx = self.x * self.im.tilemap.tile_width
        self.ry = self.y * self.im.tilemap.tile_height
    

    def draw(self, target, offset):
        img = self.im.getTileImage(self)
        if img != None:
            target.blit(img, [ self.rx-offset[0], self.ry-offset[1]])
        #pygame.draw.rect(target, self.colour, [ self.rx-offset[0], self.ry-offset[1], self.im.tilemap.tile_width, self.im.tilemap.tile_height ])
        #print("yay ", str(self.colour), "(",self.x,":",self.y,")")

    def __str__(self):
        return str(self.x)+":"+str(self.y)+":"+str(self.z)+":"+str(self.info["img_name"])+":"+str(self.info["img_id"])

def createMap(info, tile_size, icon_size, im):
    width = info[0]
    height = info[1]
    strgrid = info[2]
    tilemap = Map([info[0], info[1]], tile_size, icon_size, im)
    for x in range(width):
        for y in range(height):
            for z in range(10):
                text = strgrid[x][y][z]
                if text != "None":
                    data = text.split(":")
                    paint = [str(data[3]), int(data[4])]
                    if paint[0] == "None":
                        paint[0] = None
                    tilemap.paint(paint, int(data[2]), [int(data[0]), int(data[1])])
    return tilemap

class Map:
    def __init__(self, map_size, tile_size, icon_size, image_manager = None):
        self.width = map_size[0]
        self.height = map_size[1]
        self.tile_width = tile_size[0]
        self.tile_height = tile_size[1]
        self.im = image_manager
        if self.im == None:
            self.im = ImageManager(self, icon_size)
        #self.grid = [ [ [None] * 10 ] * height ] * width
        self.grid = []
        for x in range(self.width):
            self.grid.append([])
            for y in range(self.height):
                self.grid[x].append([None]*10)
                new_tile = Tile(x, y, 0, self.im)
                self.grid[x][y][0] = new_tile
                
        self.selected = [0, 0]
        self.selection_start = None
        self.selection_end = None

    def getPaintBounds(self):
        bounds = [0, 0, self.width-1, self.height-1]
        if self.selection_start != None:
            bounds = [min(self.selection_start[0], self.selection_end[0]), min(self.selection_start[1], self.selection_end[1]), max(self.selection_start[0], self.selection_end[0]) , max(self.selection_start[1], self.selection_end[1]) ]
        return bounds

    def flood(self, paint, start, layer, layer_locked):
        original_tile = self.grid[start[0]][start[1]][layer]
        og_paint = [None, 0]
        if original_tile == None:
            og_paint = [ original_tile.info["img_name"], original_tile.info["img_id"] ]
        done = []
        todo = [start]
        lower_layer = 0
        bounds = self.getPaintBounds()
        if layer_locked:
            lower_layer = layer
        upper_layer = layer + 1
        for z in range(lower_layer, upper_layer):
            self.paint(paint, z, start)
        while len(todo) > 0:
            newtodo = []
            for pos in todo:
                
                nextup = [ [ pos[0] - 1, pos[1] ],
                           [ pos[0] + 1, pos[1] ],
                           [ pos[0], pos[1] - 1 ],
                           [ pos[0], pos[1] + 1 ] ]
                for cur in nextup:
                    if cur[0] >= bounds[0] and cur[1] >= bounds[1] and cur[0] <= bounds[2] and cur[1] <= bounds[3]:
                        tileset = self.grid[cur[0]][cur[1]]
                        if not tileset in done:
                            for z in range(lower_layer, upper_layer):
                                tile = tileset[z]
                                if tile != None:
                                    if tile.info["img_name"] == og_paint[0] and tile.info["img_id"] == og_paint[1]:
                                        tile.info["img_name"] = paint[0]
                                        tile.info["img_id"] = paint[1]
                                
                            done.append(tileset)
                            newtodo.append(cur)
            todo = newtodo
                        

    def pack_info(self):
        str_grid = []
        for x in range(self.width):
            str_grid.append([])
            for y in range(self.height):
                str_grid[x].append([])
                for z in range(10):
                    tile = self.grid[x][y][z]
                    str_grid[x][y].append(str(tile))
        return [self.width, self.height, str_grid]

    def paint(self, paint, layer, selected = None):
        if selected == None:
            selected = self.selected
        bounds = self.getPaintBounds()
        if selected[0] >= bounds[0] and selected[1] >= bounds[1] and selected[0] <= bounds[2] and selected[1] <= bounds[3]:
            tile = self.grid[selected[0]][selected[1]][layer]
            if tile == None:
                tile = Tile(selected[0], selected[1], layer, self.im)
                self.grid[selected[0]][selected[1]][layer] = tile
            tile.info["img_name"] = paint[0]
            tile.info["img_id"] = paint[1]

    def getTileSet(self, mx, my, offset):
        tx, ty = math.floor((mx + offset[0])/self.tile_width), math.floor((my + offset[1])/self.tile_height)
        if tx >= 0 and ty >= 0 and tx < self.width and ty < self.height:
            return self.grid[tx][ty]
        return

    def convert(self, mx, my, offset):
        return [min(self.width-1, max(0, math.floor((mx + offset[0])/self.tile_width))), min(self.height-1, max(0, math.floor((my + offset[1])/self.tile_height)))]

    def setSelected(self, mx, my, offset):
        self.selected = self.convert(mx, my, offset)

    def setTileSize(self, tile_width, tile_height):
        self.tile_width = max(4, min(128, tile_width))
        self.tile_height = max(4, min(128, tile_height))
        for x in range(self.width):
            for y in range(self.height):
                for z in range(10):
                    tile = self.grid[x][y][z]
                    if tile != None:
                        tile.updateTileSize()

    def draw(self, target, offset, layer, layer_lock = False):
        target.fill([0,0,0])
        startx, starty =  max(0, math.floor(offset[0]/self.tile_width)), max(0, math.floor(offset[1]/self.tile_height))
        endx, endy = min(self.width, math.ceil(target.get_width()/self.tile_width) + startx + 1), min(self.height, math.floor(target.get_height()/self.tile_height) + starty + 2)
        #print(startx,":",starty)
        #print(endx,":",endy)
        lower_layer = 0
        if layer_lock:
            lower_layer = min(9, layer)
        for x in range(startx, endx):
            for y in range(starty, endy):
                for z in range(lower_layer, min(10, layer+1)):
                    tile = self.grid[x][y][z]
                    if tile != None:
                        tile.draw(target, offset)
        pygame.draw.rect(target, [255, 255, 255], [ (self.selected[0] * self.tile_width) - offset[0], (self.selected[1] * self.tile_height) - offset[1], self.tile_width, self.tile_height ], 2)
        pygame.draw.rect(target, [255, 255, 255], [ -offset[0], -offset[1], self.width*self.tile_width, self.height*self.tile_height], 2)

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

class Button:
    def __init__(self, dims, buttonevent, name, desc):
        self.x = dims[0]
        self.y = dims[1]
        self.width = dims[2]
        self.height = dims[3]
        self.buttonevent = buttonevent
        self.name = name
        self.desc = desc

        self.popup_timer = -1
        self.popup = False

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
                global focus
                focus = self
            elif event.button == 2:
                self.buttonevent.scroll_click(self, event, True)
            elif event.button == 3:
                self.buttonevent.right_click(self, event, True)
                focus = self
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

    def update(self):
        if self.check_mouse(*pygame.mouse.get_pos()):
            if self.popup_timer < 0:
                self.popup_timer = pygame.time.get_ticks()
            elif pygame.time.get_ticks() - self.popup_timer >= 500 and not self.popup:
                self.popup = True
                main.addPopup(self)
        elif self.popup:
            self.popup = False
            self.popup_timer = -1
            main.destroyPopup()
        elif self.popup_timer > 0:
            self.popup_timer = -1
            
        self.buttonevent.update(self)



class MapButton(ButtonEvent):
    def __init__(self, map_size, tile_size, icon_size, button_size):
        
        self.tilemap = Map(map_size, tile_size, icon_size)
        self.navi_image = pygame.image.load("navigator.png")
        self.tilemap.im.loadTiles(pygame.image.load("reds.png"), 4, 1, "reds")
        self.tilemap.im.loadTiles(pygame.image.load("blues.png"), 4, 1, "blues")
        self.tilemap.im.loadTiles(pygame.image.load("greens.png"), 4, 1, "greens")
        
        self.width = button_size[0]
        self.height = button_size[1]
        self.image = pygame.Surface((self.width, self.height))
        self.offset = [0,0]

        self.change = True
        
        self.rmb_down = False
        self.rmb_lastpos = [0, 0]
        
        self.mmb_down = False
        self.mmb_start = [0,0]

        self.lmb_down = False
        
        self.layer = 0
        self.layer_lock = False

        self.key_velocity = [1, 1]

        self.cds = Cooldowns()
        self.cds.create("zoom", 1).start()
        self.cds.create("move_keys", 10).start()
        self.cds.create("navigate", 10).start()
        self.cds.create("save_load", 100).start()

        # tool ids:
        #     0 = paint brush
        #     1 = bucket fill
        #     2 = selection
        #     3 = eraser (not used)
        
        self.tool = 0 
        self.paint = [None, 0]
        self.popup = []

    def load(self, data):
        im = self.tilemap.im
        old_tilemap = self.tilemap
        self.tilemap = createMap(data, [self.tilemap.tile_width, self.tilemap.tile_height], im.iconsize, im)
        im.tilemap = self.tilemap
        del old_tilemap
        
        self.offset = [0,0]
        self.layer = 0
        self.layer_lock = False
        self.change = True

    
            

    def new(self):
        im = self.tilemap.im
        old_tilemap = self.tilemap
        self.tilemap = Map([self.tilemap.width, self.tilemap.height], [self.tilemap.tile_width, self.tilemap.tile_height], im.iconsize, im)
        im.tilemap = self.tilemap
        del old_tilemap
        
        self.offset = [0,0]
        self.layer = 0
        self.layer_lock = False
        self.change = True

    def right_click(self, button, event, down):
        self.rmb_down = down
        self.rmb_lastpos = button.get_rel(event.pos)

    def left_click(self, button, event, down):
        self.lmb_down = down
        
        if down == True:
            rel = button.get_rel(event.pos)
            if self.tool == 2:
                self.tilemap.selection_start = self.tilemap.convert(rel[0], rel[1], self.offset)
                self.tilemap.selection_end = list(self.tilemap.selection_start)
                self.change = True
            elif self.tool == 1:
                self.tilemap.flood(self.paint, self.tilemap.convert(rel[0], rel[1], self.offset), self.layer, self.layer_lock)
                self.change = True
        else:
            if self.tool == 0:
                self.tilemap.paint(self.paint, self.layer)
                self.change = True
            elif self.tool == 2:
                if self.tilemap.selection_start[0] == self.tilemap.selection_end[0] and self.tilemap.selection_start[1] == self.tilemap.selection_end[1]:
                    self.tilemap.selection_start = None
                    self.tilemap.seelction_end = None
                    self.change = True
            elif self.tool == 3:
                self.tilemap.paint([None, 0], self.layer)
                self.change = True
                

    def scroll_click(self, button, event, down):
        self.mmb_down = down
        self.mmb_start = event.pos
        self.change = True

    def mouse_move(self, button, event):
        rel = button.get_rel(event.pos)
        self.tilemap.setSelected(rel[0], rel[1], self.offset)

        if self.rmb_down:
            rel = button.get_rel(event.pos)
            diffx = rel[0] - self.rmb_lastpos[0]
            diffy = rel[1] - self.rmb_lastpos[1]
            self.offset = [ self.offset[0] - diffx, self.offset[1] - diffy ]
            self.rmb_lastpos = rel
        

        if self.lmb_down:
            if self.tool == 0:
                self.tilemap.paint(self.paint, self.layer)
            elif self.tool == 2:
                rel = button.get_rel(event.pos)
                self.tilemap.selection_end = self.tilemap.convert(rel[0], rel[1], self.offset)
            elif self.tool == 3:
                self.tilemap.paint([None, 0], self.layer)
            
        self.change = True

    def zoom(self, rel, amount):
        if self.cds.check("zoom"):
            if pygame.key.get_pressed()[pygame.K_LCTRL]:
                amount = [amount[0]*4, amount[1]*4]
            
            xtilepos = (self.offset[0] + rel[0]) / self.tilemap.tile_width
            ytilepos = (self.offset[1] + rel[1]) / self.tilemap.tile_height
            
            self.tilemap.setTileSize(self.tilemap.tile_width + amount[0], self.tilemap.tile_height + amount[1])

            self.offset[0] = (xtilepos * self.tilemap.tile_width) - rel[0]
            self.offset[1] = (ytilepos * self.tilemap.tile_height) - rel[1]
            
            self.change = True
            self.cds.start()

    def scroll_up(self, button, event, down):
        self.zoom(button.get_rel([event.x, event.y]), [1,1])

    def scroll_down(self, button, event, down):
        self.zoom(button.get_rel([event.x, event.y]), [-1,-1])

    def update(self, button):
        keys = pygame.key.get_pressed()
        if focus == main:
            elapsed = min(1, self.cds.elapsed("move_keys"))
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.offset[0] = self.offset[0] - (self.key_velocity[0] * elapsed)
                self.change = True
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.offset[0] = self.offset[0] + (self.key_velocity[0] * elapsed)
                self.change = True
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.offset[1] = self.offset[1] - (self.key_velocity[1] * elapsed)
                self.change = True
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.offset[1] = self.offset[1] + (self.key_velocity[1] * elapsed)
                self.change = True
            self.cds.start()
    
            if self.cds.check("save_load"):
                if keys[pygame.K_q]:
                    save(fnbox.text)
                    self.cds.start()
                if keys[pygame.K_e]:
                    load(fnbox.text)
                    self.cds.start()
                if keys[pygame.K_r]:
                    self.new()
        
        if self.mmb_down and self.cds.check("navigate"):
            diffx = (event.pos[0] - self.mmb_start[0]) / 10
            diffy = (event.pos[1] - self.mmb_start[1]) / 10
            self.offset = [ self.offset[0] + diffx, self.offset[1] + diffy ]
            self.cds.start()
            self.change = True

    def addPopup(self, button):
        if button.desc != "":
            self.popup.append(popup_font.render(button.desc, 2, [255, 255, 255], [0, 0, 0]))

    def destroyPopup(self):
        self.popup = []

    def draw(self, button, screen):
        pygame.display.set_caption(str(self.offset[0])+":"+str(self.offset[1]))
        if self.change:
            self.tilemap.draw(self.image, self.offset, self.layer, self.layer_lock)
            self.change = False
        if self.tilemap.selection_start != None:
            colour = [255, 255, 255]
            bounds = self.tilemap.getPaintBounds()
            start = [ bounds[0], bounds[1] ]
            end = [ bounds[2], bounds[3] ]
            diff = [ (end[0] - start[0]) + 1, (end[1] - start[1]) + 1 ]
            pygame.draw.rect(self.image, colour, [ (start[0]*self.tilemap.tile_width) - self.offset[0], (start[1]*self.tilemap.tile_height) - self.offset[1], self.tilemap.tile_width, self.tilemap.tile_height ], 2)
            pygame.draw.rect(self.image, colour, [ (end[0]*self.tilemap.tile_width) - self.offset[0], (end[1]*self.tilemap.tile_height) - self.offset[1], self.tilemap.tile_width, self.tilemap.tile_height], 2)
            pygame.draw.rect(self.image, colour, [ (start[0]*self.tilemap.tile_width) - self.offset[0], (start[1]*self.tilemap.tile_height) - self.offset[1], self.tilemap.tile_width*diff[0], self.tilemap.tile_height*diff[1]], 2)
        screen.blit(self.image, [button.x, button.y])
        if self.mmb_down:
            screen.blit(self.navi_image, [self.mmb_start[0] - 6, self.mmb_start[1] - 6])

class TileNameSelector(ButtonEvent):
    def __init__(self, icon_size):
        self.offset = 0
        self.tile_width = icon_size[0]
        self.tile_height = icon_size[1]
        self.selected = 0
        self.last_selected = 0
        #self.cds = Cooldowns()

    def scroll(self, amount):
        if pygame.key.get_pressed()[pygame.K_LCTRL]:
                amount = amount * 4
        self.offset = min((main.tilemap.im.iconAmount()-1)*self.tile_height, max(0, self.offset + amount))
    
    def scroll_up(self, button, event, down):
        self.scroll(-4)

    def scroll_down(self, button, event, down):
        self.scroll(4)

    def mouse_move(self, button, event):
        rel = button.get_rel(event.pos)
        self.selected = math.floor( (self.offset + rel[1])/self.tile_height )

    def left_click(self, button, event, down):
        if down == True and self.selected >= 0 and self.selected < main.tilemap.im.iconAmount():
            old_name = main.paint[0]
            main.paint[0] = main.tilemap.im.icon_names[self.selected]
            self.last_selected = self.selected

    def draw(self, button, screen):
        image = pygame.Surface((button.width, button.height))
        image.fill([255, 255, 255])
        start = math.floor(self.offset / self.tile_height)
        end = min(main.tilemap.im.iconAmount(), start + math.ceil(button.height / self.tile_height))
        for i in range(start, end):
            icon = main.tilemap.im.getIcon(i)
            image.blit(icon, [0, (i*self.tile_height) - self.offset])
        pygame.draw.rect(image, [50,50,50], [0, (self.last_selected*self.tile_height) - self.offset, self.tile_width-1, self.tile_height-1], 4)
        pygame.draw.rect(image, [0,0,0], [0, (self.selected*self.tile_height) - self.offset, self.tile_width, self.tile_height], 3)
        screen.blit(image, [button.x, button.y])

class TileIdSelector(ButtonEvent):
    def __init__(self, icon_size):
        self.offset = 0
        self.tile_width = icon_size[0]
        self.tile_height = icon_size[1]
        self.selected = 0
        self.last_selected = 0
        self.last_name = None
        #self.cds = Cooldowns()
        
    def scroll(self, amount):
        if pygame.key.get_pressed()[pygame.K_LCTRL]:
                amount = amount * 4
        self.offset = min((main.tilemap.im.iconIdAmount(main.paint[0])-1)*self.tile_height, max(0, self.offset + amount))
    
    def scroll_up(self, button, event, down):
        self.scroll(-4)

    def scroll_down(self, button, event, down):
        self.scroll(4)

    def mouse_move(self, button, event):
        rel = button.get_rel(event.pos)
        self.selected = math.floor( (self.offset + rel[1])/self.tile_height )

    def left_click(self, button, event, down):
        if down == True and self.selected >= 0 and self.selected < main.tilemap.im.iconIdAmount(main.paint[0]):
            main.paint[1] = self.selected
            self.last_selected = self.selected

    def draw(self, button, screen):
        if self.last_name != main.paint[0]:
            self.selected = 0
            self.last_selected = 0
            main.paint[1] = 0
            self.last_name = main.paint[0]
        image = pygame.Surface((button.width, button.height))
        image.fill([255, 255, 255])
        start = math.floor(self.offset / self.tile_height)
        end = min(main.tilemap.im.iconIdAmount(main.paint[0]), start + math.ceil(button.height / self.tile_height))
        for i in range(start, end):
            icon = main.tilemap.im.getIdIcon(main.paint[0], i)
            if icon != None:
                image.blit(icon, [0, (i*self.tile_height) - self.offset])
        pygame.draw.rect(image, [50,50,50], [0, (self.last_selected*self.tile_height) - self.offset, self.tile_width-1, self.tile_height-1], 4)
        pygame.draw.rect(image, [0,0,0], [0, (self.selected*self.tile_height) - self.offset, self.tile_width, self.tile_height], 3)
        screen.blit(image, [button.x, button.y])

class LayerArrow(ButtonEvent):
    def __init__(self, direction):
        self.direction = direction

    def left_click(self, button, event, down):
        if down == True:
            main.layer = min(9, max(0, main.layer + self.direction))
            main.change = True

class LayerSelection(ButtonEvent):

    def left_click(self, button, event, down):
        #start [15, 157], width: 18
        if down == True:
            rel = button.get_rel(event.pos)
            main.layer = math.floor(rel[0] / 18)
            main.change = True
    
    def draw(self, button, screen):
        layer = main.layer
        #start point @ 18, 159
        #new position every 18
        x = 18 * (layer + 1)
        pygame.draw.rect(screen, [180, 180, 180], [18 * (layer + 1), 159, 12, 15], 2)

class LayerLock(ButtonEvent):

    def left_click(self, button, event, down):
        if down == True:
            main.layer_lock = (main.layer_lock == False)
            main.change = True

    def draw(self, button, screen):
        if main.layer_lock:
            pygame.draw.rect(screen, [190, 0, 0], [1, 130, 18, 24], 2)

class FuncButton(ButtonEvent):
    def __init__(self, func):
        self.func = func
    def left_click(self, button, event, down):
        if down == True:
            if self.func == "save":
                save(fnbox.text)
            elif self.func == "load":
                load(fnbox.text)
            elif self.func == "new":
                main.new()

class ToolButton(ButtonEvent):
    def __init__(self, tool):
        self.tool = tool

    def left_click(self, button, event, down):
        if down == True:
            main.tool = self.tool

    def draw(self, button, screen):
        if main.tool == self.tool:
            pygame.draw.rect(screen, [200, 200, 200], [button.x, button.y, button.width, button.height], 2)

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
        if down and focus == button:
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
        elif not down and focus == button:
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
        if focus == button:
            pygame.draw.rect(screen, [200, 200, 200], [button.x, button.y, button.width, button.height], 2)

icon_size = [64, 64]
    
buttons = [ Button( [228, 20, 832, 680], MapButton( [50, 50], [16, 16], icon_size, [832, 680]), "map", ""),
            Button( [20, 200, 64, 500], TileNameSelector(icon_size), "name_selector", "" ),
            Button( [124, 200, 64, 500], TileIdSelector(icon_size), "id_selector", ""),
            Button( [1, 155, 15, 23], LayerArrow(-1), "left_layer_arrow", "layer down"),
            Button( [194, 155, 15, 23], LayerArrow(1), "right_layer_arrow", "layer up"),
            Button( [15, 155, 180, 23], LayerSelection(), "layer_selector", "layer selection"),
            Button( [153, 130, 18, 24], FuncButton("save"), "save", "save map"),
            Button( [172, 130, 18, 24], FuncButton("load"), "load", "load map"),
            Button( [191, 130, 18, 24], FuncButton("new"), "new", "new map"),
            Button( [1, 130, 18, 24], LayerLock(), "layer_lock", "lock layer"),
            Button( [160, 4, 22, 29], ToolButton(0), "pencil", "pencil"),
            Button( [184, 4, 22, 29], ToolButton(1), "bucket", "bucket"),
            Button( [160, 35, 22, 29], ToolButton(2), "select", "select"),
            Button( [184, 35, 22, 29], ToolButton(3), "rubber", "rubber"),
            Button( [22, 132, 128, 20], TextBox("", 20, [50, 50, 50]), "filename", "enter file name")]


def findButton(name):
    for button in buttons:
        if button.name == name:
            return button
    return None
#tile_select @ [20, 200], size: [64, 500]
#id_select @ [124, 200], size: [64, 500]
#layer_down @ [1, 155], size: [15, 23]
#layer_up @ [194, 155], size: [15, 23]
#layer_selection @ [16, 155], size: [178, 23]
#save @ [153, 130], size: [18, 24]
#load @ [172, 130], size: [18, 24]
#new @ [191, 130], size: [18, 24]
#layer_lock @ [1, 130], size: [18, 24]
#pencil @ [160, 4], size: [22, 29]
#bucket @ [184, 4], size: [22, 29]
#select @ [160, 35], size: [22, 29]
#rubber @ [184, 35], size: [22, 29]
#textbox @ [22, 132], size: [128, 20]
global main, focus, fnbox
main = buttons[0].buttonevent
fnbox = findButton("filename").buttonevent
focus = main
popup_font = pygame.font.SysFont("Georgia-Italic", 18)

def fixName(name):
    if not "." in name:
        name = name + '.tmd'
    return name

def save(name):
    f = open(fixName(name), 'w')
    json.dump(main.tilemap.pack_info(), f)
    f.close()

def load(name):
    f = open(fixName(name))
    data = json.load(f)
    main.load(data)
    f.close()
                
background = pygame.image.load("background.png")

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for button in buttons:
                button.mouse_button_down(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            for button in buttons:
                button.mouse_button_up(event)
        elif event.type == pygame.MOUSEMOTION:
            for button in buttons:
                button.mouse_move(event)
        elif event.type == pygame.KEYDOWN:
            for button in buttons:
                button.key_down(event)
        elif event.type == pygame.KEYUP:
            for button in buttons:
                button.key_up(event)
    screen.blit(background, [0,0])
    for button in buttons:
        button.update()
        button.draw(screen)
    
    for i in range(len(main.popup)):
        mpos = pygame.mouse.get_pos()
        screen.blit(main.popup[i], [mpos[0], mpos[1] + 17 + (i*20)])
    pygame.display.flip()
