#! /usr/bin/env python
# -*- Mode: Python; py-indent-offset: 4 -*-
# 
# Copyright (C) 2014 Charles Twardy
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA

"""
map_lognorm.py
--------------

Copied from plot_lognorm.py to try generating 2D probability maps.

"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as img
from scipy.stats import lognorm

data = []
with open('lognorm_params.csv') as f:
    for row in f:
        data.append(row.strip()[:-3].split(','))

for line in data[1:]:
    categ, mu, sigma = line
    if 'else' in categ.lower():
        continue
    scale, shape = np.exp(float(mu)), float(sigma)
    lnorm = lognorm([shape],scale=scale)
    qtiles = [lnorm.ppf(q) for q in [.25,.50,.75]]
    x=y=np.linspace(-5,5,480)
    xx,yy=np.meshgrid(x,y)
    z=lnorm.pdf(np.sqrt(xx**2 + yy**2))
    plt.title(categ)
    plt.imshow(z,cmap='gist_gray')
    plt.colorbar()
    plt.imsave('lognorm_heat_pngs/%s.png' % categ, z, cmap='gist_heat')

#fig.set_size_inches(8,6)
#fig.suptitle("Lognormal Probability Density by Category (km)", fontsize=20)

