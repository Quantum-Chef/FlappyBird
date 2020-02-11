#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  9 10:10:20 2020

@author: jerry
"""

import pygame
import neat
import random
import os
import time
pygame.font.init()

#sets the window for the game, maybe change it so we have a full screen flappy??
WIN_WIDTH = 500
WIN_HEIGHT = 800


#imports all the images
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird1.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird2.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bg.png")))

STAT_FONT = pygame.font.SysFont("comicsans",50)
class Bird:
    #gets the images
    IMGS =  BIRD_IMGS
    #sets how far the bird can tilt when flying
    MAX_ROTATION = 25
    #how fast it tilts each frame
    ROT_VEL = 20
    #how long each animation lasts, change it so the bird flaps quicker or slower
    ANIMATION_TIME = 5
    
    #initize the class
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        #when iterating through we save a version of our y value so we can compare
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]
        
    def jump(self):
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y
        
    def move(self):
        self.tick_count += 1
        #after jumping our flight arc is calculated with this, why not change the physics for fun
        d = self.vel * self.tick_count + 1.5*self.tick_count*self.tick_count
        
        #fail safes, if our velocity is too big then set a cap
        if (d>=16):
            d = 16
        #this fine tunes the number, just to make the graphics smoother, change it >:)
        if (d<0):
            d -= 2
        
        #changes our y position
        self.y = self.y+d
        
        #if we're going up then tilt the bird
        if (d<0 or self.y < self.height):
            if (self.tilt < self.MAX_ROTATION):
                #why are we just suddently at max rotation, shouldnt we slowly move up?
                self.tilt=self.MAX_ROTATION
        #tilting down
        else:
            if (self.tilt>-90):
                self.tilt -= self.ROT_VEL
                
    def draw(self,win):
        #this is to change what frame we are looking at
        self.img_count += 1
        
        #this sets what frame of flap we are at
        if (self.img_count<self.ANIMATION_TIME):
            self.img = self.IMGS[0]
        elif (self.img_count<self.ANIMATION_TIME*2):
            self.img = self.IMGS[1]
        elif (self.img_count<self.ANIMATION_TIME*3):
            self.img = self.IMGS[2]
        elif (self.img_count<self.ANIMATION_TIME*4):
            self.img = self.IMGS[1]
        elif (self.img_count == self.ANIMATION_TIME*4+1):
            self.img = self.IMGS[0]
            self.img_count = 0
        #if we are falling at a -80 deg then we dont want to be flapping    
        if (self.tilt <= -80):
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2
        
        blitRotateCenter(win, self.img, (self.x, self.y), self.tilt)
        #this sets where in the frame the birb is
        #THIS MIGHT BREAKKKKKKKK
        # rotated_image = pygame.transform.rotate(self.img,self.tilt)
        # new_rect = rotated_image.get_rect(center=self.img.get_rect(topLeft = (self.x,self.y)).center)
        # win.blit(rotated_image, new_rect.topLeft)
        
    def get_mask(self):
        return pygame.mask.from_surface(self.img)
        
class Pipe:
    GAP = 200
    VEL = 5
    
    def __init__(self,x):
        self.x = x
        self.height = 0
        self.gap = 100
        
        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG,False,True)
        self.PIPE_BOTTOM = PIPE_IMG
        
        self.passed = False
        self.set_height()
        
    def set_height(self):
        self.height = random.randrange(50,450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP
        
    def move(self):
        self.x -= self.VEL
        
    def draw(self, win):
        win.blit(self.PIPE_TOP,(self.x,self.top))
        win.blit(self.PIPE_BOTTOM,(self.x,self.bottom))
        
    def collide(self,bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))
        
        b_point = bird_mask.overlap(bottom_mask,bottom_offset)
        t_point = bird_mask.overlap(top_mask,top_offset)
        
        if t_point or b_point:
            return True
        
        return False
    
class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG
    
    def __init__(self,y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH
        
    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
            
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH
    def draw (self,win):
        win.blit(self.IMG, (self.x1,self.y))
        win.blit(self.IMG, (self.x2,self.y))
            
    
def draw_window(win,bird,pipes,base,score):
    win.blit(BG_IMG, (0,0))
    
    for pipe in pipes:
        pipe.draw(win)
        
    text = STAT_FONT.render("Score: " + str(score),1,(255,255,255))    
    win.blit(text,(WIN_WIDTH - 10 - text.get_width(),10))
    base.draw(win)
    
    bird.draw(win)    
    pygame.display.update()
    
def blitRotateCenter(surf, image, topleft, angle):
    """
    Rotate a surface and blit it to the window
    :param surf: the surface to blit to
    :param image: the image surface to rotate
    :param topLeft: the top left position of the image
    :param angle: a float value for angle
    :return: None
    """
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect.topleft)    

def main():
    bird = Bird(230,350)
    base = Base(730)
    pipes = [Pipe(700)]
    win = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))
    clock = pygame.time.Clock()
    
    score= 0
    
    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                
        bird.move()
        add_pipe = False
        rem  = []
        for pipe in pipes:
            if pipe.collide(bird):
                pass
            
            if pipe.x + pipe.PIPE_TOP.get_width()<0:
                rem.append(pipe)
                
            if not pipe.passed and pipe.x < bird.x:
                pipe.passed= True
                add_pipe = True
                
            pipe.move()
        if add_pipe:
            score += 1 
            pipes.append(Pipe(700))
            
        for r in rem:
            pipes.remove(r)
            
        if bird.y + bird.img.get_height() >= 730:
            pass
        base.move()
        draw_window(win, bird,pipes,base,score)
    pygame.quit()
    
main()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
        