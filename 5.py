import turtle as t

t.speed(-100)
t.bgcolor('black')
t.pencolor('orange')
def square(x, y):
    for j in range(4):
        t.forward(x)
        t.right(y)
for i in range(80):
    t.right(10)
    t.circle(100)
    t.right(100)
    t.hideturtle()
t.done()

