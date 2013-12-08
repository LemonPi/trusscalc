# makes the most efficient truss possible for carrying uniform loads
# calculates loads, angles, lengths, and draws the truss given its span (length)
# and number of sections.
from math import *
import turtle
import tkinter

def print_list(list_name, list):
    print("{: <20}: ".format(list_name), end = "")
    for item in list:
        print("{: <9.3f}".format(item), end = "")
    print()

def calc_truss(length, width, sections):
    # 6.7kn/m^2 is standard pedestrian load; give width in meters
    top_load = 6.7 * width * (length - length / sections)  
    side_load = top_load / 2  # each side supports half
    nodes = sections + 1
    node_load = top_load / (sections - 1)
    base = length / sections
    # list to store all of the member values
    top_lens = [0]
    diag_lens = [0]
    diag_loads = [0]
    hor_loads = []
    thetas = [0]
    alphas = [0]  # first element is a place holder
    vert_loads = []
    mid_node = int(sections / 2)
    for i in range(mid_node + 1):  # i is the current node number
        vert_load = abs((mid_node - i) - 0.5) * node_load
        vert_loads.append(vert_load)
        hor_load = sqrt(top_load**2 - vert_load**2)
        hor_loads.append(hor_load)
        theta = asin(vert_load / top_load)
        thetas.append(theta)
        if i > 0:
            if i == mid_node:
                alphas.append(pi/2) # horizontal
                alphas.append(pi/2)
            else:
                alpha = atan(node_load / (hor_loads[i] - hor_loads[i - 1]))
                alphas.append(alpha) # alphas are shifted back 1 to i
            if i == mid_node:
                diag_load = node_load
                diag_loads.append(diag_load)
            else:
                diag_load = node_load / sin(alpha)
                diag_loads.append(diag_load)
            if i > 1:
                top_len = (base * sin(alphas[i]) + diag_lens[i - 1] * sin(abs(alphas[i] - alphas[i - 1]))) /\
                           sin(alphas[i] + thetas[i])
                top_lens.append(top_len)
                diag_len = (diag_lens[i - 1] * sin(alphas[i - 1]) + top_lens[i] * sin(thetas[i])) /\
                            sin(alphas[i])
                diag_lens.append(diag_len)
            if i == 1:
                top_len = base * sin(alpha) / sin(pi - alpha - theta)
                top_lens.append(top_len)
                diag_len = top_lens[i] * sin(thetas[i]) / sin(alpha)
                diag_lens.append(diag_len)
    
    for angle in range(len(thetas)):
        thetas[angle] = degrees(thetas[angle])
    for angle in range(len(alphas)):
        alphas[angle] = degrees(alphas[angle])    
    print_list("Top lengths", top_lens)
    print_list("Diagonal lengths", diag_lens)
    print_list("Diagonal loads", diag_loads)
    print_list("Horizontal loads", hor_loads)
    print_list("Vertical loads", vert_loads)
    print_list("Thetas", thetas)
    print_list("Alphas", alphas)
    all_l = [length, top_lens, diag_lens, thetas, alphas, base, top_load, diag_loads, hor_loads, vert_loads]
    return all_l

def center_load_truss(all_l, side_load, top_hss = 0, diag_hss = 0, bot_hss = 0):
    """
    Give thickness of hss in mm.
    """
    base = all_l[5]
    top_lens = all_l[1]
    diag_lens = all_l[2]
    thetas = all_l[3]
    alphas = all_l[4]
    top_load = all_l[6]
    diag_loads = all_l[7]
    hor_loads = all_l[8]
    vert_loads = all_l[9]
    # del thetas[0]
    for angle in range(len(thetas)):  # first uniform calculation passes them ass degrees
        thetas[angle] = radians(thetas[angle])
    for angle in range(len(alphas)):
        alphas[angle] = radians(alphas[angle])
    top_units = []
    diag_units = []
    hor_units = []
    top_defs = []
    diag_defs = []
    hor_defs = []
    print_list("Thetas after del", thetas)
    # calculate all the virtual loads
    for i in range(len(top_lens)):
        if i == 0:
            top_units.append(side_load / sin(thetas[i + 1]))  # side_load = 0.5 for unit load
            hor_units.append(top_units[i] * cos(thetas[i + 1]))
            diag_units.append(0)
        else:
            diag_unit = top_units[i - 1] * sin(thetas[i] - thetas[i + 1]) /\
                        sin(alphas[i] + thetas[i + 1])
            top_unit = (top_units[i - 1] * cos(thetas[i]) + diag_unit * \
                        cos(alphas[i + 1]) / cos(thetas[i + 1]))
            hor_unit = hor_units[i - 1] + diag_unit * cos(alphas[i + 1])
            diag_units.append(diag_unit)
            hor_units.append(hor_unit)
            top_units.append(top_unit)
    # calculate all the real deformations
    #for i in top_units:  
    #   top_defs.append(
    print("Unit loads for center loading ------")
    print_list("Diagonal loads", diag_units)
    print_list("Horizontal loads", hor_units)
    print_list("Top loads", top_units)


