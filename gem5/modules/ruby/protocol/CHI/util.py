import math

# Generates SLC select bit masks as described
# in the Arm CMN-600 Technical Reference Manual
def slc_mask(nhnfs=16, cache_line_size = 64, maxb=52):
    bs_bits = int(math.log(cache_line_size, 2))
    intlvBits = int(math.log2(nhnfs))
    mask_list = []
    for b in range(intlvBits):
        masks = [(1 << i) for i in range(b+bs_bits,maxb,intlvBits)]
        m = 0
        for mask in masks:
            m = m | mask
        mask_list.append(m)
    return mask_list
