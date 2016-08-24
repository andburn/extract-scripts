tex_coords = [(0.0, 0.3856), (1.0, 0.6144)]
out_dim = 256
out_width = round(tex_coords[1][0] * out_dim - tex_coords[0][0] * out_dim)
out_height = round(tex_coords[1][1] * out_dim - tex_coords[0][1] * out_dim)


def get_rect(ux, uy, usx, usy, sx, sy, ss, tex_dim = 512):
	# calc the coords
	tl_x = ((tex_coords[0][0] + sx) * ss) * usx + ux
	tl_y = ((tex_coords[0][1] + sy) * ss) * usy + uy
	br_x = ((tex_coords[1][0] + sx) * ss) * usx + ux
	br_y = ((tex_coords[1][1] + sy) * ss) * usy + uy

	# adjust if x coords cross-over
	horiz_delta = tl_x - br_x
	if horiz_delta > 0:
		tl_x -= horiz_delta
		br_x += horiz_delta

	# get the bar rectangle at tex_dim size
	x = round(tl_x * tex_dim)
	y = round(tl_y * tex_dim)
	width = round(abs((br_x - tl_x) * tex_dim))
	height = round(abs((br_y - tl_y) * tex_dim))

	# adjust x and y, so that texture is "visible"
	x = (x + width) % tex_dim - width
	y = (y + height) % tex_dim - height

	# ??? to cater for some special cases
	min_visible = tex_dim / 4
	while x + width < min_visible:
		x += tex_dim
	while y + height < 0:
		y += tex_dim

	# ensure wrap around is used
	if x < 0:
		x += tex_dim

	return (x, y, width, height)


def generate_tile_image(img, tile):
	from PIL import Image, ImageOps
	# tile the image horizontally (x2 is enough),
	# some cards need to wrap around to create a bar (e.g. Muster for Battle),
	# also discard alpha channel (e.g. Soulfire, Mortal Coil)
	tiled = Image.new("RGB", (img.width * 2, img.height))
	tiled.paste(img, (0, 0))
	tiled.paste(img, (img.width, 0))

	x, y, width, height = get_rect(
		tile["m_TexEnvs"]["_MainTex"]["m_Offset"]["x"],
		tile["m_TexEnvs"]["_MainTex"]["m_Offset"]["y"],
		tile["m_TexEnvs"]["_MainTex"]["m_Scale"]["x"],
		tile["m_TexEnvs"]["_MainTex"]["m_Scale"]["y"],
		tile["m_Floats"]["_OffsetX"],
		tile["m_Floats"]["_OffsetY"],
		tile["m_Floats"]["_Scale"],
		img.width
	)

	bar = tiled.crop((x, y, x + width, y + height))
	bar = ImageOps.flip(bar)
	# negative x scale means horizontal flip
	if tile["m_TexEnvs"]["_MainTex"]["m_Scale"]["x"] < 0:
		bar = ImageOps.mirror(bar)

	return bar.resize((out_width, out_height), Image.LANCZOS)
