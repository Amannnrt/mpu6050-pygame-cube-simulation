import pygame
from math import *
import socket
import time

WINDOW_SIZE = 800
window = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
clock = pygame.time.Clock()

# Initialize UDP socket
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind(('192.168.1.3', 2345))  # Bind to any IP on port 12345

projection_matrix = [[1, 0, 0],
                     [0, 1, 0],
                     [0, 0, 0]]

cube_points = [n for n in range(8)]
cube_points[0] = [[-1], [-1], [1]]
cube_points[1] = [[1], [-1], [1]]
cube_points[2] = [[1], [1], [1]]
cube_points[3] = [[-1], [1], [1]]
cube_points[4] = [[-1], [-1], [-1]]
cube_points[5] = [[1], [-1], [-1]]
cube_points[6] = [[1], [1], [-1]]
cube_points[7] = [[-1], [1], [-1]]


def multiply_m(a, b):
    a_rows = len(a)
    a_cols = len(a[0])
    b_rows = len(b)
    b_cols = len(b[0])
    product = [[0 for _ in range(b_cols)] for _ in range(a_rows)]
    if a_cols == b_rows:
        for i in range(a_rows):
            for j in range(b_cols):
                for k in range(b_rows):
                    product[i][j] += a[i][k] * b[k][j]
    else:
        print("INCOMPATIBLE MATRIX SIZES")
    return product


def connect_points(i, j, points):
    pygame.draw.line(window, (0, 255, 255), (points[i][0], points[i][1]), (points[j][0], points[j][1]))


# Main Loop
scale = 100
angle_x = angle_y = angle_z = 0
last_time = time.time()
while True:
    clock.tick(60)
    window.fill((35, 35, 35))

    # Receive data from UDP
    try:
        data, addr = udp_socket.recvfrom(1024)
        data = data.decode('utf-8').strip()
        gyro_data = data.split(',')
        if len(gyro_data) == 3:
            try:
                gyro_x, gyro_y, gyro_z = map(float, gyro_data)

                current_time = time.time()
                delta_time = current_time - last_time
                last_time = current_time

                angle_x += gyro_x * delta_time
                angle_y += gyro_y * delta_time
                angle_z += gyro_z * delta_time
            except ValueError:
                print("Error parsing gyro data:", gyro_data)
    except socket.error as e:
        print("Socket error:", e)
    except Exception as e:
        print("Unexpected error:", e)

    rotation_x = [[1, 0, 0],
                  [0, cos(angle_x), -sin(angle_x)],
                  [0, sin(angle_x), cos(angle_x)]]

    rotation_y = [[cos(angle_y), 0, sin(angle_y)],
                  [0, 1, 0],
                  [-sin(angle_y), 0, cos(angle_y)]]

    rotation_z = [[cos(angle_z), -sin(angle_z), 0],
                  [sin(angle_z), cos(angle_z), 0],
                  [0, 0, 1]]

    points = [0 for _ in range(len(cube_points))]
    i = 0
    for point in cube_points:
        rotate_x = multiply_m(rotation_x, point)
        rotate_y = multiply_m(rotation_y, rotate_x)
        rotate_z = multiply_m(rotation_z, rotate_y)

        point_2d = multiply_m(projection_matrix, rotate_z)

        x = (point_2d[0][0] * scale) + WINDOW_SIZE / 2
        y = (point_2d[1][0] * scale) + WINDOW_SIZE / 2

        points[i] = (x, y)
        i += 1
        pygame.draw.circle(window, (0, 26, 200), (x, y), 5)

    connect_points(0, 1, points)
    connect_points(0, 3, points)
    connect_points(0, 4, points)
    connect_points(1, 2, points)
    connect_points(1, 5, points)
    connect_points(2, 6, points)
    connect_points(2, 3, points)
    connect_points(3, 7, points)
    connect_points(4, 5, points)
    connect_points(4, 7, points)
    connect_points(6, 5, points)
    connect_points(6, 7, points)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            udp_socket.close()
            exit()

    pygame.display.update()
