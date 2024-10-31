# Copyright (c) 2012 The Regents of The University of Michigan
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Authors: ICS-FORTH, Polydoros Petrakis <ppetrak@ics.forth.gr>
# Authors: ICS-FORTH, Vassilis Papaefstathiou <papaef@ics.forth.gr>
# Based on previous model for ARM Cortex A72 provided by Adria Armejach (BSC)
# and information from the following links regarding Cortex-A76:
# https://en.wikichip.org/wiki/arm_holdings/microarchitectures/cortex-a76
# https://www.anandtech.com/show/12785/\
#    arm-cortex-a76-cpu-unveiled-7nm-powerhouse/2
# https://www.anandtech.com/show/12785/\
#        arm-cortex-a76-cpu-unveiled-7nm-powerhouse/3

import m5

from modules.caches.prefetcher import Stride, Tagged, AMPM

class IOCache(m5.objects.Cache):
    assoc = 8
    tag_latency = 50
    data_latency = 50
    response_latency = 50
    mshrs = 20
    size = '1kB'
    tgts_per_mshr = 12

# The following lines were copied from file devices.py
# provided by BSC (and adjusted by FORTH to match A76)

class L1I(m5.objects.Cache):
    def __init__(self, parameters, **kwargs):
        super(L1I, self).__init__(**kwargs)
        self.tag_latency      = parameters['latency']['tag']
        self.data_latency     = parameters['latency']['data']
        self.response_latency = parameters['latency']['response']
        self.size             = parameters['size']
        self.is_read_only = True
        self.writeback_clean = True
        self.mshrs = 8
        self.tgts_per_mshr = 8
        self.assoc = parameters['assoc']

class L1D(m5.objects.Cache):
    def __init__(self, parameters, **kwargs):
        super(L1D, self).__init__(**kwargs)
        self.tag_latency      = parameters['latency']['tag']
        self.data_latency     = parameters['latency']['data']
        self.response_latency = parameters['latency']['response']
        self.size             = parameters['size']
        self.assoc            = parameters['assoc']
        self.mshrs            = parameters['mshrs']
        self.tgts_per_mshr    = parameters['tgts_per_mshr']
        self.write_buffers    = parameters['write_buffers']
        
class WalkCache(m5.objects.Cache):
    def __init__(self, parameters, **kwargs):
        super(WalkCache, self).__init__(**kwargs)
        self.tag_latency      = parameters['latency']['tag']
        self.data_latency     = parameters['latency']['data']
        self.response_latency = parameters['latency']['response']
        self.size             = parameters['size']
        self.is_read_only = True
        self.writeback_clean = True
        self.mshrs = 6
        self.tgts_per_mshr = 8
        self.assoc = 8
        self.write_buffers = 16


class L2(m5.objects.Cache):
    def __init__(self, parameters, **kwargs):
        super(L2, self).__init__(**kwargs)
        self.tag_latency      = parameters['latency']['tag']
        self.data_latency     = parameters['latency']['data']
        self.response_latency = parameters['latency']['response']
        self.size             = parameters['size']        
        self.mshrs            = parameters['mshrs']
        self.tgts_per_mshr    = parameters['tgts_per_mshr']
        self.write_buffers    = parameters['write_buffers']
        self.assoc            = parameters['assoc']
        self.clusivity        = parameters['clusivity']
        self.prefetch_on_access = parameters['prefetcher']['selected'] != "None"

        if (parameters['prefetcher']['selected'] == "Stride"):
            self.prefetcher = Stride(parameters['prefetcher']['configuration']['Stride'])

        if (parameters['prefetcher']['selected'] == "Tagged"):
            self.prefetcher = Tagged(parameters['prefetcher']['configuration']['Tagged'])

        if (parameters['prefetcher']['selected'] == "AMPM"):
            self.prefetcher = AMPM(parameters['prefetcher']['configuration']['AMPM'])


class L3Slice(m5.objects.Cache):
    def __init__(self, parameters, **kwargs):
        super(L3Slice, self).__init__(**kwargs)
        self.tag_latency      = parameters['latency']['tag']
        self.data_latency     = parameters['latency']['data']
        self.response_latency = parameters['latency']['response']
        self.size             = parameters['size']
        self.assoc            = parameters['assoc']
        self.mshrs            = parameters['mshrs']
        self.tgts_per_mshr    = parameters['tgts_per_mshr']
        self.write_buffers    = parameters['write_buffers']
        self.clusivity        = parameters['clusivity']