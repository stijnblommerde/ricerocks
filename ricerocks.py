# program template for Spaceship
import simplegui
import math
import random

# globals for user interface
WIDTH = 800
HEIGHT = 600
SCREEN_SIZE = [WIDTH,HEIGHT]
ACCELERATION = 0.05
FRICTION = 0.005
MISSILE_SPEED = 5

score = 0
lives = 3
time = 0.5
rock_rotation = (2 * math.pi * 1) /60  # full circle per second (draw updates 1/60th second)
started = False
my_ship = None
rock_group = set([])
missile_group = set([])
speed_increase = 1
speed_increased = False

class ImageInfo:
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated

    
# art assets created by Kim Lathrop, may be freely re-used in non-commercial projects, please credit Kim
    
# debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/debris2_blue.png")

# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_blue.s2014.png")

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")

# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, 50)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot2.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_alpha.png")

# sound assets purchased from sounddogs.com, please do not redistribute
soundtrack = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
missile_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(.5)
ship_thrust_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
explosion_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")

# helper functions
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p,q):
    return math.sqrt((p[0] - q[0]) ** 2+(p[1] - q[1]) ** 2)

def process_sprite_group(group, canvas):
    for sprite in set(group):
        sprite.draw(canvas)
        if sprite.update():
            group.remove(sprite)
            
def group_collide(group, other_object):
    for sprite in set(group):
        if sprite.collide(other_object):
            group.remove(sprite)
            
            #creates explosion after collision 
            explosion = Sprite(other_object.pos, [0, 0], 0, 0, explosion_image, 
                               explosion_info, explosion_sound) 
            explosion_group.add(explosion)
            return True
    return False

def group_group_collide(group1, group2):
    count = 0
    for sprite in set(group1):
        if group_collide(group2, sprite):
            count = count+1
            group1.discard(sprite)
    return count 

def setup_game():
    global my_ship, rock_group, missile_group, explosion_group, score, lives, multiplier
    
    #initializes variables 
    my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)
    rock_group = set([])
    missile_group = set([])
    explosion_group = set([])
    score = 0
    lives = 3
    soundtrack.rewind()
    multiplier = 1

def speed_update(random_vel):
    global speed_increase, speed_increased
    if score % 50 == 0 and score != 0:
        if not speed_increased:
            speed_increase += 1 
            random_vel[0] *= speed_increase
            random_vel[1] *= speed_increase
            speed_increased = True
    else:
        speed_increased = False
    
    
# Ship class
class Ship:
    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        
    def draw(self,canvas):
        if self.thrust:
            #displays right image of tiled image: ship with thrusters on
            canvas.draw_image(self.image, [self.image_center[0] + 90, self.image_center[1]], self.image_size, self.pos, self.image_size, self.angle)
        else:
            #displays left image of tiled image: ship with thrusters off
            canvas.draw_image(self.image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)
        
    def update(self):
        global forward
        
        #update position based on velocity
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        
        #update angle based on angular velocity
        self.angle += self.angle_vel
        
        #computes forward vector
        forward = angle_to_vector(self.angle)

        #accelerate when thrust is on
        
        if self.thrust:
            self.vel[0] += forward[0] * ACCELERATION
            self.vel[1] += forward[1] * ACCELERATION
        
        #ships position wraps around the screen
        for d in range(2):
            if self.pos[d] >= SCREEN_SIZE[d] or self.pos[d] <= 0:
                self.pos[d] = (self.pos[d] + self.vel[d]) % SCREEN_SIZE[d]
        
        #friction
        self.vel[0] *= (1-FRICTION)
        self.vel[1] *= (1-FRICTION)
        
    def turn_right(self):
        #increment angular velocity
        self.angle_vel += 0.1
    
    def turn_left(self):
        #decrement angular velocity
        self.angle_vel -= 0.1
    
    def thrust_on(self):
        self.thrust = True
        
        #play thrust sound
        ship_thrust_sound.play()
    
    def thrust_off(self):
        self.thrust = False
        
        #rewind thrust sound
        ship_thrust_sound.rewind()
    
    def shoot(self):
        global forward, missile_group
        missile_pos = [self.pos[0] + forward[0] * self.radius,self.pos[1] + forward[1] * self.radius] #tip of ships cannon
        missile_vel = [0,0]
        missile_vel[0] = self.vel[0] + forward[0] * MISSILE_SPEED #ships velocity + forward * c
        missile_vel[1] = self.vel[1] + forward[1] * MISSILE_SPEED
        a_missile = Sprite(missile_pos, missile_vel, 0, 0, missile_image, missile_info, missile_sound)
        missile_group.add(a_missile)
        
    def get_position(self):
        return self.pos
    
    def get_radius(self):
        return self.radius
    
    
