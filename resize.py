import os
from os import listdir
from os.path import isfile
from argparse import ArgumentParser
from PIL import Image
import xml.etree.ElementTree as ET 

def get_file_info(file):
	# get the file name and extension
	info = os.path.splitext(file)
	return info[0], info[-1]

def resize_jpg(infile, outfile, new_size):
	try:
		img = Image.open(infile)
		img = img.resize(new_size, Image.ANTIALIAS)

		# save the image to a new file
		img.save(outfile, "JPEG")
		print("Resized image '%s'" % infile)
	except IOError:
		print("Cannot resize image '%s'" % infile)

def resize_png(infile, outfile, new_size):
	try:
		img = Image.open(infile)
		img = img.resize(new_size, Image.ANTIALIAS)

		# save the image to a new file
		img.save(outfile, "PNG")
		print("Resized image '%s'" % infile)
	except IOError:
		print("Cannot resize image '%s'" % infile)


def resize_svg(infile, outfile, new_size):
	tree = ET.parse(infile)

	# get the <svg> tag  
	root = tree.getroot()
	
	# set the width and height attributes to the new values
	root.set('width', str(new_size[0]))
	root.set('height', str(new_size[1]))

	# save the image to a new file
	print("Resized image '%s'" % infile)
	tree.write(outfile)

def get_image_mode(path):

	img = Image.open(path)
	first_frame = img.tile[0][1]

	while True:
		# for each frame verify the updated region
		if img.tile:
			update_region = img.tile[0][1]
			if update_region != first_frame:
				return 'partial'
		try:
			img.seek(img.tell() + 1)
		except EOFError:
			break
	return 'full'

def resize_gif(infile, outfile, new_size):

	all_frames = []
	mode = get_image_mode(infile)

	try:
		frame = Image.open(infile)

		last_frame = frame.resize(new_size, Image.ANTIALIAS)
		last_frame = last_frame.convert('RGBA')

		while frame:
			new_frame = Image.new('RGBA', new_size)

			if mode == 'partial':
				new_frame.paste(last_frame)

			new_frame.paste(frame.resize(new_size, Image.ANTIALIAS))
			new_frame.info = frame.info

			# add the current frame to the list of frames
			all_frames.append(new_frame)
			last_frame = new_frame

			try:
				frame.seek(frame.tell() + 1)
			except EOFError:
				break
		first_frame = all_frames[0]
		first_frame.save(outfile, optimize=True, save_all=True, append_images=all_frames[1:], loop=0)
		print("Resized image '%s'" % infile)
	except IOError:
		print("Cannot resize image '%s'" % path)

def get_resize_method(ext):
	method = resize_jpg

	if ext == ".png":
		method = resize_png
	elif ext == ".svg":
		method = resize_svg
	elif ext == ".gif":
		method = resize_gif
	elif ext == ".jpg" or ".jpeg":
		method = resize_jpg

	return method

def resize_image(image, path, out_path, new_size):

	img_path = os.path.join(path, image)
	filename, ext = get_file_info(image)
	out_path = os.path.join(out_path, 
		filename + "_" + str(new_size[0]) + "x" + str(new_size[1]) + ext)

	resize_method = get_resize_method(ext)
	resize_method(img_path, out_path, new_size)

if __name__ == '__main__':
	parser = ArgumentParser()

	parser.add_argument("--dir", type=str, default="images/",
						help="The images folder")
	parser.add_argument("--out_dir", type=str, default="resizes/",
						help="The resized images folder")
	parser.add_argument("--width", type=int, default=150,
						help="The new width of the image")
	parser.add_argument("--height", type=int, default=150,
						help="The new height of the image")

	args = parser.parse_args()
	dir_path = args.dir
	out_dir = args.out_dir
	size = (args.width, args.height)

	# get all the images in the specified folder
	images = [img for img in listdir(dir_path) if isfile(os.path.join(dir_path, img))]

	if not os.path.exists(out_dir):
		os.makedirs(out_dir)

	# iterate through the images and resize them
	for img in images:
		resize_image(img, dir_path, out_dir, size)