import argparse
import os

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans


def parse_args():
    parser = argparse.ArgumentParser('postprocess summary')
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--result_dir', type=str, required=True)
    parser.add_argument('--method', type=str, required=True, choices=['nearest', 'uniform'])
    parser.add_argument('--k', type=int, default=7)
    parser.add_argument('--n', type=int, default=1, help='Number of presidents to select')

    return parser.parse_args()


def main(args):
    file_path = os.path.join(args.result_dir, os.pardir, f'summary_{os.path.basename(args.result_dir)}.csv')
    df = pd.read_csv(file_path)

    # Standard scaling
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df)
    scaled_df = pd.DataFrame(scaled_data, columns=df.columns)

    # K-Means clustering
    kmeans = KMeans(n_clusters=args.k, random_state=42)
    clusters = kmeans.fit_predict(scaled_df)
    centers = kmeans.cluster_centers_

    # Find N-Nearest neighbors
    presidents = []
    for i in range(args.k):
        samples_in_cluster = scaled_df[clusters == i].to_numpy()
        if args.method == 'uniform':
            nearest_indices = np.random.choice(samples_in_cluster.shape[0], args.n, replace=False)
            nearest = np.array([np.where(clusters == i)[0][j] for j in nearest_indices])
        elif args.method == 'nearest':
            distance = np.linalg.norm(samples_in_cluster - centers[i], axis=1)
            nearest = np.argsort(distance)[:args.n]
        else:
            raise ValueError(f"Invalid method: {args.method}")
        presidents.append(nearest)

    # Print presidents
    for i, cluster in enumerate(presidents):
        print()
        print("=" * 100)
        print(f'Cluster {i}')
        print("=" * 100)

        # Print column names
        print("filename", end=" "*12)
        for column in _columns:
            print(f"{column:10}", end=" ")

        for j in cluster:
            print(f'\nconfig_{j:05d}.json', end=" ")
            for column in _columns:
                print(f"{df.iloc[j][column]:10}", end=" ")


_columns = ['healthMax', 'armor', 'moveSpeed', 'cooltime', 'range', 'casttime', 'damage', 'win_rate']


if __name__ == '__main__':
    args = parse_args()
    np.random.seed(args.seed)
    main(args)