# Sprite class
class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound = None):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        if sound:
            sound.rewind()
            sound.play()
   
    def draw(self, canvas): 
        if self.animated == True:
            current_explosion_index = (self.age % self.lifespan) // 1
            current_explosion_center = [self.image_center[0] + current_explosion_index * self.image_size[0], 
                                       self.image_center[1]]
            canvas.draw_image(self.image, current_explosion_center, self.image_size, self.pos, self.image_size) 
        else:
            canvas.draw_image(self.image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)
        
    def update(self):
        
        #update position and angle
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.angle += self.angle_vel
        
        #rock and missiles position wraps around the screen
        for d in range(2):
            if self.pos[d] >= SCREEN_SIZE[d] or self.pos[d] <= 0:
                self.pos[d] = (self.pos[d] + self.vel[d]) % SCREEN_SIZE[d]
        
        #increment age and check if Sprite should be removed
        self.age = self.age + 1
        if self.age >= self.lifespan:
            return True
        else:
            return False
        
    def get_position(self):
        return self.pos
    
    def get_radius(self):
        return self.radius
    
    def collide(self, other_object):
        if dist(self.pos, other_object.pos) < (self.radius + other_object.radius):
            return True
        else:
            return False
    
        
def draw(canvas):
    global time, started, lives, score
    
    # animate background
    time += 1
    wtime = (time / 4) % WIDTH
    center = debris_info.get_center()
    size = debris_info.get_size()
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, center, size, (wtime - WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    canvas.draw_image(debris_image, center, size, (wtime + WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    
    #draw lives and score
    canvas.draw_text("Lives", [50,50], 20, "White", "sans-serif")
    canvas.draw_text(str(lives), [50,50+20], 20, "White", "sans-serif")
    score_size = frame.get_canvas_textwidth("Score", 20, "sans-serif")
    canvas.draw_text("Score ", [WIDTH - 50 - score_size,50], 20, "White", "sans-serif")
    canvas.draw_text(str(score), [WIDTH - 50 - score_size,50+20], 20, "White", "sans-serif")           
    
    # draw and update ship
    my_ship.draw(canvas)
    my_ship.update()
    
    if not started:
        #draw splash screen
        canvas.draw_image(splash_image, splash_info.get_center(),
                          splash_info.get_size(), [WIDTH / 2, HEIGHT / 2],
                          splash_info.get_size())
    
    if started:
        #draw and update rocks
        process_sprite_group(rock_group, canvas)
    
        #draw and update missiles
        process_sprite_group(missile_group, canvas)
        
        #draw and update explosions
        process_sprite_group(explosion_group, canvas)
        
        #update lives when ship hits rock and play explosion sound
        if group_collide(rock_group, my_ship):
            lives = lives - 1
            explosion_sound.play()        
    
        #update score by 10 when missile hits rock and play explosion sound
        missile_collision = group_group_collide(missile_group, rock_group)
        if missile_collision > 0:
            score = score + missile_collision * 10
            explosion_sound.play()
        
        #play soundtrack
        soundtrack.play()
        
        #reset game when player runs out of lives
        if lives == 0:
            started = False
    
# timer handler that spawns a rock    
def rock_spawner():
    global rock_group, score
    
    random_pos = [random.randrange(0,WIDTH),random.randrange(0,HEIGHT)]
    random_vel = [random.randrange(-1,1),random.randrange(-1,1)]
    random_angle_vel = random.random() * rock_rotation * random.choice([-1, 1])
    
    #speed increase when score reaches multiple of 5
    speed_update(random_vel)
    
    #create a rock sprite
    a_rock = Sprite(random_pos, random_vel, 0, random_angle_vel, asteroid_image, asteroid_info)
    
    #ignore rocks spawned on top of ship
    if dist(my_ship.pos,a_rock.pos) >= (my_ship.radius + a_rock.radius):
        #don't spawn more then 12 rocks
        if len(rock_group) <= 12:
            rock_group.add(a_rock)

def key_down(key):
    #left and right arrow keys down turn ship left and right
    if key == simplegui.KEY_MAP['left']:
        my_ship.turn_left()
    elif key == simplegui.KEY_MAP['right']:
        my_ship.turn_right()
    elif key == simplegui.KEY_MAP['up']:
        my_ship.thrust_on()
    elif key == simplegui.KEY_MAP['space']:
        my_ship.shoot()
        
def key_up(key):
    #left and right arrow keys up stop ship from turning left and right
    if key == simplegui.KEY_MAP['left'] or key == simplegui.KEY_MAP['right']:
        my_ship.angle_vel = 0
    elif key == simplegui.KEY_MAP['up']:
        my_ship.thrust_off()

def click(pos):
    global started
    center = [WIDTH / 2, HEIGHT / 2]
    size = splash_info.get_size()
    inwidth = (center[0] - size[0] / 2) < pos[0] < (center[0] + size[0] / 2)
    inheight = (center[1] - size[1] / 2) < pos[1] < (center[1] + size[1] / 2)
    if (not started) and inwidth and inheight:
        started = True
        setup_game()
        
# initialize frame
frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)

# register handlers
frame.set_draw_handler(draw)
frame.set_keydown_handler(key_down)
frame.set_keyup_handler(key_up)
frame.set_mouseclick_handler(click)
timer = simplegui.create_timer(1000.0, rock_spawner)

#initialize variables
setup_game()
    
# get things rolling
timer.start()
frame.start()

