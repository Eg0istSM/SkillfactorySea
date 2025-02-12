from random import randint


# классы исключений
class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Мимо доски"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Клетка занята!"


class BoardWrongShipException(BoardException):
    pass


# класс точек с системой координат
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot({self.x},{self.y})"


class Ship:
    def __init__(self, head, l, orient):
        self.head = head
        self.l = l
        self.orient = orient
        self.lives = l

    @property
    def dots(self):  # создание корабля
        ship_coord = []
        for i in range(self.l):
            coord_x = self.head.x
            coord_y = self.head.y
            if self.orient == 0:
                coord_x += i
            elif self.orient == 1:
                coord_y += i

            ship_coord.append(Dot(coord_x, coord_y))
        return ship_coord

    def shot(self, shot):  # проверка попадания в корабль, возвращает Bool
        return shot in self.dots


# доска,добавление кораблей, проверка координатов кораблей,контуры
class Board:
    def __init__(self, hid=False, size=6):  # задаем атрибуты доски
        self.size = size
        self.hid = hid

        self.count = 0

        self.field = [["O"] * size for _ in range(size)]

        self.busy = []
        self.ships = []

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def add_ship(self, ship):  # добавление корабля на доску
        for d in ship.dots:
            if self.out(d) or d in self.busy:  # проверка на занятость клеток и выполнения условий заполнения доски
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):  # окружение коробля, которое не могут занимать другие корабли
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "T"
                    self.busy.append(cur)

    def __str__(self):  # определяем формат вывода доски в терминал
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "O")
        return res

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:  # проверка количества жизней корабля
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Вы уничтожили корабль противника!")
                    return False
                else:
                    print("Вы попали в корабль соперника!")
                    return True

        self.field[d.x][d.y] = "T"
        print("Промах!")
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Компьютер сделал ход: {d.x + 1} {d.y + 1}")
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Введите координаты: ").split()

            if len(cords) != 2:
                print("Необходимо ввести два числа! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print("Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def greet(self):
        print('-----------------------')
        print('Добро пожаловать в игру')
        print('      Морской бой      ')
        print('-----------------------')
        print('   Формат ввода: x y   ')
        print('   x - номер строки    ')
        print('   y - номер столбца   ')

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-" * 20)
            print("Доска компа:")
            print(self.ai.board)
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь.")
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Ходит компьютер.")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-" * 20)
                print("Пользователь ВЫИГРАЛ!!!")
                break

            if self.us.board.count == 7:
                print("-" * 20)
                print("Компьютер побеждает!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()