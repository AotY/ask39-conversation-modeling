#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright © 2018 LeonTao
#
# Distributed under terms of the MIT license.
"""
Scale Dot-Product Attention
"""

import torch
import torch.nn as nn
import numpy as np


class ScaleDotProductAttention(nn.Module):
    def __init__(self,
                 temperature,
                 dropout=0.1):
        super().__init__()

        self.temperature = temperature
        self.dropout = nn.Dropout(dropout)
        self.softmax = nn.Softmax(dim=2)

    def forward(self, q, k, v, mask=None):
        """
        Args:
            q: [num_heads * batch_size, q_len, k_size]
            k: [num_heads * batch_size, k_len, k_size]
            v: [num_heads * batch_size, v_len, v_size]

            mask: [num_heads * batch_size, len_q, len_k]
        """
        attn = torch.bmm(q, k.transpose(1, 2))
        attn = attn / self.temperature

        if mask is not None:
            #  attn = attn.masked_fill(mask, -np.inf)
            attn = attn.masked_fill(mask, -float('inf'))

        # [b, q_len, k_len]
        attn = self.softmax(attn)
        attn = self.dropout(attn)

        # [b, q_len, h]
        output = torch.bmm(attn, v)

        return output, attn

