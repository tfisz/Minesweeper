from random import randint

BOMBA: int = 9


class Pole:
    def __init__(self):
        self.sasiedzi = 0


class Mapa(Pole):
    def __init__(self, x, y):
        self.dane = [[Pole() for i in range(x)] for i in range(y)]

    def wyznacz_mape(self, x, y, liczba_min):
        while liczba_min > 0:
            pozycja = randint(0, (x * y)-1)
            if self.dane[int(pozycja / x)][pozycja % x].sasiedzi != BOMBA:
                self.dane[int(pozycja/x)][pozycja % x].sasiedzi = BOMBA
                liczba_min -= 1

        for i in range(y):
            for j in range(x):
                if self.dane[i][j].sasiedzi == BOMBA:
                    if i > 0 and j > 0 and self.dane[i - 1][j - 1].sasiedzi != BOMBA:
                        self.dane[i-1][j-1].sasiedzi += 1
                    if j > 0 and self.dane[i][j - 1].sasiedzi != BOMBA:
                        self.dane[i][j-1].sasiedzi += 1
                    if i < y-1 and j > 0 and self.dane[i + 1][j - 1].sasiedzi != BOMBA:
                        self.dane[i+1][j-1].sasiedzi += 1
                    if i > 0 and self.dane[i - 1][j].sasiedzi != BOMBA:
                        self.dane[i-1][j].sasiedzi += 1
                    if i < y-1 and self.dane[i + 1][j].sasiedzi != BOMBA:
                        self.dane[i+1][j].sasiedzi += 1
                    if i > 0 and j < x-1 and self.dane[i - 1][j + 1].sasiedzi != BOMBA:
                        self.dane[i-1][j+1].sasiedzi += 1
                    if j < x-1 and self.dane[i][j + 1].sasiedzi != BOMBA:
                        self.dane[i][j+1].sasiedzi += 1
                    if i < y-1 and j < x-1 and self.dane[i + 1][j + 1].sasiedzi != BOMBA:
                        self.dane[i+1][j+1].sasiedzi += 1