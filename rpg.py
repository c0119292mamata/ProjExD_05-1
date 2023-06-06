import math
import random
import sys
import pygame as pg
import time
from pygame.locals import *

# global変数
WIDTH = 1600    # ウィンドウの横幅
HIGHT = 900     # ウィンドウの縦幅
txt_origin = ["攻撃","防御","魔法","回復","調教","逃走"]    # 勇者の行動選択肢のリスト
LEVEL = 1
HP = 100         # 勇者のHP
MP = 10         # 勇者のMP
ENE_HP = 200     # 敵スライムのHP
ENE_MP = 0
ATK = 10
MJC = 30
DEF = 10
TAM = 5
TAME_POINT = 20
ENE_ATK = 10
TAME = 0

class Text:
    def __init__(self,syo):
        self.text = syo
    
    def draw(self, scr, text_color, x, y):
        font = pg.font.SysFont("hg正楷書体pro", 100)
        text_surface = font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=(x,y))
        scr.blit(text_surface, text_rect)

class Button:
    """
    勇者の行動選択ボタンに関するクラス
    """
    def __init__(self, x, y, width, height, color, hover_color, text, text_color, action, num, text2, hp_mp, ene):
        """
        初期化メソッド
        x: ボタンのx座標
        y: ボタンのy座標
        width: ボタンの横幅
        height: ボタンの縦幅
        color: ボタンの色
        hover_color: マウスカーソルがボタンの上にある時のボタンの色
        text: 行動選択肢の文字
        text_color: 文字の色
        action: action関数
        num: index(0:攻撃, 1:防御, 2:魔法, 3:回復, 4:調教, 5:逃走)
        """
        self.rect = pg.Rect(x, y, width, height)    # rectを四角形を描画するsurfaceで初期化
        self.color = color
        self.hover_color = hover_color
        self.text = text
        self.text_color = text_color
        self.action = action
        self.num = num
        self.text2 = text2
        self.hp_mp = hp_mp
        self.ene = ene

    def draw(self,scr):
        """
        ボタンを描画するメソッド
        scr: display surface
        """
        pg.draw.rect(scr, self.color, self.rect)    # ボタンとなる四角形を描画
        font = pg.font.SysFont("hg正楷書体pro", 50)  # フォント指定
        text_surface = font.render(self.text, True, self.text_color)    # テキストsurface
        text_rect = text_surface.get_rect(center=self.rect.center)      # テキストの中心値指定
        scr.blit(text_surface, text_rect)   # ボタン描画

    def handle_event(self, event, scr, fight_img, win2, exps):
        """
        勇者の行動の切り替えメソッド
        event: event
        """
        # マウスボタンが押されたかつ左クリック(event.button == 1)の場合
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            # マウスの座標がボタンの範囲内にあれば
            if self.rect.collidepoint(event.pos):
                act = self.action(self.num, self.text2, self.hp_mp, self.ene, scr, fight_img, win2, exps)   # action関数を実行
                return act
            
            
