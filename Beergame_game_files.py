import pygame,sys
import numpy as np
from barve import *
import time
#nastavitve
Retailer_lagg=1
WholeSeller_lagg=1
Distributer_lagg=1
Manufacturer_lagg=1
class Agent:
    def __init__(self,pos,lagg_time,type):
        self.pos=[pos[0],pos[1]]
        self.stock=10
        self.backlog=0
        self.aux_stock_counter=10
        self.order_new_stock=0
        self.lagg_buffer=[0]*lagg_time
        self.type=type
        self.cumulative_cost=0
        self.backlog_cost=10
        self.stock_cost=5
    def recieve_shipment(self,shipment):
        # prejmi dobavo
        self.lagg_buffer.append(shipment)
        self.aux_stock_counter+=self.lagg_buffer[0]
        self.lagg_buffer.pop(0)
    def send_shipment(self,order):
        if order>self.stock:
            shipment=self.stock
        else:shipment=order
        self.aux_stock_counter-=order
        if self.aux_stock_counter<0:
            self.backlog=self.aux_stock_counter*(-1)
            self.stock=0
        else:
            self.stock=self.aux_stock_counter
            self.backlog=0
        return shipment
    def predict_order(self):
        self.order_new_stock=round(self.stock+self.backlog)
    def print_agent(self):
        text1='Stock='+str(self.stock)
        text2='Backlog='+str(self.backlog)
        text3='New order='+str(self.order_new_stock)
        TextSurf1=font.render(text1, True, WHITE)
        TextSurf3=font.render(text3, True, WHITE)
        TextSurf2=font.render(text2, True, WHITE)
        TextSurf4=font.render(self.type, True, WHITE)
        screen.blit(surf,self.pos)
        screen.blit(TextSurf1,(self.pos[0]+10,self.pos[1]+10))
        screen.blit(TextSurf2,(self.pos[0]+10,self.pos[1]+100))
        screen.blit(TextSurf3,(self.pos[0]+10,self.pos[1]+50))
        screen.blit(TextSurf4,(self.pos[0],self.pos[1]-20))
    def calculate_cost(self):
        self.cumulative_cost+=self.backlog_cost+self.stock_cost
        return self.cumulative_cost


def advance_time(agenti):
    demand=round(np.random.exponential(10))
    shipment=Manufacturer.order_new_stock
    Manufacturer.recieve_shipment(shipment)
    shipment=Manufacturer.send_shipment(Distributer.order_new_stock)
    Distributer.recieve_shipment(shipment)
    shipment=Distributer.send_shipment(WholeSeller.order_new_stock)
    WholeSeller.recieve_shipment(shipment)
    shipment=WholeSeller.send_shipment(Retailer.order_new_stock)
    Retailer.recieve_shipment(shipment)
    shipment=Retailer.send_shipment(demand)
    for x in agenti:x.predict_order()
    print('Demand=',demand)

pygame.init()
t=0
count=0
dolzina=1280
visina= 720
FPS = 30
clock = pygame.time.Clock()
screen = pygame.display.set_mode((dolzina,visina))
rect_w,rect_h=150,150
surf=pygame.Surface((rect_h,rect_w))
surf.fill(RED)
total_cost=0
font = pygame.font.Font('freesansbold.ttf',20)
tx='Cikel = '+str(count)
txsurf=font.render(tx, True, WHITE)
txx='Press any key to advance cycle'
txxsurf=font.render(txx, True, WHITE)
Retailer=Agent((1010,200),Retailer_lagg-1,'Retailer')
WholeSeller=Agent((710,200),WholeSeller_lagg-1,'WholeSeller')
Distributer=Agent((410,200),Distributer_lagg-1,'Distributer')
Manufacturer=Agent((110,200),Manufacturer_lagg-1,'Manufacturer')
agenti=[Manufacturer,Distributer,WholeSeller,Retailer]
for x in agenti:x.predict_order()
