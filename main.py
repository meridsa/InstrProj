from SideGrabber import runSG

def main():
    """The main function that solves the cube"""
    #On startup grab 1 side
    input('Press enter when first face (F) is facing camera!')
    front = runSG('c')
    print(front)
    input('Rotate top of cube towards you so that U is facing camera and press enter!')
    up = runSG('c')
    print(up)
    input('Rotate top of cube towards you so that B is facing camera and press enter!')
    back = runSG('c')
    print(back)
    input('Rotate top of cube towards you so that D is facing camera and press enter!')
    down = runSG('c')
    print(down)
    input('Rotate cube clockwise 90 degrees such that L is facing camera and press enter!')
    left = runSG('c')
    print(left)
    input('Rotate cube clockwise 180 degrees such that R is facing camera and press enter!')
    right = runSG('c')
    print(right)

    cube = [front, up, back, down, left, right]


if __name__ == '__main__': main()