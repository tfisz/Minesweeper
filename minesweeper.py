from map import*
from tkinter import messagebox
from tkinter import *
import time
import threading

SZEROKOSC: int = 16
WYSOKOSC: int = 16
LICZBA_MIN: int = 40


class Minesweeper:
    def __init__(self, root):
        with open("statystyki.txt", 'r') as statystyki:
            self.lista_wynikow = [int(i) for i in statystyki] # wygrane / przegrane / czas

        self.root = root
        root.title("Minesweeper!")

        menu = Menu(root)
        root.config(menu=menu)
        game_menu = Menu(menu)
        menu.add_cascade(label="Gra", menu=game_menu)
        game_menu.add_command(label="Nowa", command=self.reset)
        game_menu.add_command(label="Statystyki", command=self.stats)
        game_menu.add_command(label="Wyjdź", command=root.destroy)

        self.mapa = Mapa(WYSOKOSC, SZEROKOSC)
        self.mapa.wyznacz_mape(WYSOKOSC, SZEROKOSC, LICZBA_MIN)

        frame = Frame(root)
        frame.pack()

        self.zakryte = PhotoImage(file="zakryte.png")
        self.puste = PhotoImage(file="puste.png")
        self.bomba = PhotoImage(file="bomba.png")
        self.flaga = PhotoImage(file="flaga.png")
        self.brak_bomby = PhotoImage(file="brak_bomby.png")
        self.numery = []
        for x in range(1, 9):
            self.numery.append(PhotoImage(file=str(x) + ".png"))

        self.buttons = dict({})
        self.odkrytePola = 0
        self.postawioneFlagi = 0
        self.czyRozpoczeta = FALSE
        self.Czas = 0
        self.poczatkowyCzas = int(time.clock())
        self.odwiedzone = []

        x_coord, y_coord = 0, 0
        for i in range(WYSOKOSC*SZEROKOSC):

            if self.mapa.dane[x_coord][y_coord].sasiedzi == 9:
                mina = 1
            else:
                mina = 0

            # ustawiamy grafikę
            gfx = self.zakryte

            # 0 = Button widget
            # 1 = jeśli mina t/n (1/0)
            # 2 = stan (0 = niekliknięty, 1 = kliknięty, 2 = oflagowany)
            # 3 = id buttona
            # 4 = [x, y] położenie na planszy
            # 5 = sąsiedztwo
            self.buttons[i] = [Button(frame, image=gfx),
                               mina,
                               0,
                               i,
                               [x_coord, y_coord],
                               self.mapa.dane[x_coord][y_coord].sasiedzi]
            self.buttons[i][0].bind('<Button-1>', self.lclicked_wrapper(i))
            self.buttons[i][0].bind('<Button-3>', self.rclicked_wrapper(i))
            self.buttons[i][0].bind('<Double-Button-1>', self.dclicked_wrapper(i))
            # kalkulacja położenia
            x_coord += 1
            if x_coord == SZEROKOSC:
                x_coord = 0
                y_coord += 1

        # umieszczamy buttony na layoucie
        for key in self.buttons:
            self.buttons[key][0].grid(row=self.buttons[key][4][1], column=self.buttons[key][4][0])

        # dodajemy timer i licznik flag
        self.label2 = Label(frame, text="Czas: 0")
        self.label2.grid(row=WYSOKOSC, column=0, columnspan=3)

        self.label3 = Label(frame, text="Pozostało: " + str(LICZBA_MIN-self.postawioneFlagi))
        self.label3.grid(row=WYSOKOSC, column=SZEROKOSC-3, columnspan=3)

    def lclicked_wrapper(self, key):
        return lambda Button: self.lclicked(self.buttons[key])

    def rclicked_wrapper(self, key):
        return lambda Button: self.rclicked(self.buttons[key])

    def dclicked_wrapper(self, key):
        return lambda Button: self.dclicked(self.buttons[key])

    def lclicked(self, button_data):
        if button_data[1] == 1:  # jeśli mina
            # pokaż wszystkie miny
            for key in self.buttons:
                if self.buttons[key][1] != 1 and self.buttons[key][2] == 2:
                    self.buttons[key][0].config(image=self.brak_bomby)
                if self.buttons[key][1] == 1 and self.buttons[key][2] != 2:
                    self.buttons[key][0].config(image=self.bomba)
            # koniec gry
            self.przegrana()
        elif button_data[1] == 0 and button_data[2] == 0:
            # zmień ikonę
            if self.czyRozpoczeta == FALSE:
                self.czyRozpoczeta = TRUE
                t = threading.Thread(target=self.timer)
                t.start()

            if button_data[5] == 0:
                self.czysc_puste(button_data[3], TRUE)
            else:
                button_data[0].config(image=self.numery[button_data[5] - 1])
                button_data[2] = 1
                self.odkrytePola += 1

            if self.odkrytePola == WYSOKOSC*SZEROKOSC - LICZBA_MIN:
                self.wygrana()

    def rclicked(self, button_data):
        # jeśli niekliknięte, stawiamy flagę
        if button_data[2] == 0:
            button_data[0].config(image=self.flaga)
            button_data[2] = 2
            button_data[0].unbind('<Button-1>')

            self.postawioneFlagi += 1
            self.update_flags()
        # jeśli oflagowane, zabieramy flagę
        elif button_data[2] == 2:
            button_data[0].config(image=self.zakryte)
            button_data[2] = 0
            button_data[0].bind('<Button-1>', self.lclicked_wrapper(button_data[3]))

            self.postawioneFlagi -= 1
            self.update_flags()

    def dclicked(self, button_data):  # funkcja, która po podwójnym klkiknięciu sprawdza czy liczba otaczających flag
                                      # zgadza się z grafiką po czym odkrywa otoczenie pola
        if button_data[2] == 1 and button_data[5] != 0:
            x_coord, y_coord = button_data[4]
            flag_counter = 0
            for key in self.buttons:
                if self.buttons[key][4] == [x_coord - 1, y_coord - 1] and self.buttons[key][2] == 2:
                    flag_counter += 1
                if self.buttons[key][4] == [x_coord, y_coord - 1] and self.buttons[key][2] == 2:
                    flag_counter += 1
                if self.buttons[key][4] == [x_coord + 1, y_coord - 1] and self.buttons[key][2] == 2:
                    flag_counter += 1
                if self.buttons[key][4] == [x_coord - 1, y_coord] and self.buttons[key][2] == 2:
                    flag_counter += 1
                if self.buttons[key][4] == [x_coord + 1, y_coord] and self.buttons[key][2] == 2:
                    flag_counter += 1
                if self.buttons[key][4] == [x_coord - 1, y_coord + 1] and self.buttons[key][2] == 2:
                    flag_counter += 1
                if self.buttons[key][4] == [x_coord, y_coord + 1] and self.buttons[key][2] == 2:
                    flag_counter += 1
                if self.buttons[key][4] == [x_coord + 1, y_coord + 1] and self.buttons[key][2] == 2:
                    flag_counter += 1

            if flag_counter == button_data[5]:
                key = button_data[3]
                if x_coord > 0 and y_coord > 0 and self.buttons[key-SZEROKOSC-1][2] == 0:
                    self.lclicked(self.buttons[key-SZEROKOSC-1])
                if y_coord > 0 and self.buttons[key-SZEROKOSC][2] == 0:
                    self.lclicked(self.buttons[key - SZEROKOSC])
                if x_coord < SZEROKOSC-1 and y_coord > 0 and self.buttons[key-SZEROKOSC+1][2] == 0:
                    self.lclicked(self.buttons[key - SZEROKOSC+1])
                if x_coord > 0 and self.buttons[key-1][2] == 0:
                    self.lclicked(self.buttons[key - 1])
                if x_coord < SZEROKOSC-1 and self.buttons[key+1][2] == 0:
                    self.lclicked(self.buttons[key + 1])
                if x_coord > 0 and y_coord < WYSOKOSC-1 and self.buttons[key+SZEROKOSC-1][2] == 0:
                    self.lclicked(self.buttons[key + SZEROKOSC - 1])
                if y_coord < WYSOKOSC-1 and self.buttons[key+SZEROKOSC][2] == 0:
                    self.lclicked(self.buttons[key + SZEROKOSC])
                if x_coord < SZEROKOSC-1 and y_coord < WYSOKOSC-1 and self.buttons[key+SZEROKOSC+1][2] == 0:
                    self.lclicked(self.buttons[key + SZEROKOSC + 1])

    def czysc_puste(self, key, allowedClear):  # funkcja która w przypadku gdy natrafimy na 0 odkrywa całe jego otoczenie
        if self.buttons[key][2] == 0 and allowedClear == TRUE and self.buttons[key][1] == 0 and key not in self.odwiedzone:

            self.odwiedzone.append(key)
            self.buttons[key][2] = 1
            if self.buttons[key][5] == 0:
                self.buttons[key][0].config(image = self.puste)
            else:
                self.buttons[key][0].config(image=self.numery[self.buttons[key][5] - 1])

            self.odkrytePola += 1

            if self.odkrytePola == WYSOKOSC*SZEROKOSC-LICZBA_MIN:
                self.wygrana()

            if self.buttons[key][5] == 0:
                allowedClear = TRUE
            else:
                allowedClear = FALSE

            x_coord, y_coord = self.buttons[key][4]
            if y_coord > 0 and x_coord > 0:
                self.czysc_puste(key-SZEROKOSC-1, allowedClear)
            if y_coord > 0:
                self.czysc_puste(key-SZEROKOSC, allowedClear)
            if y_coord > 0 and x_coord < SZEROKOSC-1:
                self.czysc_puste(key-SZEROKOSC+1, allowedClear)
            if x_coord > 0:
                self.czysc_puste(key-1, allowedClear)
            if x_coord < SZEROKOSC-1:
                self.czysc_puste(key+1, allowedClear)
            if y_coord < WYSOKOSC-1 and x_coord>0:
                self.czysc_puste(key+SZEROKOSC-1, allowedClear)
            if y_coord < WYSOKOSC-1:
                self.czysc_puste(key+SZEROKOSC, allowedClear)
            if y_coord < WYSOKOSC-1 and x_coord<SZEROKOSC-1:
                self.czysc_puste(key+SZEROKOSC+1, allowedClear)

    def przegrana(self):
        self.czyRozpoczeta = FALSE
        self.lista_wynikow[1] += 1
        for key in self.buttons:
            self.buttons[key][0].unbind('<Button-1>')
            self.buttons[key][0].unbind('<Button-3>')
            self.buttons[key][0].unbind('<Double-Button-1>')
        messagebox.showinfo("Koniec gry", "Przegrałeś!"
                                          "\nLiczba wygranych: "+str(self.lista_wynikow[0])+
                                          "\nLiczba przegranych: "+str(self.lista_wynikow[1]))

        for i in range(3):
            self.lista_wynikow[i] = str(self.lista_wynikow[i])
        with open("statystyki.txt", 'w') as statystyki:
            statystyki.write('\n'.join(self.lista_wynikow))

    def wygrana(self):
        self.czyRozpoczeta = FALSE
        self.lista_wynikow[0] += 1
        if self.Czas < self.lista_wynikow[2]: self.lista_wynikow[2] = self.Czas
        for key in self.buttons:
            self.buttons[key][0].unbind('<Button-1>')
            self.buttons[key][0].unbind('<Button-3>')
            self.buttons[key][0].unbind('<Double-Button-1>')
        messagebox.showinfo("Koniec gry", "Gratulacje, wygrana!"
                                          "\nLiczba wygranych: " + str(self.lista_wynikow[0]) +
                                          "\nLiczba przegranych: " + str(self.lista_wynikow[1]))

        for i in range(3):
            self.lista_wynikow[i] = str(self.lista_wynikow[i])
        with open("statystyki.txt", 'w') as statystyki:
            statystyki.write('\n'.join(self.lista_wynikow))

    def update_flags(self):
        self.label3.config(text="Pozostało: " + str(LICZBA_MIN-self.postawioneFlagi))

    def timer(self):
        while self.czyRozpoczeta == TRUE:
            self.label2.config(text="Czas: " + str(self.Czas))
            self.Czas += 1
            time.sleep(1)

    def reset(self):
        self.lista_wynikow = []
        with open("statystyki.txt", 'r') as statystyki:
            self.lista_wynikow = [int(i) for i in statystyki]  # wygrane / przegrane / pocz/ zaaw/ trudny

        self.odkrytePola = 0
        self.postawioneFlagi = 0
        self.update_flags()
        self.czyRozpoczeta = FALSE
        self.Czas = 0
        self.odwiedzone = []

        self.mapa = Mapa(WYSOKOSC, SZEROKOSC)
        self.mapa.wyznacz_mape(WYSOKOSC, SZEROKOSC, LICZBA_MIN)
        x_coord, y_coord = 0, 0
        for i in range(SZEROKOSC*WYSOKOSC):
            self.buttons[i][0].config(image=self.zakryte)
            self.buttons[i][2] = 0
            self.buttons[i][5] = self.mapa.dane[x_coord][y_coord].sasiedzi
            self.buttons[i][1] = 0
            self.buttons[i][0].bind('<Button-1>', self.lclicked_wrapper(i))
            self.buttons[i][0].bind('<Button-3>', self.rclicked_wrapper(i))
            self.buttons[i][0].bind('<Double-Button-1>', self.dclicked_wrapper(i))
            if self.mapa.dane[x_coord][y_coord].sasiedzi == 9:
                self.buttons[i][1] = 1

            x_coord += 1
            if x_coord == SZEROKOSC:
                x_coord = 0
                y_coord += 1

    def stats(self):
        if self.czyRozpoczeta == FALSE:
            for i in range(3):
                self.lista_wynikow[i] = int(self.lista_wynikow[i])
        if self.lista_wynikow[0] == 0 and self.lista_wynikow[1] == 0:
            messagebox.showinfo("Statystyki", "\nLiczba wygranych: 0" +
                                "\nLiczba przegranych: 0" +
                                "\nProcent wygranych: 0%" +
                                "\nNajlepszy czas: brak")
        elif self.lista_wynikow[0] == 0 and self.lista_wynikow[1] != 0:
            messagebox.showinfo("Statystyki", "\nLiczba wygranych: 0" +
                                "\nLiczba przegranych: " + str(self.lista_wynikow[1]) +
                                "\nProcent wygranych: 0%" +
                                "\nNajlepszy czas: brak")
        else:
            messagebox.showinfo("Statystyki", "\nLiczba wygranych: " + str(self.lista_wynikow[0]) +
                                              "\nLiczba przegranych: " + str(self.lista_wynikow[1]) +
                                              "\nProcent wygranych: " + str(int(100*self.lista_wynikow[0]/(self.lista_wynikow[0]+self.lista_wynikow[1]))) + "%" +
                                              "\nNajlepszy czas: " + str(self.lista_wynikow[2]))
