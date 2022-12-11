
# -*- coding: utf-8 -*-
import numpy as np
from fun.dist import get_distance_hav
import Settings


def get_lcs_matrix(s1, s2):
    dp = np.zeros((len(s1[0]) + 1, len(s2[0]) + 1))
    for i in range(1, len(s1[0]) + 1):
        for j in range(1, len(s2[0]) + 1):
            lon1, lat1, lon2, lat2 = s1[0][i-1], s1[1][i-1], s2[0][j - 1], s2[1][j - 1]
            if get_distance_hav(lon1, lat1, lon2, lat2) <= Settings.dist_error:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp


def get_lcs_seq(i, j, dp, s1, s2, index1, index2, res):
    while i > 0 and j > 0:
        lon1, lat1, lon2, lat2 = s1[0][i - 1], s1[1][i - 1], s2[0][j - 1], s2[1][j - 1]
        if get_distance_hav(lon1, lat1, lon2, lat2) <= Settings.dist_error:
            index1 += str(i-1)
            index2 += str(j-1)
            i -= 1
            j -= 1
        else:
            if dp[i - 1][j] > dp[i][j - 1]:
                i -= 1
            elif dp[i - 1][j] < dp[i][j - 1]:
                j -= 1
            else:
                get_lcs_seq(i - 1, j, dp, s1, s2, index1, index2, res)
                get_lcs_seq(i, j - 1, dp, s1, s2, index1, index2, res)
                return res
    return [index1[::-1], index2[::-1]]


if __name__ == '__main__':
    arr = np.load("../0.npy", allow_pickle=True)
    s1 = arr[10][3]
    s2 = arr[21][3]
    index1 = ''
    index2 = ''
    dp = get_lcs_matrix(s1, s2)
    res = []
    res = get_lcs_seq(len(s1[0]), len(s2[0]), dp, s1, s2, index1, index2, res)
    print(res)


