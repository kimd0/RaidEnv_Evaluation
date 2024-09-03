import argparse
import os
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
import seaborn as sns
import matplotlib.pyplot as plt


def parse_args():
    parser = argparse.ArgumentParser('postprocess summary')
    parser.add_argument('--result_dir', type=str, required=True)
    parser.add_argument('--epi_num', type=int, default=100)

    return parser.parse_args()


def main(args):
    file_path = os.path.join(args.result_dir, os.pardir, f'summary_{os.path.basename(args.result_dir)}.csv')
    df = pd.read_csv(file_path)

    # Check integrity
    assert all(df['count'] == args.epi_num), \
        "Episode count mismatch at {} rows".format(df[~df['count'] == args.epi_num].index)
    df.drop(columns=['count'], inplace=True)

    # Standard scaling
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df)
    scaled_df = pd.DataFrame(scaled_data, columns=df.columns)

    # K-Means clustering - all
    clusters = KMeans(n_clusters=7, random_state=42).fit_predict(scaled_df)
    df['cluster'] = clusters

    # t-SNE - parameter
    columns_parameter = ['armor', 'casttime', 'cooltime', 'damage', 'healthMax', 'moveSpeed', 'range']
    tsne_parameter = TSNE(n_components=2, random_state=42).fit_transform(scaled_df[columns_parameter])

    # Visualization1 - result
    plt.figure(figsize=(8, 6))
    for cluster, color in enumerate(['red', 'green', 'blue', 'orange', 'purple', 'brown', 'pink']):
        plt.scatter(
            tsne_parameter[clusters == cluster, 0],
            tsne_parameter[clusters == cluster, 1],
            color=color,
            edgecolor='k',
            alpha=0.7,
            label=f'Cluster {cluster}'
        )
        plt.xlim(-70, 70)
        plt.ylim(-70, 70)
        plt.title('t-SNE with KMeans Clustering')
        plt.xlabel('t-SNE 1')
        plt.ylabel('t-SNE 2')
        plt.legend()
        plt.grid(True)
        plt.show()

    plt.figure(figsize=(8, 6))
    for cluster, color in enumerate(['red', 'green', 'blue', 'orange', 'purple', 'brown', 'pink']):
        plt.scatter(
            tsne_parameter[clusters == cluster, 0],
            tsne_parameter[clusters == cluster, 1],
            color=color,
            edgecolor='k',
            alpha=0.7,
            label=f'Cluster {cluster}'
        )
    plt.xlim(-70, 70)
    plt.ylim(-70, 70)
    plt.title('t-SNE with KMeans Clustering')
    plt.xlabel('t-SNE 1')
    plt.ylabel('t-SNE 2')
    plt.legend()
    plt.grid(True)
    plt.show()

    # Visualization2 - parameter
    plt.figure(figsize=(15, len(columns_parameter) * 5))
    for i, col in enumerate(columns_parameter, 1):
        plt.subplot(len(columns_parameter), 1, i)
        sns.boxplot(x='cluster', y=col, data=df)
        plt.title(f'Distribution of {col} by Cluster')
        plt.xlabel('Cluster')
        plt.ylabel(col)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    args = parse_args()
    main(args)
