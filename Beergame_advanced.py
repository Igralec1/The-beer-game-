from Beergame_game_files import *

while True:
    milisec=clock.tick(FPS)
    t+=milisec/1000
    pygame.display.set_caption('t={:.2f}'.format(t))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            print('Total cost ='+str(total_cost))
            pygame.quit()
            sys.exit()
        if event.type ==pygame.KEYDOWN:
            #računanje
            advance_time(agenti)
            for x in agenti:total_cost+=x.calculate_cost()
            count+=1
            tx='Cikel = '+str(count)
            txx='Press any key to advance cycle'
            txxsurf=font.render(txx, True, WHITE)
            txsurf=font.render(tx, True, WHITE)
    #risanje
    screen.fill(BLACK)
    screen.blit(txsurf,(600,50))
    screen.blit(txxsurf,(500,650))
    for x in agenti:x.print_agent()
    pygame.display.update()