class Explosion(pg.sprite.Sprite):
    """
    爆発に関するクラス
    """
    def __init__(self, life: int):
        """
        爆弾が爆発するエフェクトを生成する
        引数1 obj：爆発するBombまたは敵機インスタンス
        引数2 life：爆発時間
        """
        super().__init__()
        img = pg.image.load("ex04/fig/explosion.gif")
        img = pg.transform.scale(img, (200, 200))
        self.imgs = [img, pg.transform.flip(img, 1, 1)]
        self.image = self.imgs[0]
        self.rect = self.image.get_rect(center=(900,600))
        self.life = life

    def update(self):
        """
        爆発時間を1減算した爆発経過時間_lifeに応じて爆発画像を切り替えることで
        爆発エフェクトを表現する
        """
        self.life -= 1
        self.image = self.imgs[self.life//10%2]
        if self.life < 0:
            self.kill()

            
            
        
class P_HP_MP:
    def __init__(self,turn):
        self.level = LEVEL
        self.max_hp = HP
        self.max_mp = MP
        self.hp = HP
        self.mp = MP
        self.atk = ATK
        self.defe = DEF
        self.mjc = MJC
        self.turn = turn
        self.font = pg.font.SysFont("hg正楷書体pro", 50)
        self.pl_hp = self.font.render(f"Lv:{self.level} HP:{self.hp} MP:{self.mp}", True, (255,255,255))
        self.PL_action = ""
        
    def PL(self,hp,mp):
        self.hp=hp
        self.mp=mp
        self.pl_hp = self.font.render(f"Lv:{self.level} HP:{self.hp} MP:{self.mp}", True, (255,255,255))
        
    def LEVEL(self):
        self.level += 1
        self.max_hp += 10
        self.max_mp += 10
        self.hp=self.max_hp
        self.mp=self.max_mp
        self.pl_hp = self.font.render(f"Lv:{self.level} HP:{self.hp} MP:{self.mp}", True, (255,255,255))
        
        
class enemy:
    def __init__(self,turn):
        self.turn = turn
        self.max_hp = ENE_HP
        self.hp = ENE_HP
        self.atk = ENE_ATK
        self.font = pg.font.SysFont("hg正楷書体pro", 50)
        self.ene_hp = self.font.render(f"HP:{self.hp}", True, (255,255,255))
    
    def ENE(self,hp):
        self.hp = hp
        self.ene_hp = self.font.render(f"HP:{self.hp}", True, (255,255,255))
        

def action(i, text:Text, hp_mp:P_HP_MP, e_inf:enemy, screen, fight_img, win2, exps):
    """
    勇者の行動に関する関数
    i: index (0:攻撃, 1:防御, 2:魔法, 3:回復, 4:調教, 5:逃走)
    """
    global HP, ENE_HP, TAME, is_mouse_pressed

    
    hp = int(hp_mp.hp)
    mp = int(hp_mp.mp)
    atk = int(hp_mp.atk)
    mjc = int(hp_mp.mjc)
    ene_hp = int(e_inf.hp)
    is_mouse_pressed = False

    if hp_mp.turn==1:    
        if txt_origin[i]=="攻撃":   # 攻撃ボタンが押されたら
            ene_hp -=  atk          # スライムのHPを減らす
            if ene_hp <= 0:         # スライムのHPが0以下になったら
                ene_hp = 0          # スライムのHPを0にする
            text.text = f"{atk}ダメージ与えた"
            e_inf.ENE(ene_hp)
            hp_mp.turn = 0
            toka=0
            # 攻撃エフェクト
            for j in range(25):
                toka += 10
                if toka > 255:
                    toka = 0
                fight_img.set_alpha(toka)
                screen.blit(fight_img,[200, 100])
                pg.display.update()
            time.sleep(0.1)

        if txt_origin[i]=="防御":
            text.text = "盾を構えた"
            hp_mp.turn = 0

        #調教：使用時の敵HPによって成功率が変わる
        if txt_origin[i] == "調教":
            m = random.randint(0, e_inf.max_hp)
            #i = 0  #絶対成功する
            if m <= (e_inf.max_hp - ene_hp):
                print("ていむ成功！！！")
                TAME = 1
            else:
                TAME = 2
            hp_mp.turn = 0

        if txt_origin[i]=="魔法":
            if mp>0:
                ene_hp -= mjc
                if ene_hp <= 0:         # スライムのHPが0以下になったら
                    ene_hp = 0      
                mp-=1
                hp_mp.turn = 0
                text.text = f"{mjc}ダメージ与えた"
            else:
                text.text = "MPが足りません"
            e_inf.ENE(ene_hp)
            hp_mp.PL(hp,mp)
            exps.add(Explosion(100))
            exps.update()
            exps.draw(screen)
            pg.display.update()
            time.sleep(1)

        if txt_origin[i]=="回復":
            if hp<HP and mp>0:
                nokori=HP-hp
                if nokori>MJC:
                    hp+=MJC
                else:
                    hp+=nokori
                mp-=1
                if hp>=HP:
                    hp=HP
                hp_mp.PL(hp,mp)
                text.text = f"{nokori}回復した"
                hp_mp.turn = 0
            elif mp<1:
                text.text = "MPが足りません"
            elif hp>=50:
                text.text = "体力が満タンです"
                
        if txt_origin[i]=="逃走":
            text.text="勇者は逃げ出した"
            screen.blit(win2,[50,50])
            text.draw(screen, (255,255,255), WIDTH/2,150)
            pg.display.update()
            time.sleep(3)
            sys.exit()
            
    if hp_mp.turn==0:
        hp_mp.PL_action = txt_origin[i]

def ENE_action(PL_action,hp_mp:P_HP_MP,text:Text, screen, ene_img, attack_slime):
    hp = int(hp_mp.hp)
    mp = int(hp_mp.mp)
    current_time = time.time() #ここからワイの実装
    attack_interval = 5 #攻撃の間隔
    last_attack_time = 0 #攻撃時刻
    keika_time = current_time - last_attack_time
    for k in range(30):
        if  keika_time >= attack_interval: #スライムの攻撃
            attack_x = random.randint(0, WIDTH - ene_img.get_width())
            attack_y = random.randint(0, HIGHT - ene_img.get_width())
            last_attack_time = current_time
            time.sleep(0.01) #攻撃の速さ
        screen.blit(attack_slime,[attack_x,attack_y]) #ここもワイ
        pg.display.update()
    if PL_action=="防御":
        damege = ENE_ATK - DEF
        hp -= damege
        hp_mp.PL(hp,mp)
    else:
        damege = ENE_ATK
        hp -= damege
        hp_mp.PL(hp,mp)
    text.text=f"{damege}ダメージくらった"
    hp_mp.turn=1
        
        
def level_up(p_inf:P_HP_MP, text:Text, screen, win2):
    p_inf.LEVEL()
    text.text = "レベルが1上がった"
    screen.blit(win2,[50,50])
    text.draw(screen, (255,255,255), WIDTH/2,150)
    
    

def title():
    pg.display.set_caption("簡易型ゲーム")
    screen = pg.display.set_mode((1600, 900))
    bg_img = pg.image.load("ex05/fig/back_title.png")
    bg_img = pg.transform.scale(bg_img,(1600,900))
    rect = pg.Rect(700, 600, 200, 80)
    bg_rct = pg.Rect(0, 0, 1600, 900)
    font = pg.font.SysFont("hg正楷書体pro", 50)  # フォント指定
    font2 = pg.font.SysFont("hg正楷書体pro", 150)  # フォント指定
    text_surface = font.render("始める", True, (255,0,0))    # テキストsurface
    text_surface2 = font2.render("簡易式RPGゲーム", True, (0,0,0))    # テキストsurface
    text_rect = text_surface.get_rect(center=rect.center)      # テキストの中心値指定
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: return    # ×ボタンが押されたらプログラム終了
            
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if rect.collidepoint(event.pos):
                    return
        
        pg.draw.rect(screen, (200,200,200), bg_rct)
        screen.blit(bg_img,[0, 0])
        pg.draw.rect(screen, (100,100,100), rect)    # ボタンとなる四角形を描画
        screen.blit(text_surface, text_rect)
        screen.blit(text_surface2,[200,200])
        pg.display.update()     
        
        
def main():
    """
    main関数
    """
    global TAME
    turn=1
    bg_image = "./ex05/fig/back.png"
    pg.display.set_caption("RPG of くそげー")   # ウィンドウの名前
    screen = pg.display.set_mode((WIDTH, HIGHT))    # 1600x900のdisplay surface
    clock  = pg.time.Clock()                        # 時間
    # surface
    # 背景
    bg_img = pg.image.load(bg_image)
    bg_img = pg.transform.scale(bg_img,(WIDTH,HIGHT))
    # 敵スライム
    ene_img = pg.image.load("./ex05/fig/ene.png")
    ene_rct = ene_img.get_rect()
    attack_slime = pg.image.load("./ex05/fig/momoka.png")
    attack_slime = pg.transform.scale(attack_slime, (300, 200))
    # 攻撃エフェクト
    fight_img = pg.image.load("./ex05/fig/fight_effect.png")
    fight_img = pg.transform.scale(fight_img,(WIDTH,HIGHT))
    # テキストボックス
    win = pg.image.load("./ex05/fig/win.png")
    win = pg.transform.scale(win,(WIDTH/4,HIGHT/2))
    win2 = pg.transform.scale(win,(WIDTH-100,HIGHT/4))
    # フォント
    font1 = pg.font.SysFont("hg正楷書体pro", 100)
    font3 = pg.font.SysFont("None",200)
    # テキスト
    syo="野生のスライムが現れた"
    text = Text(syo)
    fight_txt = "スライムを倒した！"
    die_text = "You died"
    txt = []    # 選択ボタンを描画するsurfaceのリスト
    text_surface = P_HP_MP(turn)
    ene = enemy(turn)
    # 勇者の行動選択ボタンを描画するsurfaceを作成しリストtxtに追加
    exps = pg.sprite.Group()
    
    font3 = pg.font.SysFont(None, 200)
    die_text = "You died" # 死亡メッセージ

    for i,tx in enumerate(txt_origin):
        # インスタンス化
        if i%2==0:
            button = Button(125, 500+(i//2)*100, 100, 50, 
                            (50,50,50), (0,0,0), tx, 
                            (255,255,255), action, 
                            i, text, text_surface, ene)
        else:
            button = Button(275, 500+(i//2)*100, 100, 50, 
                            (50,50,50), (0,0,0), tx, 
                            (255,255,255), action, 
                            i, text, text_surface, ene)
        txt.append(button)

    # 繰り返し文    
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: return    # ×ボタンが押されたらプログラム終了

            for button in txt:
                button.handle_event(event, screen, fight_img, win2, exps)

                #変更箇所
                if  TAME == 1:
                    text.text = "ていむ成功！！"
                elif TAME == 2:
                    text.text = "ていむ失敗..."
                    TAME = 0

        screen.blit(bg_img,[0, 0])      # 背景描画
        screen.blit(win,[50, 400])      # テキストボックス描画
        screen.blit(win2,[50, 50])      # 行動選択のテキストボックス描画


        x = 200
        for chr in text.text:
            rendered_text = font1.render(chr, True, (255, 255, 255))
            text_width = rendered_text.get_width()
            screen.blit(rendered_text,[x, 100])
            x += text_width
        for i in txt:
            i.draw(screen)  # ボタン描画
            
        if  ene.hp <= 0:
            text.text = fight_txt
            text_surface.turn=2
            ene.turn=2
            screen.blit(win2,[50,50])
            screen.blit(ene.ene_hp,[WIDTH/2-ene_rct.width/2+225, HIGHT/2-50])    # 敵スライムのHP表示
            text.draw(screen, (255,255,255), WIDTH/2,150)
            pg.display.update()
            time.sleep(1)
            level_up(text_surface, text,screen, win2)

        if ene.turn!=2:
            screen.blit(ene_img,[WIDTH/2-ene_rct.width/2+100, HIGHT/2]) # 敵スライム描画
            screen.blit(ene.ene_hp,[WIDTH/2-ene_rct.width/2+225, HIGHT/2-50])    # 敵スライムのHP表示
        screen.blit(text_surface.pl_hp,[100, 350])   # 勇者のHP,MP表示
        pg.display.update()     # ディスプレイのアップデート
        clock.tick(100)         # 時間

        if text_surface.hp<=0: # HPが0になったら
            die_text2 = font3.render(die_text, True, (255, 0, 0))
            screen.blit(die_text2, (600, 450)) # 600, 450の位置に赤色で"You died"を表示する
            pg.display.update()
            time.sleep(3)
            pg.quit()

        if ene.hp <= 0 or TAME == True:
            pg.display.update()
            time.sleep(3)
            sys.exit()
        
        if text_surface.turn==0:
            time.sleep(1)
            text.text="相手の攻撃"
            screen.blit(win2,[50,50])
            text.draw(screen, (255,255,255), WIDTH/2,150)
            pg.display.update()
            time.sleep(1)
            PL_action=text_surface.PL_action
            ENE_action(PL_action,text_surface,text,screen,ene_img,attack_slime)
            

if __name__ == "__main__":
    pg.init()
    title()
    main()
    pg.quit()
    sys.exit()