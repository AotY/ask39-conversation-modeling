#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright © 2018 LeonTao
#
# Distributed under terms of the MIT license.

"""
Utils for transformer model.
"""
import torch
import torch.nn as nn
import numpy as np


def get_non_pad_mask(input, padid):
    """
    input: [b, l] ?
    """
    assert input.dim() == 2
    return input.ne(padid).type(torch.float).unsqueeze(-1) # [max_len, batch_size, 1]

def get_sinusoid_encoding_table(n_position, embedding_size, padid=None):
    """Sinusoid position encoding table."""

    def cal_angle(position, hid_idx):
        return position / np.power(10000, 2 * (hid_idx // 2) / embedding_size)

    def get_posi_angle_vec(position):
        return [cal_angle(position, hid_idx) for hid_idx in range(embedding_size)]

    sinusoid_table = np.array([get_posi_angle_vec(position) for position in range(n_position)])

    sinusoid_table[:, 0::2] = np.sin(sinusoid_table[:, 0::2]) # dim 2i
    sinusoid_table[:, 1::2] = np.cos(sinusoid_table[:, 1::2]) # dim 2i + 1

    if padid is not None:
        # zero vector for padding dimension
        sinusoid_table[padid] = 0.

    return torch.tensor(sinusoid_table, dtype=torch.float)

def get_relative_encoding_table(n_position, embedding_size=512, max_relative_pos=10):
    """
    From tensor2tensor: https://github.com/tensorflow/tensor2tensor
    return: [n_position, n_position, embedding_size]
    """
    range_vec = torch.arange(n_position)
    range_mat = range_vec.repeat(n_position).view(n_position, n_position)
    distance_mat = range_mat - range_mat.transpose(0, 1)
    distance_mat_clipped = torch.clamp(distance_mat, -max_relative_pos, max_relative_pos)
    final_mat = distance_mat_clipped + max_relative_pos

    pos_size = max_relative_pos * 2 + 1
    embedding_table = torch.rand(pos_size, embedding_size)
    embedding = embedding_table.index_select(0, final_mat.view(-1)).view(n_position, n_position, embedding_size)

    return embedding

def get_attn_key_pad_mask(k, q, padid):
    '''
        For masking out the padding part of key sequence.
        k: [batch_size, max_len]
        q: [batch_size, max_len]
    '''
    # Expand to fit the shape of key query attention matrix.
    len_q = q.size(1)
    padding_mask = k.eq(padid)
    padding_mask = padding_mask.unsqueeze(1).expand(-1, len_q, -1)  # b x lq x lk

    return padding_mask

def get_subsequent_mask(input):
    ''' For masking out the subsequent info. '''

    sz_b, len_s = input.size()
    # Returns the upper triangular part of the matri
    subsequent_mask = torch.triu(
        torch.ones((len_s, len_s), device=input.device, dtype=torch.uint8), diagonal=1)
    subsequent_mask = subsequent_mask.unsqueeze(0).expand(sz_b, -1, -1)  # b x ls x ls

    return subsequent_mask

