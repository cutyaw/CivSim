import random
import time
import curses

WORLD_SIZE = 20
NUM_YEARS = 1000000000
DESIRED_DATA_POINTS = 100
BIRTH_RATE = 0.03
show_world = True
chaos_mode = False

# Define the World
class World:
    def __init__(self, size):
        self.size = size
        self.grid = [[' ' for _ in range(size)] for _ in range(size)]

    def display(self, window):
        for row in self.grid:
            window.addstr(' '.join(row))
            window.addstr('\n')

def plot_population_graph(stdscr, population_count_list, title):
    try:
        graph_win = stdscr.subwin(curses.LINES - 1, curses.COLS // 3 - 3, 0, 2 * curses.COLS // 3)
        graph_win.clear()
        graph_height = curses.LINES - 1
        graph_width = curses.COLS // 3 - 3

        max_population = max(population_count_list)
        min_population = min(population_count_list)
        scale_factor = graph_height / (max_population * 2) if max_population > 0 else 1

        start_year = max(0, len(population_count_list) - graph_width)
        for year in range(start_year, len(population_count_list)):
            y_pos = int(graph_height - population_count_list[year] * scale_factor)
            graph_win.addch(y_pos, year - start_year, '—')

        # Add side numbers for the lowest, in-between, and highest population counts
        low_value = min_population
        high_value = max_population
        in_between_value = (max_population + min_population) // 2

        # Calculate the y-coordinate for each number
        y_low = int(graph_height - low_value * scale_factor)
        y_in_between = int(graph_height - in_between_value * scale_factor)
        y_high = int(graph_height - high_value * scale_factor)

        # Display the numbers on the graph window on the left side
        graph_win.addstr(y_low, 0, f"{low_value}")
        graph_win.addstr(y_in_between, 0, f"{in_between_value}")
        graph_win.addstr(y_high, 0, f"{high_value}")

        # Display the title above the graph
        title_x = (graph_width - len(title)) // 2
        graph_win.addstr(0, title_x, title)

        graph_win.refresh()
    except Exception as e:
        pass


class Person:
    def __init__(self, name, x, y, age):
        self.name = name
        self.x = x
        self.y = y
        self.age = age
        self.partner = None
        self.kids = []
        self.mental_health = 100
        self.dead = False

    def move(self):
        dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        new_x = (self.x + dx) % WORLD_SIZE
        new_y = (self.y + dy) % WORLD_SIZE
        self.x = new_x
        self.y = new_y

    def update(self):
        global kids
        if self.partner == None: # najit si partnera
            for person in people:
                if person.partner == None:
                    if person.age >= 15 and self.age >= 15 and self.age <= 65 and person.age <= 65:
                        if abs(self.age - person.age) <= 4:
                            self.partner = person
                            person.partner = self
        else:
            if len(self.kids) < 3:   #Zkusit udelat deti
                if random.random() < birth_rate:
                    nam = random.choice(names)
                    baby = Person(f'{nam}', self.x, self.y, 0)
                    self.kids.append(baby)
                    self.partner.kids.append(baby)
                    people.append(baby)
                    kids += 1

        self.move()
        self.grow()
        self.hurt_mental_health_passively()

        if self.partner != None and self.partner.dead:
                self.partner.hurt_mental_health()
                self.partner = None
    
        if self.age >= random.randint(80, 100):
            self.dead = True

        if(random.randint(0, 1000) > 999):
            self.dead = True
    
        if self.mental_health == 0: #sebevrazda
            self.dead = True

    def hurt_mental_health(self):
        self.mental_health += random.randint(-75, 0)

    def hurt_mental_health_passively(self):
        self.mental_health += random.randint(-10, 10)

    def grow(self):
        self.age += 1

    def __repr__(self):
        return f'{self.name} (Age: {self.age})'
    

start = time.time()
temp = time.time_ns()
people = []
kids = 0
birth_rate = 0
names = None
def main(stdscr):
    global temp
    global people
    global birth_rate
    global names
    global kids
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    stdscr.clear()
    world = World(WORLD_SIZE)
    names = open("names.txt", "r").read().splitlines()


    for i in range(3):
        x = random.randint(0, WORLD_SIZE - 1)
        y = random.randint(0, WORLD_SIZE - 1)
        age = random.randint(1, 5)
        nam = random.choice(names)
        person = Person(f'{nam}', x, y, age)
        people.append(person)

    death_count = 0
    population_count_list = []
    lastyearpop = 0

    for year in range(NUM_YEARS):
        year += 1
        max_population = WORLD_SIZE ** 2
        current_population = len(people)
        world.grid = [[' ' for _ in range(WORLD_SIZE)] for _ in range(WORLD_SIZE)]

        if not chaos_mode:
            birth_rate = random.uniform(0.01, 0.05) * (1 - current_population / max_population)
        else:
            birth_rate = random.uniform(0.05, 0.1)
        
        kids = 0

        for person in people:
            if person.dead:
                death_count += 1
                people.remove(person)
            else:
                #new_people.append(person)
                person.update()
                world.grid[person.y][person.x] = "X"

        stdscr.clear()
        stdscr.addstr('\n')
        if show_world:
            world.display(stdscr)
        stdscr.addstr('\n')
        if people:
            if chaos_mode:
                stdscr.addstr("CHAOS MODE ON\n", curses.color_pair(1))
            stdscr.addstr(f"Year: {year}\nPopulation Count: {len(people)}\nOldest Person: {max(people, key=lambda person: person.age)}\nDeath Count: {death_count}\nBirth Rate: {round(birth_rate, 3)}\nBirths this year: {kids}\n")
            lastyearpop = len(people)
        else:
            stdscr.addstr("Everyone died\n", curses.color_pair(2))
            stdscr.addstr("Everyone died\n", curses.color_pair(2))
            stdscr.addstr("Everyone died\n", curses.color_pair(2))
            time.sleep(5)
            break

        population_count_list.append(len(people))
        plot_population_graph(stdscr, population_count_list, "Population Graph")
        #if year >= 1000:
        #    stop = time.time()
        #    curses.endwin()
        #    print(f"Time taken: {stop - start}")
        #    time.sleep(3)
        #    break
        #time.sleep(0.01)
        stdscr.refresh()    

if __name__ == "__main__":
    curses.wrapper(main)
