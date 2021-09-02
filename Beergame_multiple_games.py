import pygame,sys
import numpy as np
from barve import *
import time
import random as rnd
import math
#nastavitve
Retailer_lagg=2
WholeSeller_lagg=2
Distributer_lagg=2
Manufacturer_lagg=2
class Game:
    def __init__(self,Retailer_lagg,WholeSeller_lagg,Distributer_lagg,Manufacturer_lagg):
        self.Retailer=Agent((1010,200),Retailer_lagg-1,'Retailer')
        self.WholeSeller=Agent((710,200),WholeSeller_lagg-1,'WholeSeller')
        self.Distributer=Agent((410,200),Distributer_lagg-1,'Distributer')
        self.Manufacturer=Agent((110,200),Manufacturer_lagg-1,'Manufacturer')
        self.agenti=[self.Retailer,self.WholeSeller,self.Distributer,self.Manufacturer]
    def advance_time(self):
        demand=round(np.random.exponential(10))
        shipment=self.Manufacturer.order_new_stock
        self.Manufacturer.recieve_shipment(shipment)
        shipment=self.Manufacturer.send_shipment(self.Distributer.order_new_stock)
        self.Distributer.recieve_shipment(shipment)
        shipment=self.Distributer.send_shipment(self.WholeSeller.order_new_stock)
        self.WholeSeller.recieve_shipment(shipment)
        shipment=self.WholeSeller.send_shipment(self.Retailer.order_new_stock)
        self.Retailer.recieve_shipment(shipment)
        shipment=self.Retailer.send_shipment(demand)
        for x in self.agenti:x.predict_order()
        print('Demand=',demand)


