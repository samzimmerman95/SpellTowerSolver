try:
    from PIL import Image, ImageFilter, ImageDraw, ImageOps
except ImportError:
    import Image
import pytesseract
import numpy as np
# import matplotlib.pyplot as plt

print("tesseract version:", pytesseract.get_tesseract_version())


def darkMode(image):
    testArea = image.crop((0, 5, image.width, 10))
    top = testArea.convert("1")
    a = np.array(top)
    total = np.sum(a)
    threshold = (len(a)*len(a[0]))/2
    if total > threshold:
        return False
    else:
        return True


def newDarkMode(image):
    im = image.convert("1", dither=Image.NONE)
    h = im.histogram()
    darkToLight = h[0]/h[-1]
    if darkToLight > 1:
        return True
    else:
        False


def cropAndFilter(file):
    tower = Image.open(file)
    if newDarkMode(tower):
        tower = ImageOps.invert(tower)
        # print("Dark Mode detected!")
        # tower.show()

    topRemoved = tower.crop((0, tower.height/5, tower.width, tower.height))

    grayScale = topRemoved.convert("L")
    largerLetters = grayScale.filter(
        ImageFilter.MinFilter)  # Makes letter larger
    a = np.array(largerLetters)
    a[a > 33] = 255
    darkestRemaining = Image.fromarray(a)
    median = darkestRemaining.filter(
        ImageFilter.MedianFilter)
    final = median.convert("1", dither=Image.NONE)
    # final.show()
    return final, tower.height/5


def recgonizeLetters(image):
    customConfig = r'--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ load_system_dawg=false load_freq_dawg=false'
    grid = pytesseract.image_to_boxes(
        image, output_type=pytesseract.Output.DICT, config=customConfig)
    grid.pop('page', None)
    return grid


def drawBoundingBoxes(image, data):
    # Draw rectangles around letters and cross at midpoint. Testing only.
    h = image.height  # coordinates are from bottom left so have to know height to draw
    image = image.convert("RGB")
    im = ImageDraw.Draw(image)
    for i in range(len(data['char'])):
        shape = [data['left'][i], h-data['top'][i],
                 data['right'][i], h-data['bottom'][i]]
        im.rectangle(shape, width=3, outline="#ff0000")

        x = data['midPointX'][i]
        y = data['midPointY'][i]
        im.line([x-10, h-y, x+10, h-y], width=2, fill="#0000ff")
        im.line([x, h-y-10, x, h-y+10], width=2, fill="#0000ff")

    # print("num boxes: ", len(data['char']))
    # image.show()


def removeErrantRecognitions(image, data):
    toRemove = []
    upperBound = (image.width / 14) * 1.5  # 120.5
    lowerBound = image.width / 140  # 8.03

    for i in range(len(data['char'])):
        height = data['top'][i] - data['bottom'][i]
        width = data['right'][i] - data['left'][i]
        if height > upperBound or width > upperBound:
            toRemove.append(i)
            # print(height, width)
        elif height < lowerBound and width < lowerBound:
            toRemove.append(i)
            # print(height, width)

    toRemove.sort(reverse=True)
    for index in toRemove:
        data['char'].pop(index)
        data['left'].pop(index)
        data['right'].pop(index)
        data['top'].pop(index)
        data['bottom'].pop(index)
        # print("Removed index:", index)


def calculateRow(image, data):
    data['midPointY'] = []
    for i in range(len(data['char'])):
        data['midPointY'].append(data['bottom'][i] +
                                 (data['top'][i] - data['bottom'][i]) // 2)
    averages = findAverages(data['midPointY'])
    # Since (0,0) for image is bottom left, larger number means towards the top
    averages.sort(reverse=True)
    insertMissingSection(averages, image)
    identifyLocation('row', 'midPointY', averages, data)
    # print("Row averages:", averages)


def calculateCol(image, data):
    data['midPointX'] = []
    for i in range(len(data['char'])):
        data['midPointX'].append(data['left'][i] +
                                 (data['right'][i] - data['left'][i]) // 2)

    averages = findAverages(data['midPointX'])
    insertMissingSection(averages, image)
    identifyLocation('col', 'midPointX', averages, data)
    # print("Col averages:", averages)
    diff = []
    for i in range(1, len(averages)):
        diff.append(averages[i] - averages[i-1])
    # print("Diff in Col: ", diff)


def findAverages(array):
    # Given an array find the average of all groups all similiar elements
    # Elements are deemed the same using the same function, if their values close
    a = sorted(array)
    averages = []
    total = a[0]
    num = 1
    for i in range(1, len(a)):
        if same(a[i-1], a[i]):
            total += a[i]
            num += 1
        else:
            averages.append(total // num)
            total = a[i]
            num = 1
    averages.append(total // num)

    return averages


def insertMissingSection(averages, image):
    # Find empty rows or cols and edit averages to reflect that
    # On my phone, the difference between cols/rows is ~124
    i = 1
    differentColThreshold = (image.width / 7) * 1.1  # 178.8
    while i < len(averages):
        diff = abs(averages[i]-averages[i-1])
        if diff > differentColThreshold:
            averages.insert(i, 0)
            i += 1
        i += 1


def identifyLocation(section, raw, averages, data):
    # Based on averages array, identify the row or col for each letter
    data[section] = []
    for i in range(len(data[raw])):
        val = min(averages, key=lambda x: abs(x-data[raw][i]))
        data[section].append(averages.index(val))


def constructGrid(data):
    rows = max(data['row'])
    cols = max(data['col'])
    print(f"Construct grid {rows} rows and {cols} cols.")
    grid = [[' ' for c in range(cols+1)] for r in range(rows+1)]

    for i in range(len(data['char'])):
        r = data['row'][i]
        c = data['col'][i]
        grid[r][c] = data['char'][i]

    for i in range(len(grid)):
        grid[i] = ''.join(grid[i]).lower()

    return grid


def same(known, test):
    diff = abs(known-test)
    if diff < 20:
        return True
    return False


def displayCroppedGrid(file, image, data, cropHeight):
    # Crop the oringial picture to only show area with letters
    # If we want to draw path of word on this, coordinates in data will be off
    margin = 25
    left = min(data['left']) - margin
    right = max(data['right']) + margin
    top = max(data['top']) + margin
    bottom = min(data['bottom']) - margin
    h = image.height + cropHeight
    original = Image.open(file)
    c = original.crop((left, h-top, right, h-bottom))
    # c.show()


def convert(file):
    image, cropHeight = cropAndFilter(file)
    data = recgonizeLetters(image)
    removeErrantRecognitions(image, data)
    calculateRow(image, data)
    calculateCol(image, data)
    drawBoundingBoxes(image, data)
    grid = constructGrid(data)
    # displayCroppedGrid(file, image, data, cropHeight)
    # print(data)
    return grid, data


# convert('DarkTower.jpeg')
# convert('newApp/4.jpeg')
# print(convert('current/2.jpeg'))
