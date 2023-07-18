import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap
from matplotlib.ticker import FuncFormatter

def gantt(num_jobs, outputpath='./JobShop/output', mode='SPT'):
    cmap = get_cmap('viridis')
    color_list = [cmap(i / num_jobs) for i in range(num_jobs)]
    filename = outputpath + '/eventlog.csv'
    df = pd.read_csv(filename)
    df.sort_values(by=['Machine', 'Time'], inplace=True)
    df.dropna(inplace=True)
    colors = {f'Job {i}': color_list[i] for i in range(num_jobs)}
    fig, ax = plt.subplots(figsize=(10, 7))
    y_values = range(df['Machine'].nunique())
    makespan = -1
    for idx, machine in enumerate(df['Machine'].unique()):
        machine_df = df[df['Machine'] == machine]
        for i in range(num_jobs):
            job_name = f'Job {i}'
            times = machine_df[machine_df['Job'] == job_name]['Time'].values
            color = colors.get(job_name)
            ax.barh(idx, width=times[1]-times[0], left=times[0], color=color, label=job_name)
            if times[1] > makespan:
                makespan = times[1]
    ax.set_xlabel('Time')
    ax.set_yticks(y_values)
    ax.set_yticklabels(df['Machine'].unique())
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: 'Machine {:0.0f}'.format(x)))
    ax.set_ylabel('Machine')
    ax.set_title(f'Job Shop Gantt Chart ({mode})')
    ax.grid(axis='x')
    print('makespan:', makespan)

    
    plt.axvline(x=makespan, color='b', linestyle='--')
    plt.text(makespan, 1, f'Makespan = {makespan}', color='b', ha='center', va='bottom', transform=plt.gca().get_xaxis_transform())
    # plt.text(makespan, -0.018, f'{makespan}', color='b', ha='center', va='top', transform=plt.gca().get_xaxis_transform())

    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(), loc='lower right')
    plt.savefig(outputpath + '/Gantt_Chart.png')
    plt.show()