def draw_truss(all_l, start_pos, top_hss, diag_hss, bot_hss, scale):
    """
    List of all values, start_pos(x, y), hss widths(mm), scale(pixels/m).
    """
    length = all_l[0]
    base = all_l[5]
    top_lens = all_l[1]
    diag_lens = all_l[2]
    thetas = all_l[3]
    alphas = all_l[4]
    top_rvrs = top_lens[::-1]
    del thetas[-1]
    thetas_rvrs = thetas[::-1]
    alphas_rvrs = alphas[::-1]
    del alphas_rvrs[0]  # last one is shared, drawn already
    diag_rvrs = diag_lens[::-1]
    del diag_rvrs[0]  # last one is shared
    # scale = 1600 / length    for comfortable scaling

    turtle.penup()
    turtle.setpos(start_pos)
    turtle.pendown()
    turtle.pensize(top_hss / 1000 * scale)  # drawing for top chord
    for i in range(1, len(top_lens)):  # top lens starts at 1
        turtle.setheading(0)
        turtle.left(thetas[i])
        turtle.forward(top_lens[i] * scale)
    for i in range(len(top_rvrs) - 1):  # stop before last element for reverse
        turtle.setheading(0)
        turtle.right(thetas_rvrs[i])
        turtle.forward(top_rvrs[i] * scale)
    turtle.penup()
    turtle.setpos(start_pos)  # return to start to draw bottom chord and diagonal members
    turtle.pendown()

    for i in range(1, len(top_lens)):
        turtle.pensize(bot_hss / 1000 * scale)
        turtle.setheading(0)  # face east again
        turtle.forward(base * scale)  # draw the bottom section
        turtle.setheading(180)  # face west
        turtle.right(alphas[i])
        turtle.pensize(diag_hss / 1000 * scale)  # switch to diagonal size
        turtle.forward(diag_lens[i] * scale)
        turtle.setheading(0)  # face east
        turtle.right(alphas[i])
        turtle.forward(diag_lens[i] * scale)  # end up at the node
    for i in range(len(top_rvrs) - 1):
        turtle.pensize(bot_hss / 1000 * scale)
        turtle.setheading(0)  # face east again
        turtle.forward(base * scale)  # draw the bottom section
        turtle.setheading(0)  # face west
        turtle.left(alphas_rvrs[i])
        turtle.pensize(diag_hss / 1000 * scale)  # switch to diagonal size
        turtle.forward(diag_rvrs[i] * scale)
        turtle.setheading(180)  # face east
        turtle.left(alphas_rvrs[i])
        turtle.forward(diag_rvrs[i] * scale)  # end up at the node
    return turtle.position() # return turtle's last position

 
if __name__ == '__main__':
        """turtle.screensize(4500, 1000)
        turtle.speed(7)
        turtle.hideturtle()
        a = draw_truss(calc_truss(41.5, 10), (-2000, 0), 203, 89, 254, 12)
        b = draw_truss(calc_truss(67, 16), a, 254, 127, 254, 12)
        c = draw_truss(calc_truss(41.5, 10), b, 203, 89, 254, 12)
        screenshot = turtle.getscreen()
        screenshot.getcanvas().postscript(file="mytruss_small.eps")"""
        turtle.screensize(3000, 1000)
        # draw truss takes in the list of all values generated by calc_truss
        draw_truss(calc_truss(41.5, 4, 10), (-1000, 0), 203, 89, 254, 40)
