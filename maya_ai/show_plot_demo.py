from maya_ai.calculator import Calculator

if __name__ == '__main__':
    calc = Calculator()
    try:
        img = calc.show_plot_gui('sin(x)', -3.14, 3.14, points=300, blocking=True)
        print('Displayed plot:', img)
    except Exception as e:
        print('Failed to display plot in GUI:', e)
