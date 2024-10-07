from celery import shared_task
import matplotlib

matplotlib.use('Agg')

import matplotlib.pyplot as plt


@shared_task
def create_plot():
    plt.figure(figsize=(8, 8))
    plt.savefig('path_to_save_figure.png')
