import xml.etree.ElementTree as ET
import glob
import os
import json
import argparse


def xml_to_yolo_bbox(bbox, w, h):
    # xmin, ymin, xmax, ymax
    x_center = ((bbox[2] + bbox[0]) / 2) / w
    y_center = ((bbox[3] + bbox[1]) / 2) / h
    width = (bbox[2] - bbox[0]) / w
    height = (bbox[3] - bbox[1]) / h
    return [x_center, y_center, width, height]


def yolo_to_xml_bbox(bbox, w, h):
    # x_center, y_center width heigth
    w_half_len = (bbox[2] * w) / 2
    h_half_len = (bbox[3] * h) / 2
    xmin = int((bbox[0] * w) - w_half_len)
    ymin = int((bbox[1] * h) - h_half_len)
    xmax = int((bbox[0] * w) + w_half_len)
    ymax = int((bbox[1] * h) + h_half_len)
    return [xmin, ymin, xmax, ymax]

def main():

    parser = argparse.ArgumentParser(description="Partition dataset of images into training and testing sets",
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        '-o', '--outputDir',
        help='Path to the folder where the image labels should be stored. If not specified, the program fails.',
        type=str,
        default=None
    )

    parser.add_argument(
        '-i', '--imageDir',
        help='Path to the folder where the image dataset is stored. If not specified, the program fails.',
        type=str,
        default=None
    )

    args = parser.parse_args()

    if args.outputDir == None or args.imageDir == None:
        print('\'Output\' or \'Image\' directory was not specified.')
        return 

    classes = []
    # input_dir = "annotations/"
    # input_dir = 'train/'
    output_dir = args.outputDir
    input_dir = image_dir = args.imageDir

    # image_dir = "images/"
    index = 0
    # create the labels folder (output directory)
    os.mkdir(output_dir)

    # class names and index
    labels = [{'name':'placeofbirth', 'id':1}, {'name':'dateofbirth', 'id':2},{'name':'height', 'id':3},{'name':'bloodgroup', 'id':4},{'name':'sex', 'id':5},\
            {'name':'expirelocation', 'id':6},{'name':'id1', 'id':7},{'name':'id2', 'id':8},{'name':'idnumber', 'id':9},{'name':'lastnames', 'id':10}, \
            {'name':'firstnames', 'id':11}]

    # identify all the xml files in the annotations folder (input directory)
    files = glob.glob(os.path.join(input_dir, '*.xml'))
    # loop through each 
    for fil in files:
        basename = os.path.basename(fil)
        filename = os.path.splitext(basename)[0]
        # check if the label contains the corresponding image file
        if not os.path.exists(os.path.join(image_dir, f"{filename}.jpg")):
            print(f"{filename} image does not exist!")
            continue

        result = []

        # parse the content of the xml file
        tree = ET.parse(fil)
        root = tree.getroot()
        width = int(root.find("size").find("width").text)
        height = int(root.find("size").find("height").text)

        for obj in root.findall('object'):
            label = obj.find("name").text
            # check for new classes and append to list
            if label not in classes:
                classes.append(label)
            # get class id    
            for item in labels:
                if item['name'] == label:
                    index = item['id']

            # index = classes.index(label)
            pil_bbox = [int(x.text) for x in obj.find("bndbox")]
            yolo_bbox = xml_to_yolo_bbox(pil_bbox, width, height)
            # convert data to string
            bbox_string = " ".join([str(x) for x in yolo_bbox])
            result.append(f"{index} {bbox_string}")

        if result:
            # generate a YOLO format text file for each xml file
            with open(os.path.join(output_dir, f"{filename}.txt"), "w", encoding="utf-8") as f:
                f.write("\n".join(result))

    # generate the classes file as reference
    with open('classes.txt', 'w', encoding='utf8') as f:
        f.write(json.dumps(classes))


if __name__ == '__main__':
    main()
