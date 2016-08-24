#!/usr/bin/env python
import os
import sys
import unitypack
from argparse import ArgumentParser
from unitypack.environment import UnityEnvironment
from card_tile import generate_tile_image


def handle_asset(asset, textures, cards):
	for obj in asset.objects.values():
		if obj.type == "AssetBundle":
			d = obj.read()
			for path, obj in d["m_Container"]:
				path = path.lower()
				asset = obj["asset"]
				if not path.startswith("final/"):
					path = "final/" + path
				if not path.startswith("final/assets"):
					continue
				textures[path] = asset

		elif obj.type == "GameObject":
			d = obj.read()
			cardid = d.name
			if cardid in ("CardDefTemplate", "HiddenCard"):
				# not a real card
				cards[cardid] = {"path": "", "tile": ""}
				continue
			if len(d.component) != 2:
				# Not a CardDef
				continue
			carddef = d.component[1][1].resolve()
			if not isinstance(carddef, dict) or "m_PortraitTexturePath" not in carddef:
				# Not a CardDef
				continue
			path = carddef["m_PortraitTexturePath"]
			if path:
				path = "final/" + path

			tile = carddef.get("m_DeckCardBarPortrait")
			if tile:
				tile = tile.resolve()
			cards[cardid] = {
				"path": path.lower(),
				"tile": tile.saved_properties if tile else {},
			}


def extract_info(files):
	cards = {}
	textures = {}
	env = UnityEnvironment()

	for file in files:
		print("Reading %r" % (file))
		with open(file, "rb") as f:
			bundle = unitypack.load(f, env)

		for asset in bundle.assets:
			print("Parsing %r" % (asset.name))
			handle_asset(asset, textures, cards)

	return cards, textures


def save_image(image, name, prefix, args):
	dirname = os.path.join(args.outdir, prefix)
	if not os.path.exists(dirname):
		os.makedirs(dirname)
	path = os.path.join(dirname, name + ".png")
	if args.skip_existing and os.path.exists(path):
		return

	print("%r -> %r" % (name, path))
	image.save(path)


def process_tile_texture(texture, tile):
	return generate_tile_image(texture.image, tile)


def main():
	p = ArgumentParser()
	p.add_argument("--outdir", nargs="?", default="")
	p.add_argument("--skip-existing", action="store_true")
	p.add_argument("files", nargs="+")
	args = p.parse_args(sys.argv[1:])

	cards, textures = extract_info(args.files)
	paths = [card["path"] for card in cards.values()]
	print("Found %i cards, %i textures including %i unique in use." % (
		len(cards), len(textures), len(set(paths))
	))

	by_id_dir = "by-id"
	tiles_dir = "tiles"

	for id, values in cards.items():
		path = values["path"]
		if not path:
			print("%r does not have a texture" % (id))
			continue

		if path not in textures:
			print("Path %r not found for %r" % (path, id))
			continue

		pptr = textures[path]
		texture = pptr.resolve()

		save_image(texture.image, id, by_id_dir, args)

		if values["tile"]:
			tile_texture = process_tile_texture(texture, values["tile"])
			save_image(tile_texture, id, tiles_dir, args)


if __name__ == "__main__":
	main()
