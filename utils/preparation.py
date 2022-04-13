import json
from os import mkdir
from shutil import rmtree

import h5py
import matplotlib.pyplot as plt
import numpy as np
from IPython.display import display
from ipywidgets import IntProgress


def get_segmentation(size=1000, segments=5, radius=0.2, seed=1):
    segmentation = np.zeros((size, size), dtype="uint16")
    axis = np.linspace(0, 1, size)
    coords = np.stack(np.meshgrid(axis, axis), axis=-1)
    rng = np.random.default_rng(seed)
    for segment in range(1, 1 + segments):
        center = rng.random(2) * (1 - 2 * radius) + radius
        mask = np.linalg.norm(coords - center, axis=2) < radius
        segmentation[mask] = segment
    return segmentation


def get_chunks(array, chunks=3, _axis=0):
    if array.ndim == _axis + 1:
        yield from np.array_split(array, chunks, axis=_axis)
    else:
        for i in np.array_split(array, chunks, axis=_axis):
            yield from get_chunks(i, chunks=chunks, _axis=_axis + 1)


def get_stats(segmentation, progress=False, repeat=1):
    if isinstance(segmentation, list):
        side_len = int(np.sqrt(len(segmentation)))
        segments = []
        counts = []
        centers = []
        covs = []
        progress_bar = IntProgress(min=0, max=100)
        if progress:
            display(progress_bar)
        for i, segmentation_i in enumerate(segmentation):
            if i % (len(segmentation) / 100) == 0:
                progress_bar.value += 1
            segments_i, counts_i, centers_i, covs_i = get_stats(
                segmentation_i, repeat=repeat
            )
            segments.append(segments_i)
            counts.append(counts_i)
            centers.append(
                (centers_i + np.array([i % side_len, i // side_len])) / side_len
                if len(centers_i) > 0
                else centers_i
            )
            covs.append(covs_i)
        return segments, counts, centers, covs
    axes = [np.linspace(0, 1, dim_len) for dim_len in segmentation.shape]
    coords = np.stack(np.meshgrid(*axes[::-1]), axis=-1)
    segments = []
    count = []
    center_of_mass = []
    covariance_matrix = []
    for segment in range(1, 1 + segmentation.max()):
        mask = segmentation == segment
        if mask.sum() > 1:
            segments.append(segment)
            count.append(mask.sum())
            segment_coords = coords[mask]
            center_of_mass.append(np.mean(segment_coords, axis=0))
            covariance_matrix.append(np.cov(segment_coords.T))
    return (
        np.repeat(np.array(segments), repeat, axis=0),
        np.repeat(np.array(count), repeat, axis=0),
        np.repeat(np.array(center_of_mass), repeat, axis=0),
        np.repeat(np.array(covariance_matrix), repeat, axis=0),
    )


def plot(segmentation, stats=None, _ax=None, _vmax=None):
    if isinstance(segmentation, list):
        side_len = int(np.sqrt(len(segmentation)))
        vmax = max(i.max() for i in segmentation)
        fig, axs = plt.subplots(side_len, side_len, sharex=True, sharey=True)
        fig.subplots_adjust(wspace=-0.6, hspace=0.05)

        def get_stats(i):
            centers = stats[2][i]
            centers = centers * side_len - np.array([i % side_len, i // side_len])
            if len(stats) == 4:
                return stats[0][i], stats[1][i], centers, stats[3][i]
            else:
                return stats[0][i], stats[1][i], centers

        for i, chunk in enumerate(segmentation):
            plot(
                chunk,
                stats and get_stats(i),
                _ax=axs[i // side_len, i % side_len],
                _vmax=vmax,
            )
        plt.show()
    else:
        ax = _ax or plt
        ax.imshow(segmentation, "cubehelix", vmin=0, vmax=_vmax)
        if stats is not None:
            plt.xlim(0, segmentation.shape[0])
            plt.ylim(segmentation.shape[1], 0)
            if len(stats) == 3:
                for _, count, center in zip(*stats):
                    ax.plot(
                        center[0] * len(segmentation),
                        center[1] * len(segmentation),
                        marker="o",
                        markersize=count**0.5 / 20,
                        color="red",
                    )
            else:
                for _, count, center, cov in zip(*stats):
                    eigenvals, eigenvecs = np.linalg.eig(cov)
                    scaled_eigenvecs = eigenvecs * eigenvals[:, None]
                    scaled_eigenvecs *= (
                        count**0.5 / np.linalg.norm(scaled_eigenvecs, axis=0).max()
                    )
                    scaled_center = center * len(segmentation)
                    for e in scaled_eigenvecs:
                        ax.arrow(*scaled_center - e / 2, *e, head_width=0, color="red")
        if _ax is None:
            plt.show()


def save_chunked_stats(chunked_stats, folder, progress=False):
    rmtree(folder, ignore_errors=True)
    mkdir(folder)
    progress_bar = IntProgress(min=0, max=100)
    if progress:
        display(progress_bar)
    for i, (segments, counts, centers, covs) in enumerate(zip(*chunked_stats)):
        if i % (len(chunked_stats[0]) / 100) == 0:
            progress_bar.value += 1
        with open(folder / f"{i}.json", "w") as f:
            json.dump(
                {
                    "segments": segments.tolist(),
                    "counts": counts.tolist(),
                    "centers": centers.tolist(),
                    "covs": covs.tolist(),
                },
                f,
            )
        with h5py.File(folder / f"{i}.hdf5", "w") as f:
            f.create_dataset("segments", data=segments)
            f.create_dataset("counts", data=counts)
            f.create_dataset("centers", data=centers)
            f.create_dataset("covs", data=covs)