class Agent:
    def __init__(self,pos,lagg_time,type):
        self.brain=self.brain()
        self.pos=[pos[0],pos[1]]
        self.stock=10
        self.backlog=0
        self.aux_stock_counter=10
        self.order_new_stock=0
        self.lagg_buffer=[0]*lagg_time
        self.type=type
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
        if len(self.lagg_buffer)==0:buff=0
        else: buff=self.lagg_buffer[0]
        inputs=[self.stock,self.backlog,buff]
        self.order_new_stock=self.brain.brain_run(inputs)
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
    class brain:
        def __init__(self):
            self.nrinputs=3
            self.nroutputs=1
            #net_struct=[nr.layers,nr.nodes in layer1,nr.nodes in layer 2,...]
            self.net_struct=[2,3,2]
            self.nodes=np.zeros(self.net_struct[0])
            #ni končano
            self.nrnodes=3
            self.nodes=[[0 for i in range(self.net_struct[j+1])] for j in range(self.net_struct[0])]
            self.weithinp=np.zeros((self.net_struct[1],self.nrinputs))
            self.weithmid=np.zeros((self.net_struct[0]-1,self.nrnodes,self.nrnodes))
            self.weithout=np.zeros((self.nroutputs,self.nrnodes))
            self.biasin=np.zeros((self.nrnodes))
            self.biasmid=np.zeros((self.net_struct[0]-1,self.nrnodes))
            self.biasout=np.zeros((self.nroutputs))
        def init_weith_and_bias(self):
            for x in range(self.net_struct[1]):
                self.biasin[x]=rnd.uniform(-1,1)
                for y in range(self.nrinputs):
                    self.weithinp[x][y]=rnd.uniform(-1,1)
            for x in range(self.net_struct[0]-1):
                for y in range(self.net_struct[x+2]):
                    self.biasmid[x][y]=rnd.uniform(-1,1)
                    for z in range(self.net_struct[x+1]):
                        self.weithmid[x][y][z]=rnd.uniform(-1,1)
            for x in range(self.nroutputs):
                self.biasout[x]=rnd.uniform(-1,1)
                for y in range(self.net_struct[-1]):
                    self.weithout[x][y]=rnd.uniform(-1,1)
        def mutate(self,l,r):
            for x in range(self.net_struct[1]):
                self.biasin[x]+=rnd.uniform(l,r)
                for y in range(self.nrinputs):
                    self.weithinp[x][y]+=rnd.uniform(l,r)
            for x in range(self.net_struct[0]-1):
                for y in range(self.net_struct[x+2]):
                    self.biasmid[x][y]+=rnd.uniform(l,r)
                    for z in range(self.net_struct[x+1]):
                        self.weithmid[x][y][z]+=rnd.uniform(l,r)
            for x in range(self.nroutputs):
                self.biasout[x]+=rnd.uniform(l,r)
                for y in range(self.net_struct[-1]):
                    self.weithout[x][y]+=rnd.uniform(l,r)
        def sigma(self,x):
            t=1/(1+math.exp(-x))
            if t<0.001:
                t=0
            elif t>0.995:t=1
            return t
        def brain_show(self,imm,d,h,inp,output):
            #inputs
            for x in range(self.nrinputs):
                if int(inp[x])<=255:r=int(inp[x])
                else:r=255
                b=255-r
                pygame.draw.circle(imm,(r,b,r),(int(d/2),int(h/2)-50+23*x),10)
            #nodes
            for x in range(self.net_struct[0]):
                for y in range(self.net_struct[x+1]):
                    pygame.draw.circle(imm,(int(self.nodes[x][y]*255),int(255-self.nodes[x][y]*255),int(self.nodes[x][y]*255)),(int(d/2)+(x+1)*25,int(h/2)-40+23*y),10)
            #output
            for x in range(self.nroutputs):
                if output<0:
                    pygame.draw.circle(imm,(255,abs(int(output*80)),abs(int(output*50))),(int(d/2)+(self.net_struct[0]+1)*25,int(h/2)-28+23*x),10)
                else:
                    pygame.draw.circle(imm,(255,255-abs(int(output*80)),abs(int(output*50))),(int(d/2)+(self.net_struct[0]+1)*25,int(h/2)-28+23*x),10)
        def brain_run(self,inp):
            for x in range(self.net_struct[1]):
                suma=0
                for y in range(self.nrinputs):
                    suma+=inp[y]*self.weithinp[x][y]
                suma+=self.biasin[x]
                if suma>100:suma=100
                elif suma<-100:suma=-100
                self.nodes[0][x]=self.sigma(suma)
            for x in range(self.net_struct[0]-1):
                for y  in range(self.net_struct[x+2]):
                    suma=0
                    for z  in range(self.net_struct[x+1]):
                        suma+=self.nodes[x][z]*self.weithmid[x][y][z]
                    suma+=self.biasmid[x][y]
                    if suma>100:suma=100
                    elif suma<-100:suma=-100
                    self.nodes[x+1][y]=self.sigma(suma)
            for x in range(self.nroutputs):
                suma=0
                for y in range(self.net_struct[-1]):
                    suma+=self.nodes[-1][y]*self.weithout[x][y]
                suma+=self.biasout[x]
                if suma>100:suma=100
                elif suma<-100:suma=-100
                output=round(np.power(self.sigma(suma),-1))

            return output

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
font = pygame.font.Font('freesansbold.ttf',20)
tx='Cikel = '+str(count)
txsurf=font.render(tx, True, WHITE)
txx='Press any key to advance cycle'
txxsurf=font.render(txx, True, WHITE)

igra=Game(Retailer_lagg,WholeSeller_lagg,Distributer_lagg,Manufacturer_lagg)
for x in igra.agenti:x.brain.init_weith_and_bias()
for x in igra.agenti:x.predict_order()
while True:
    milisec=clock.tick(FPS)
    t+=milisec/1000
    pygame.display.set_caption('t={:.2f}'.format(t))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type ==pygame.KEYDOWN:
            #računanje
            igra.advance_time()
            count+=1
            tx='Cikel = '+str(count)
            txx='Press any key to advance cycle'
            txxsurf=font.render(txx, True, WHITE)
            txsurf=font.render(tx, True, WHITE)
    #risanje
    screen.fill(BLACK)
    screen.blit(txsurf,(600,50))
    screen.blit(txxsurf,(500,650))
    for x in igra.agenti:x.print_agent()
    pygame.display.update()
