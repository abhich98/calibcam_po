# Functions in this file will be subject to autograd and need to be written accordingly
# - Do not import functions that are not compatible with autograd
# - Autograd numpy used here

import autograd.numpy as np
from .optimization_autograd import rodrigues2rotMats

def map_m(rX1_0, rX1_1, rX1_2,
          tX1_0, tX1_1, tX1_2,
          r1_0, r1_1, r1_2,
          t1_0, t1_1, t1_2,
          M,
          nRes):
    # rX1
    rX1 = np.concatenate([rX1_0.reshape(nRes, 1),
                          rX1_1.reshape(nRes, 1),
                          rX1_2.reshape(nRes, 1)], 1)
    # tX1
    tX1 = np.concatenate([tX1_0.reshape(nRes, 1),
                          tX1_1.reshape(nRes, 1),
                          tX1_2.reshape(nRes, 1)], 1)
    # r1
    r1 = np.concatenate([r1_0.reshape(nRes, 1),
                         r1_1.reshape(nRes, 1),
                         r1_2.reshape(nRes, 1)], 1)
    # t1
    t1 = np.concatenate([t1_0.reshape(nRes, 1),
                         t1_1.reshape(nRes, 1),
                         t1_2.reshape(nRes, 1)], 1)

    RX1 = rodrigues2rotMats(rX1)
    R1 = rodrigues2rotMats(r1)

    # R1 * M + t1
    m_proj_0_1 = R1[:, 0, 0] * M[:, 0] + \
                 R1[:, 0, 1] * M[:, 1] + \
                 t1[:, 0]
    m_proj_1_1 = R1[:, 1, 0] * M[:, 0] + \
                 R1[:, 1, 1] * M[:, 1] + \
                 t1[:, 1]
    m_proj_2_1 = R1[:, 2, 0] * M[:, 0] + \
                 R1[:, 2, 1] * M[:, 1] + \
                 t1[:, 2]
    # RX1 * m_proj + tX1
    m_proj_0_2 = RX1[:, 0, 0] * m_proj_0_1 + \
                 RX1[:, 0, 1] * m_proj_1_1 + \
                 RX1[:, 0, 2] * m_proj_2_1 + \
                 tX1[:, 0]
    m_proj_1_2 = RX1[:, 1, 0] * m_proj_0_1 + \
                 RX1[:, 1, 1] * m_proj_1_1 + \
                 RX1[:, 1, 2] * m_proj_2_1 + \
                 tX1[:, 1]
    m_proj_2_2 = RX1[:, 2, 0] * m_proj_0_1 + \
                 RX1[:, 2, 1] * m_proj_1_1 + \
                 RX1[:, 2, 2] * m_proj_2_1 + \
                 tX1[:, 2]
    # m_proj / m_proj[2]
    x_pre = m_proj_0_2 / m_proj_2_2
    y_pre = m_proj_1_2 / m_proj_2_2
    # distort
    r2 = x_pre ** 2 + y_pre ** 2

    return x_pre, y_pre, r2


def calc_res_x(rX1_0, rX1_1, rX1_2,
               tX1_0, tX1_1, tX1_2,
               k_1, k_2, p_1, p_2, k_3,
               fx, cx, fy, cy,
               r1_0, r1_1, r1_2,
               t1_0, t1_1, t1_2,
               M, m, delta,
               nRes):
    x_pre, y_pre, r2 = map_m(rX1_0, rX1_1, rX1_2,
                             tX1_0, tX1_1, tX1_2,
                             r1_0, r1_1, r1_2,
                             t1_0, t1_1, t1_2,
                             M,
                             nRes)
    # distort
    x = x_pre * (1 + k_1 * r2 + k_2 * r2 ** 2 + k_3 * r2 ** 3) + \
        2 * p_1 * x_pre * y_pre + \
        p_2 * (r2 + 2 * x_pre ** 2)
    # A * m_proj
    x_post = x * fx + cx

    res_x = delta * (x_post - m[:, 0])

    return res_x


def calc_res_y(rX1_0, rX1_1, rX1_2,
               tX1_0, tX1_1, tX1_2,
               k_1, k_2, p_1, p_2, k_3,
               fx, cx, fy, cy,
               r1_0, r1_1, r1_2,
               t1_0, t1_1, t1_2,
               M, m, delta,
               nRes):
    x_pre, y_pre, r2 = map_m(rX1_0, rX1_1, rX1_2,
                             tX1_0, tX1_1, tX1_2,
                             r1_0, r1_1, r1_2,
                             t1_0, t1_1, t1_2,
                             M,
                             nRes)
    # distort
    y = y_pre * (1 + k_1 * r2 + k_2 * r2 ** 2 + k_3 * r2 ** 3) + \
        p_1 * (r2 + 2 * y_pre ** 2) + \
        2 * p_2 * x_pre * y_pre
    # A * m_proj
    y_post = y * fy + cy

    res_y = delta * (y_post - m[:, 1])

    return res_y


