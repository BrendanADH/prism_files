# get variables; #robots, #tasks, grid_size

import numpy as np
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("num_robots", type=int, help="Number of robots to be included in the model")
parser.add_argument("num_tasks", type=int, help="Number of tasks to be included in the model")
parser.add_argument("grid_size", type=int, help="Size of grid axis")
parser.add_argument("output_name", type=str, help="Filename for output")

args = parser.parse_args()
print(f"Model created.")

f = open(args.output_name + ".prism", "x")

f.write("mdp\n\n")
f.write(f'''const int num_robots = {args.num_robots};
const int num_tasks = {args.num_tasks};
const int grid_size = {args.grid_size};
const int max_grid_id = {args.grid_size - 1};
''')

# robot modules:
for i in range(0, args.num_robots):
    f.write(f'''\nmodule robot{i}
    
    \tR{i}Lock : bool; // lock for clock sync
    \tx{i} : [0..max_grid_id] init 0; // location variables
    \ty{i} : [0..max_grid_id] init 0;

    \t[release] R{i}Lock = true -> (R{i}Lock'=false); // release lock according to the sync module

    \t// movement commands
    \t[R{i}MoveLeft] !R{i}Lock & x{i}>0 -> (x{i}'=x{i}-1) & (R{i}Lock' = true);
    \t[R{i}MoveRight] !R{i}Lock & x{i}<max_grid_id-> (x{i}'=x{i}+1) & (R{i}Lock' = true);
    \t[R{i}MoveUp] !R{i}Lock & y{i}<max_grid_id -> (y{i}'=y{i}+1) & (R{i}Lock' = true);
    \t[R{i}MoveDown] !R{i}Lock & y{i}>0 -> (y{i}'=y{i}-1) & (R{i}Lock' = true);
    
    \t//complete tasks:\n''')

    for j in range(0, args.num_tasks):
        f.write(f'''\t[T{j}Complete] !R{i}Lock & T{j}Active=true & x{i}=tx{j} & y{i}=ty{j}-> (R{i}Lock' = true);\n''')

    f.write(f'''\n\t// wait
    \t[R{i}Wait] !R{i}Lock -> (R{i}Lock' = true); //do nothing
    
    endmodule\n\n''')

# task modules:
for i in range(0, args.num_tasks):
    f.write(f'''\nmodule task{i}
    
    \tT{i}Active : bool init true;
    \ttx{i} : [0..max_grid_id];
    \tty{i} : [0..max_grid_id];
    
    \t[T{i}Complete] T{i}Active=true & x{i}=tx{i} & y{i}=ty{i} -> (T{i}Active' = false);
    
    endmodule\n\n''')


# synchronisation modules:
f.write(f'''module sync

\tcompleted: [0..{args.num_robots}] init 0;

\t[release] completed = {args.num_robots} -> (completed'=0);''')

for i in range(0, args.num_robots):
    f.write(f'''
    
    \t[R{i}MoveLeft] true -> (completed' = min(completed+1, num_robots));
    \t[R{i}MoveRight] true -> (completed' = min(completed+1, num_robots));
    \t[R{i}MoveUp] true -> (completed' = min(completed+1, num_robots));
    \t[R{i}MoveDown] true -> (completed' = min(completed+1, num_robots));
    \t[R{i}Wait] true -> (completed' = min(completed+1, num_robots));''')

f.write('\n\nendmodule\n\n')

# obstacles
f.write(f'module obstacles\n')
for i in range(0, args.grid_size):
    for j in range(0, args.grid_size):
        f.write(f'\tX{i}Y{j}_Occupied : bool init false;\n')
f.write('\nendmodule\n\n')


# rewards
f.write('''rewards "time"
		
\t[release] true: 1;

endrewards''')
