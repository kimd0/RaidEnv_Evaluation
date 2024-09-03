import argparse
import os
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt


def parse_args():
    parser = argparse.ArgumentParser('postprocess summary')
    parser.add_argument('--result_dir', type=str, required=True)
    parser.add_argument('--max_k', type=int, default=20)

    return parser.parse_args()


def main(args):
    file_path = os.path.join(args.result_dir, os.pardir, f'summary_{os.path.basename(args.result_dir)}.csv')
    df = pd.read_csv(file_path)

    # Standard scaling
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df)
    scaled_df = pd.DataFrame(scaled_data, columns=df.columns)

    # Elbow Method
    wcss = []
    for i in range(1, args.max_k+1):
        kmeans = KMeans(n_clusters=i, random_state=42)
        kmeans.fit(scaled_df)
        wcss.append(kmeans.inertia_)

    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, args.max_k+1), wcss, marker='o')
    plt.title('Elbow Method')
    plt.xlabel('Number of clusters')
    plt.ylabel('WCSS')
    plt.grid(True)
    plt.show()


if __name__ == '__main__':
    args = parse_args()
    main(args)
