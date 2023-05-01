from public import public

@public
def flag_url(flag_code, size):
    return f"https://www.transformice.com/images/drapeaux/{size}/{flag_code.upper()}.png"

@public
def shaman_object_id_parts(shaman_object_id):
    if shaman_object_id > 9999:
        return divmod(shaman_object_id - 10_000, 10_000)

    if shaman_object_id > 99:
        return divmod(shaman_object_id, 100)

    return shaman_object_id, 0

@public
def shop_item_id_parts(shop_item_id):
    if shop_item_id > 9999:
        return divmod(shop_item_id - 10_000, 10_000)

    if shop_item_id > 99:
        return divmod(shop_item_id, 100)

    return 0, shop_item_id
