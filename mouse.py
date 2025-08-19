import subprocess
import sys
from random import randint, choice
from math import ceil
from typing import Tuple

def move_to_area(x, y, width, height, deviation, speed):
    '''
    Arguments same as pyautogui.locateAllOnScreen format: x and y are top left corner
    
    This advanced function saves the xdotool commands to a temporary file
    'mouse.sh' in ./tmp/ then executes them from the shell to give clean curves
    '''


    # Run the command and capture output
    output = subprocess.check_output(["xdotool", "getdisplaygeometry"], text=True)

    # Split into width and height
    initial_w, initial_h = map(int, output.strip().split())

    initial_w = randint(0, initial_w)
    initial_h = randint(0, initial_h)

    initial_w = 100 # until i figure out sth better
    initial_h = 100

    x_coord = x + randint(0, width)
    y_coord = y + randint(0, height)
    
    move(mouse_bez((initial_w, initial_h), (x_coord, y_coord), deviation, speed))
  
    
def pascal_row(n):
    # This returns the nth row of Pascal's Triangle
    result = [1]
    x, numerator = 1, n
    for denominator in range(1, n//2+1):
        # print(numerator,denominator,x)
        x *= numerator
        x /= denominator
        result.append(x)
        numerator -= 1
    if n&1 == 0:
        # n is even
        result.extend(reversed(result[:-1]))
    else:
        result.extend(reversed(result)) 
    return result


    
def make_bezier(xys):

    # xys should be a sequence of 2-tuples (Bezier control points)
    n = len(xys)
    combinations = pascal_row(n - 1)
    def bezier(ts):
        # This uses the generalized formula for bezier curves
        # http://en.wikipedia.org/wiki/B%C3%A9zier_curve#Generalization
        result = []
        for t in ts:
            tpowers = (t**i for i in range(n))
            upowers = reversed([(1-t)**i for i in range(n)])
            coefs = [c*a*b for c, a, b in zip(combinations, tpowers, upowers)]
            result.append(
                list(sum([coef*p for coef, p in zip(coefs, ps)]) for ps in zip(*xys)))
        return result
    return bezier


def mouse_bez(init_pos: Tuple[int, int], fin_pos: Tuple[int, int], deviation: int, speed: int):
    '''
    GENERATE BEZIER CURVE POINTS
    Takes init_pos and fin_pos as a 2-tuple representing xy coordinates
        variation is a 2-tuple representing the
        max distance from fin_pos of control point for x and y respectively
        speed is an int multiplier for speed. The lower, the faster. 1 is fastest.
            
    '''

    #time parameter
    ts = [t/(speed * 100.0) for t in range(speed * 101)]
    
    #bezier centre control points between (deviation / 2) and (deviaion) of travel distance, plus or minus at random
    control_1 = (init_pos[0] + choice((-1, 1)) * abs(ceil(fin_pos[0]) - ceil(init_pos[0])) * 0.01 * randint(deviation // 2, deviation),
                init_pos[1] + choice((-1, 1)) * abs(ceil(fin_pos[1]) - ceil(init_pos[1])) * 0.01 * randint(deviation // 2, deviation)
                    )
    control_2 = (init_pos[0] + choice((-1, 1)) * abs(ceil(fin_pos[0]) - ceil(init_pos[0])) * 0.01 * randint(deviation // 2, deviation),
                init_pos[1] + choice((-1, 1)) * abs(ceil(fin_pos[1]) - ceil(init_pos[1])) * 0.01 * randint(deviation // 2, deviation)
                    )
        
    xys = [init_pos, control_1, control_2, fin_pos]
    bezier = make_bezier(xys)
    points = bezier(ts)

    return points
        

def connected_bez(coord_list, deviation, speed):

    '''
    Connects all the coords in coord_list with bezier curve
    and returns all the points in new curve
    
    ARGUMENT: DEVIATION (INT)
        deviation controls how straight the lines drawn my the cursor
        are. Zero deviation gives straight lines
        Accuracy is a percentage of the displacement of the mouse from point A to
        B, which is given as maximum control point deviation.
        Naturally, deviation of 10 (10%) gives maximum control point deviation
        of 10% of magnitude of displacement of mouse from point A to B, 
        and a minimum of 5% (deviation / 2)
    '''
    
    i = 1
    points = []
    
    points.append('click')
    while i < len(coord_list):
        points += mouse_bez(coord_list[i - 1], coord_list[i], deviation, speed)
        points.append('click')
        i += 1
    
    return points


def move(mouse_points, rand_err = True):
    '''
    Moves mouse in accordance with a list of points (continuous curve)
    Input these as a list of points (2-tuple or another list)
    
    Generates file (mouse.sh) in ./tmp/ and runs it as bash file
    
    If you want a click at a particular point, write 'click' for that point in
    mouse_points
    
    This advanced function saves the xdotool commands to a temporary file
    'mouse.sh' in ./tmp/ then executes them from the shell to give clean curves
    
    You may wish to generate smooth bezier curve points to input into this
    function. In this case, take mouse_bez(init_pos, fin_pos, deviation, speed)
    as the argument.
    
    PARAMETERS:
        mouse_points
            list of 2-tuples or lists of ints or floats representing xy coords
        rand_err
            whether to introduce random doubleclicks
    '''
    
    #fname = 'mouse.sh'
     
    #outfile = open(CWD + '/tmp/' + fname, 'w')
    #os.system('chmod +x ' + CWD + '/tmp/' + fname)
    print('#!/bin/bash')
    print('\n\n')

    
    #round floats to ints
    mouse_points = [[round(v) for v in x] if type(x) is not str else x for x in mouse_points]
    for coord in mouse_points:
        if coord == 'click':
            if rand_err:
                tmp = randint(1,39)
                if tmp == 1:
                    print('xdotool click 3 \n')
                elif tmp == 2:
                    print('xdotool click --repeat 2 1 \n')
                elif tmp in range(4, 40):   #if tmp == 4, write nothing
                    print('xdotool click 1 \n') #normal click
            else:
                print('xdotool click 1 \n')
        else:
            if coord[0] >= 0 and coord[1] >= 0:
                print('xdotool mousemove ' + str(coord[0]) + ' ' + str(coord[1]) + '\n', end='')
     
    # outfile.close()
    # subprocess.call([CWD + '/tmp/' + fname])



if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(f"Usage: python {sys.argv[0]} x y width height")
        sys.exit(1)

    x = int(sys.argv[1])
    y = int(sys.argv[2])
    width = int(sys.argv[3])
    height = int(sys.argv[4])

    move_to_area(x, y, width, height, 4, 8)